"""
ari_brain.py — Orquestador de modelos de ARI.

Un solo archivo, usado por las dos variantes (ARI.py web y ari_module.py
embebido). Toda la lógica de modelos vive aquí; las apps solo llaman a
`responder()`.

DISEÑO
──────
1. ORDEN ESTRICTO. Gemini es el cerebro. Se intenta SIEMPRE, en cada
   pregunta, sin excepción. NVIDIA solo se toca cuando Gemini devolvió una
   excepción en esa misma llamada. No hay estado de "cooldown" ni memoria
   de fallos previos: el estado invisible fue lo que antes hacía que la
   conversación se quedara pegada en el respaldo.

2. UN SOLO HISTORIAL. La conversación vive en una lista de mensajes de
   LangChain. Los dos proveedores leen exactamente la misma lista, así que
   no importa quién contestó el turno anterior: no hay desincronización.

3. SDK VIGENTE. `google.generativeai` está descontinuado por Google.
   `langchain-google-genai` usa `google-genai` por debajo, que es el
   soportado.

4. ITERACIÓN EXPLÍCITA, NO `with_fallbacks`. LangChain trae
   `Runnable.with_fallbacks()`, pero no reporta cuál proveedor respondió ni
   por qué fallaron los anteriores. Este sistema necesita ese diagnóstico,
   así que el recorrido se hace a mano sobre los mismos objetos Chat de
   LangChain. Se gana trazabilidad sin perder la abstracción.

DEPENDENCIAS (requirements.txt)
    langchain-core
    langchain-google-genai
    langchain-nvidia-ai-endpoints
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
import re

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage


# ══════════════════════════════════════════════════════════════════
# Configuración
# ══════════════════════════════════════════════════════════════════

MODELO_GEMINI = "gemini-2.5-flash"

# Respaldos NVIDIA en orden. Los modelos con modo de razonamiento van al
# final: gastan su presupuesto de tokens en el monólogo interno y a veces
# lo devuelven como respuesta.
MODELOS_NVIDIA = [
    "mistralai/mistral-nemotron",
    "nvidia/llama-3.1-nemotron-51b-instruct",
    "meta/llama-3.2-90b-vision-instruct",
]

MODELOS_NVIDIA_VISION = [
    "meta/llama-3.2-90b-vision-instruct",
    "meta/llama-3.2-11b-vision-instruct",
]

# Familias que exigen "detailed thinking off" como system message propio.
_RAZONADORES = ("nemotron-3", "super", "ultra", "nano", "reasoning", "deepseek-v4")

MAX_TOKENS_RESPUESTA = 1024
MAX_TURNOS_CONTEXTO = 12          # 6 preguntas + 6 respuestas
TIMEOUT_SEG = 30                  # por proveedor; corto para no dejar la UI colgada

MSG_SIN_SERVICIO = (
    "⏳ **Estoy recibiendo muchas consultas en este momento.**\n\n"
    "Espera un minuto y vuelve a preguntarme, por favor.\n\n"
    "Si tu trámite es urgente, acude al área de RH de la DFC o consulta el "
    "portal: https://martin-carrizalez.github.io/portal-RH-DFC/"
)

INSTRUCCION_IMAGEN = (
    "Analiza esta imagen de una incapacidad médica y verifica los 3 requisitos "
    "obligatorios: 1) sello oficial con logotipo del IMSS o ISSSTE, 2) firma y "
    "sello del médico tratante, 3) firma y sello del Jefe de Consulta. Marca cada "
    "uno con ✅ o ❌, di qué debe hacer si falta alguno y revisa que no exceda 28 "
    "días (salvo maternidad). Si no es legible o no parece una incapacidad, dilo. "
    "Responde en español."
)


# ══════════════════════════════════════════════════════════════════
# Resultado
# ══════════════════════════════════════════════════════════════════

@dataclass
class Resultado:
    """Lo que devuelve `responder()`."""
    texto: str
    proveedor: str                       # "gemini" | "nvidia" | "ninguno"
    modelo: str = ""
    errores: list[tuple[str, str]] = field(default_factory=list)  # (modelo, error)

    @property
    def ok(self) -> bool:
        return self.proveedor != "ninguno"

    @property
    def es_respaldo(self) -> bool:
        return self.proveedor == "nvidia"


# ══════════════════════════════════════════════════════════════════
# Construcción de clientes
# ══════════════════════════════════════════════════════════════════

def _cliente_gemini(api_key: str):
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model=MODELO_GEMINI,
        google_api_key=api_key,
        temperature=0.3,
        max_output_tokens=MAX_TOKENS_RESPUESTA,
        timeout=TIMEOUT_SEG,
        # Sin reintentos internos: si Gemini está saturado queremos pasar al
        # respaldo de inmediato, no esperar su backoff exponencial. Ese era el
        # motivo de que la interfaz se quedara "pensando" varios minutos.
        max_retries=0,
    )


def _cliente_nvidia(api_key: str, modelo: str):
    from langchain_nvidia_ai_endpoints import ChatNVIDIA
    return ChatNVIDIA(
        model=modelo,
        api_key=api_key,
        temperature=0.3,
        max_completion_tokens=MAX_TOKENS_RESPUESTA,
        top_p=0.9,
    )


# ══════════════════════════════════════════════════════════════════
# Armado de mensajes
# ══════════════════════════════════════════════════════════════════

def _mensaje_usuario(pregunta: str, imagen_data_url: Optional[str]) -> HumanMessage:
    """Un solo formato de mensaje sirve para Gemini y para NVIDIA: bloques
    de contenido con `image_url`, que es el estándar OpenAI que ambos
    proveedores aceptan."""
    if not imagen_data_url:
        return HumanMessage(content=str(pregunta))
    return HumanMessage(content=[
        {"type": "text", "text": str(pregunta)},
        {"type": "image_url", "image_url": {"url": imagen_data_url}},
    ])


def _construir_mensajes(system_prompt: str, historial: list[BaseMessage],
                        pregunta: str, imagen_data_url: Optional[str],
                        modelo: str) -> list[BaseMessage]:
    mensajes: list[BaseMessage] = []
    if any(k in modelo.lower() for k in _RAZONADORES):
        # NVIDIA exige esta línea como system message independiente; pegada
        # al prompt principal el modelo la ignora.
        mensajes.append(SystemMessage(content="detailed thinking off"))
    mensajes.append(SystemMessage(content=system_prompt))
    mensajes.extend(historial[-MAX_TURNOS_CONTEXTO:])
    mensajes.append(_mensaje_usuario(pregunta, imagen_data_url))
    return mensajes


# ══════════════════════════════════════════════════════════════════
# Validación de la salida
# ══════════════════════════════════════════════════════════════════

_MARCAS_RAZONAMIENTO = (
    "here's a thinking process", "here is a thinking process",
    "thinking process:", "let me analyze", "analyze user input",
    "identify intent", "check constraints", "formulate response",
    "draft response", "internal monologue", "the user is asking",
    "okay, the user", "proceso de pensamiento", "razonamiento interno",
)


class SalidaInvalida(Exception):
    """La respuesta llegó, pero no es presentable al usuario."""


def _limpiar(texto: str) -> str:
    texto = re.sub(r"<think>.*?</think>", "", texto, flags=re.DOTALL | re.IGNORECASE)
    texto = re.sub(r"^\s*</?think>\s*", "", texto, flags=re.IGNORECASE)
    return texto.strip()


def _validar(texto: str) -> str:
    """Devuelve el texto listo para mostrar o lanza SalidaInvalida.
    Lanzar hace que el orquestador pase al siguiente modelo, igual que si
    la API hubiera fallado."""
    texto = _limpiar(texto or "")
    if not texto:
        raise SalidaInvalida("respuesta vacía")

    cabeza = texto[:400].lower()
    if any(m in cabeza for m in _MARCAS_RAZONAMIENTO):
        raise SalidaInvalida("el modelo devolvió su cadena de razonamiento")

    # ARI siempre contesta en español; un bloque en inglés es fuga de CoT.
    marcadores_en = ("the user", "i should", "i'll ", "response:", "prompt.")
    if sum(1 for m in marcadores_en if m in cabeza) >= 2:
        raise SalidaInvalida("el modelo respondió en inglés (razonamiento filtrado)")

    return texto


def _texto_de(respuesta: Any) -> str:
    contenido = getattr(respuesta, "content", respuesta)
    if isinstance(contenido, list):  # algunos proveedores devuelven bloques
        contenido = "".join(
            b.get("text", "") for b in contenido if isinstance(b, dict)
        )
    return str(contenido or "")


# ══════════════════════════════════════════════════════════════════
# Orquestador
# ══════════════════════════════════════════════════════════════════

def _invocar(cliente, mensajes) -> str:
    return _validar(_texto_de(cliente.invoke(mensajes)))


def responder(
    pregunta: str,
    system_prompt: str,
    historial: list[BaseMessage],
    gemini_api_key: str,
    nvidia_api_key: str = "",
    imagen_data_url: Optional[str] = None,
) -> Resultado:
    """Responde una pregunta. Nunca lanza excepción.

    Orden garantizado por construcción:
      1. Gemini, siempre, en cada llamada.
      2. Solo si Gemini falló: los modelos de NVIDIA, en orden.
      3. Si todo falló: mensaje de espera, sin códigos de error.
    """
    errores: list[tuple[str, str]] = []

    # ── 1. GEMINI (cerebro principal, sin condiciones) ────────────
    if gemini_api_key:
        try:
            mensajes = _construir_mensajes(system_prompt, historial, pregunta,
                                           imagen_data_url, MODELO_GEMINI)
            return Resultado(_invocar(_cliente_gemini(gemini_api_key), mensajes),
                             "gemini", MODELO_GEMINI, errores)
        except Exception as e:
            errores.append((MODELO_GEMINI, f"{type(e).__name__}: {e}"[:300]))
    else:
        errores.append((MODELO_GEMINI, "GEMINI_API_KEY no configurada"))

    # ── 2. NVIDIA (solo porque Gemini falló arriba) ───────────────
    if not nvidia_api_key:
        errores.append(("nvidia", "NVIDIA_API_KEY no configurada"))
        return Resultado(MSG_SIN_SERVICIO, "ninguno", "", errores)

    lista = MODELOS_NVIDIA_VISION if imagen_data_url else MODELOS_NVIDIA
    for modelo in lista:
        try:
            mensajes = _construir_mensajes(system_prompt, historial, pregunta,
                                           imagen_data_url, modelo)
            return Resultado(_invocar(_cliente_nvidia(nvidia_api_key, modelo), mensajes),
                             "nvidia", modelo, errores)
        except Exception as e:
            errores.append((modelo, f"{type(e).__name__}: {e}"[:300]))

    # ── 3. Nada respondió ─────────────────────────────────────────
    return Resultado(MSG_SIN_SERVICIO, "ninguno", "", errores)


# ══════════════════════════════════════════════════════════════════
# Utilidades para las apps
# ══════════════════════════════════════════════════════════════════

def imagen_a_data_url(imagen, max_lado: int = 1024, calidad: int = 70) -> str:
    """PIL.Image → data URL base64. Los VLM de NVIDIA rechazan payloads
    grandes, así que la imagen se reduce hasta caber bajo ~180 KB."""
    import base64
    import io

    for lado, q in ((max_lado, calidad), (760, 55), (600, 45)):
        img = imagen.convert("RGB")
        if max(img.size) > lado:
            r = lado / max(img.size)
            img = img.resize((int(img.size[0] * r), int(img.size[1] * r)))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=q)
        b64 = base64.b64encode(buf.getvalue()).decode()
        if len(b64) <= 180_000:
            return f"data:image/jpeg;base64,{b64}"
    raise ValueError("La imagen es demasiado grande incluso comprimida")


def registrar_turno(historial: list[BaseMessage], pregunta: str, respuesta: str) -> None:
    """Guarda el turno en el historial compartido. Se llama SIEMPRE, sin
    importar qué proveedor contestó: ese es el punto del historial único."""
    historial.append(HumanMessage(content=str(pregunta)))
    historial.append(AIMessage(content=str(respuesta)))
