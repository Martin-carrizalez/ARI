import streamlit as st
import google.generativeai as genai
from datetime import date
from PIL import Image
import pytz
from datetime import datetime

def today_mx():
    return datetime.now(pytz.timezone('America/Mexico_City')).date()

# ── Configuración ──────────────────────────────────────────────
st.set_page_config(
    page_title="ARI – Asistente RH DFC",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# ── Calendario de quincenas 2026 ───────────────────────────────
QUINCENAS = [
    {"q":"Q-01","fecha":date(2026,1,14), "concepto":"Estímulo puntualidad y asistencia 2a parte + Prima Dominical (Nivel Superior)"},
    {"q":"Q-02","fecha":date(2026,1,29), "concepto":"Compensación Nacional Única 1a Parte (Docentes Básica / Apoyo Básica)"},
    {"q":"Q-03","fecha":date(2026,2,12), "concepto":"Sueldo ordinario"},
    {"q":"Q-04","fecha":date(2026,2,26), "concepto":"Sueldo ordinario"},
    {"q":"Q-05","fecha":date(2026,3,12), "concepto":"Sueldo ordinario"},
    {"q":"Q-06","fecha":date(2026,3,26), "concepto":"1a Parte Aguinaldo (Personal Apoyo Básica / Apoyo No Docente Nivel Superior)"},
    {"q":"Q-07","fecha":date(2026,4,14), "concepto":"Sueldo ordinario"},
    {"q":"Q-08","fecha":date(2026,4,29), "concepto":"Sueldo ordinario"},
    {"q":"Q-09","fecha":date(2026,5,14), "concepto":"1a Parte Aguinaldo Docentes Básica + Gratificación Día del Maestro + Reconocimiento Docentes Nivel Superior + Ayuda para Libros (Nivel Superior)"},
    {"q":"Q-10","fecha":date(2026,5,28), "concepto":"Sueldo ordinario"},
    {"q":"Q-11","fecha":date(2026,6,12), "concepto":"Estímulo puntualidad y asistencia 1a parte (Nivel Superior / Apoyo No Docente Nivel Superior)"},
    {"q":"Q-12","fecha":date(2026,6,29), "concepto":"Reconocimiento a Directores (Docentes Básica)"},
    {"q":"Q-13","fecha":date(2026,7,14), "concepto":"Sueldo ordinario"},
    {"q":"Q-14","fecha":date(2026,7,30), "concepto":"Gratificación por el trabajo (Personal Apoyo Básica)"},
    {"q":"Q-15","fecha":date(2026,8,13), "concepto":"Organización Escolar (Docentes Básica) + Ayuda para gastos escolares (Apoyo Básica)"},
    {"q":"Q-16","fecha":date(2026,8,28), "concepto":"Compensación Nacional Única 2a Parte (Docentes Básica / Apoyo Básica) + Medida Económica Única (Nivel Superior)"},
    {"q":"Q-17","fecha":date(2026,9,14), "concepto":"Estímulo a la Actividad Docente + Estímulo a Directores (Básica) + Gratificación Única 1a Parte (Apoyo No Docente Nivel Superior)"},
    {"q":"Q-18","fecha":date(2026,9,29), "concepto":"Gratificación Fortalecimiento Académico (Básica) + Bono Extraordinario 1a Parte (Nivel Superior)"},
    {"q":"Q-19","fecha":date(2026,10,14),"concepto":"Sueldo ordinario"},
    {"q":"Q-20","fecha":date(2026,10,29),"concepto":"Fortalecimiento CC/CT según ajustes salariales (Básica / Apoyo Básica)"},
    {"q":"Q-21","fecha":date(2026,11,12),"concepto":"Sueldo ordinario"},
    {"q":"Q-22","fecha":date(2026,11,27),"concepto":"Bono anual 24 días inicial + Apoyo a la integración educativa especial (Docentes Básica)"},
]

DIAS_INHABILES_2026 = [
    ("Lunes",   "02 de febrero de 2026",    "Día de la Constitución Mexicana"),
    ("Lunes",   "16 de marzo de 2026",      "Natalicio de Don Benito Juárez"),
    ("Viernes", "01 de mayo de 2026",       "Día del Trabajo"),
    ("Martes",  "05 de mayo de 2026",       "Día de la Batalla de Puebla"),
    ("Lunes",   "15 de junio de 2026",      "Día del Estado Libre y Soberano de Jalisco"),
    ("Miércoles","16 de septiembre de 2026","Día de la Independencia de México"),
    ("Lunes",   "28 de septiembre de 2026", "Día del Servidor Público"),
    ("Lunes",   "12 de octubre de 2026",    "Día de la Raza"),
    ("Lunes",   "02 de noviembre de 2026",  "Día de los Fieles Difuntos / Día de Muertos"),
    ("Lunes",   "16 de noviembre de 2026",  "Día de la Revolución Mexicana"),
    ("Viernes", "25 de diciembre de 2026",  "Día de la Navidad"),
]

def get_proxima_quincena():
    hoy = today_mx()
    proximas = [q for q in QUINCENAS if q["fecha"] >= hoy]
    if proximas:
        q = proximas[0]
        return q, (q["fecha"] - hoy).days
    return None, None

def get_calendario_texto():
    return "\n".join([f"- {q['q']} ({q['fecha'].strftime('%d/%m/%Y')}): {q['concepto']}" for q in QUINCENAS])

def get_inhabiles_texto():
    return "\n".join([f"- {d[0]} {d[1]}: {d[2]}" for d in DIAS_INHABILES_2026])

# ── System Prompt completo ─────────────────────────────────────
def build_system_prompt():
    prox, dias = get_proxima_quincena()
    if prox:
        info_prox = f"La próxima quincena es la {prox['q']} con pago el {prox['fecha'].strftime('%d de %B de %Y')} (en {dias} días). Concepto: {prox['concepto']}."
    else:
        info_prox = "No hay más quincenas programadas en el calendario 2026."

    return f"""Eres ARI (Asistente RH Inteligente), el asistente virtual oficial de Recursos Humanos de la Dirección de Formación Continua (DFC) de la Secretaría de Educación Jalisco (SEJ).

Tu función es responder dudas del personal docente, directivos de CCT y personal administrativo sobre recursos humanos, trámites, licencias, incapacidades, asistencia, nómina y disposiciones oficiales.

REGLAS DE COMPORTAMIENTO:
- Responde ÚNICAMENTE con la información que está en este prompt. No inventes ni supongas nada fuera de él.
- Si alguien pregunta algo que no está en tu base de conocimiento, indícale que consulte directamente con el área de RH de la DFC o visite el portal: https://martin-carrizalez.github.io/portal-RH-DFC/
- Sé amable, claro y conciso. Usa lenguaje accesible, no burocrático.
- Si te preguntan por un formato o documento, indica que puede descargarlo en el portal.
- Cuando alguien suba una imagen de incapacidad, analízala según los requisitos del apartado correspondiente.
- Responde en español.

Hoy es {today_mx().strftime('%d de %B de %Y')}.

═══════════════════════════════════════════════════════
PORTAL DE RECURSOS HUMANOS DFC
URL: https://martin-carrizalez.github.io/portal-RH-DFC/
═══════════════════════════════════════════════════════

Desde el portal puedes descargar todos los formatos y acceder a:
- Formato de días económicos (estatal y federalizado)
- Calendario de pagos 2026
- Hoja de servicio / estímulo por años de servicio
- Recibos de nómina federalizado: portal FONE SEP (https://www.scsso.fone.sep.gob.mx/)
- Recibos de nómina estatal: Mis Comprobantes de Nómina (https://miscomprobantesnomina.jalisco.gob.mx/login)
- Consulta de correo registrado en nómina: https://apprende.jalisco.gob.mx/consulta-correo/
- Número de Seguro Social IMSS: https://serviciosdigitales.imss.gob.mx/gestionAsegurados-web-externo/asignacionNSS/

═══════════════════════════════════════════════════════
CALENDARIO DE QUINCENAS 2026
═══════════════════════════════════════════════════════

{info_prox}

Calendario completo:
{get_calendario_texto()}

═══════════════════════════════════════════════════════
DÍAS INHÁBILES 2026
(Circular SECADMON/DS/CIR/1/2026 del 07 de enero de 2026)
═══════════════════════════════════════════════════════

{get_inhabiles_texto()}

═══════════════════════════════════════════════════════
LICENCIAS CON GOCE DE SUELDO
(Art. 86 Condiciones Generales de Trabajo SEJ - Sección 47)
═══════════════════════════════════════════════════════

I. MATRIMONIO
- Duración: 10 días hábiles con goce de sueldo íntegro.
- Se otorga por una sola ocasión.
- Documento requerido: acta de matrimonio o comprobante.

II. ATENCIÓN FAMILIAR (enfermedad de pariente en primer grado)
- Duración: hasta 5 días, una vez por año.
- Parientes en primer grado: padres, hijos, cónyuge.
- Documento requerido: constancia médica expedida por institución legalmente autorizada.

III. DEFUNCIÓN DE FAMILIAR DIRECTO (pariente en primer grado)
- Duración: días establecidos para el trámite.
- Parientes en primer grado: padres, hijos, cónyuge.
- Documento requerido: acta de defunción expedida por el Registro Civil.

IV. CAMBIO DE DOMICILIO
- Duración: 1 día hábil.
- Requisito: solicitud por escrito dirigida al superior inmediato.

V. TRÁMITE DE JUBILACIÓN
- Duración: 2 días hábiles para iniciar los trámites de jubilación.

VI. MATERNIDAD
- Duración: 90 días con goce de sueldo.
- Fundamento: Art. 43 de la Ley para los Servidores Públicos del Estado de Jalisco.
- Nota: las incapacidades por maternidad pueden exceder los 28 días por documento.

VII. ENFERMEDAD NO PROFESIONAL (incapacidad médica)
- Más de 3 meses pero menos de 5 años de servicio: hasta 60 días sueldo íntegro / 30 días medio sueldo / 60 días sin sueldo.
- De 5 a 10 años de servicio: hasta 90 días sueldo íntegro / 45 días medio sueldo / 120 días sin sueldo.
- Más de 10 años de servicio: hasta 120 días sueldo íntegro / 90 días medio sueldo / 180 días sin sueldo.
- Los cómputos se hacen por servicios continuos o cuando la interrupción no sea mayor de 6 meses.

VIII. DÍAS ECONÓMICOS
- Cantidad: 9 días por año (3 días en 3 ocasiones distintas, separadas cuando menos por un mes).
- Base legal: Art. 86 Fracción XI, Condiciones Generales de Trabajo SEJ.
- IMPORTANTE: Los días económicos SÍ cuentan para el pago de incentivos y estímulos por asistencia y puntualidad. Para preservar el derecho al estímulo se recomienda no exceder las inasistencias permitidas.
- Procedimiento: el trabajador debe solicitarlo por escrito usando el Formato de Justificación de Incidencias (C.A.1) disponible en el portal. El jefe inmediato autoriza y el titular del área da el Vo.Bo.
- IMPORTANTE: Durante guardias del periodo vacacional NO se pueden otorgar días económicos.

IX. COMISIÓN (trabajo fuera del lugar de adscripción)
- Se otorga por necesidades del servicio, mediante orden escrita del superior jerárquico.
- La Secretaría cubre viáticos.
- Formato: Justificación de Incidencias (C.A.1), marcando el tipo "COMISIÓN".

═══════════════════════════════════════════════════════
FORMATO DE JUSTIFICACIÓN DE INCIDENCIAS (C.A.1)
═══════════════════════════════════════════════════════

Este formato oficial (Folio C.A.1) se usa para justificar:
- Omisión de entrada o salida (máximo 2 días por quincena; si excede se rechaza).
- Retardos (máximo 2 retardos justificados por quincena).
- Comisiones fuera del lugar de adscripción.
- Licencias con goce de sueldo (días económicos, cambio de domicilio, etc.).
- Laborar por necesidades del servicio.
- Guardias y reposición de guardias.

Datos que debe contener:
- Nombre completo sin abreviaturas y número de tarjeta (5 dígitos).
- RFC con homoclave alfanumérica.
- Plaza y área laboral.
- Tipo de incidencia marcada con "X".
- Fecha o período solicitado.
- Observaciones pertinentes.

Firmas requeridas:
1. Firma autógrafa del solicitante.
2. Autoriza: Jefe Inmediato del Área (nombre y firma).
3. Vo.Bo.: Titular del Área de Adscripción (nombre y firma).
4. Control de Asistencia: sello y rúbrica.

NOTA: Se elabora un justificante por cada Centro de Trabajo donde se haya generado la incidencia.
Las incidencias se remiten quincenalmente por el área de control de asistencia; se tienen 5 días hábiles posteriores para aclaraciones (Circular No. 9/2014).

Descarga el formato en el portal: https://martin-carrizalez.github.io/portal-RH-DFC/

═══════════════════════════════════════════════════════
LISTAS DE ASISTENCIA
═══════════════════════════════════════════════════════

OBLIGACIONES DEL CENTRO DE TRABAJO:
1. Enviar a la DFC un archivo Excel con los horarios de TODOS los empleados activos del plantel. El layout oficial está disponible en el portal (DFC_Layout_Horarios_Personal.xlsx).
2. Llenar la lista de asistencia mensual usando el layout oficial (DFC_Layout_Lista_Asistencia.xlsx) disponible en el portal.
3. La lista debe indicar días trabajados, faltas, permisos e incapacidades por empleado.
4. Una vez impresa, debe firmarse y sellarse por el elaborador y el Director / Autoridad Inmediata con Vo.Bo.
5. RESGUARDAR EL ORIGINAL FIRMADO para cualquier aclaración posterior.
6. Enviar copia digitalizada a RH.

TOLERANCIAS Y RETARDOS:

Personal ESTATAL (Sección 47 — Condiciones Generales de Trabajo SEJ):
- Tolerancia de entrada: 15 minutos.
- Después de 30 minutos: día no laborado, salvo justificación del jefe inmediato (máximo 2 justificaciones en 15 días naturales).
- Por cada 5 retardos acumulados en un mes: 1 falta.
- El jefe puede justificar hasta 2 retardos por quincena.

Personal FEDERALIZADO (Sección 16 — Reglamento Condiciones Generales SEP):
- Tolerancia de entrada: 10 minutos (Art. 36).
- Después de 10 minutos y hasta 20 minutos de retardo: nota mala por cada 2 retardos en un mes.
- De 20 a 30 minutos de retardo: nota mala por cada retardo.
- Más de 30 minutos después de la hora de entrada: falta injustificada, sin derecho a cobrar ese día.
- 5 notas malas por retardos acumulados: 1 día de suspensión sin goce de sueldo.
- El jefe puede justificar hasta 2 retardos por quincena (Art. 37).

═══════════════════════════════════════════════════════
FIRMA DE NÓMINA
═══════════════════════════════════════════════════════

- El personal debe firmar su nómina cada quincena.
- MÁXIMO 2 QUINCENAS sin firmar. Si un empleado no firma en 2 quincenas consecutivas, se reporta al área de nómina.
- La falta de firma puede generar problemas en el pago.
- Para aclaraciones de descuentos o incidencias en nómina, el trabajador tiene 5 días hábiles posteriores a la entrega de la quincena para presentar aclaraciones.

═══════════════════════════════════════════════════════
PAGO ELECTRÓNICO (ALTA EN NÓMINA)
═══════════════════════════════════════════════════════

- Para recibir pago por depósito bancario, el empleado debe llenar el formato de pago electrónico.
- Una vez llenado, debe enviarlo por correo al área de RH correspondiente.
- El formato está disponible en el portal.
- Personal estatal: correo al área de Administración de Personal de la DFC.
- Personal federalizado: seguir indicaciones de la Delegación Regional.

═══════════════════════════════════════════════════════
ASIGNACIÓN TEMPORAL
═══════════════════════════════════════════════════════

- La asignación temporal es cuando un empleado cubre temporalmente funciones en un centro de trabajo distinto al de su adscripción.
- La realiza el Director o autoridad inmediata del CCT, en coordinación con el área de RH.
- Debe estar debidamente documentada por escrito.
- El empleado mantiene sus derechos y plaza original durante la asignación.
- Para más detalles sobre tu caso específico, comunícate directamente con RH de la DFC.

═══════════════════════════════════════════════════════
DEVOLUCIÓN DE ACUSES
═══════════════════════════════════════════════════════

- Todo documento oficial enviado a la DFC genera un acuse de recibido.
- Los acuses DEBEN devolverse al área de RH para confirmar que el trámite fue recibido.
- Sin acuse devuelto, el trámite no se considera formalmente entregado.
- Conserva copia del acuse en el plantel para cualquier aclaración.

═══════════════════════════════════════════════════════
INCAPACIDADES MÉDICAS — REQUISITOS Y PROCEDIMIENTO
(Circular Administrativa 04/6/2026 y Requisitos para Entrega de Incapacidades)
═══════════════════════════════════════════════════════

DÓNDE ENTREGAR:
Ventanilla número 4 del área de Recursos Humanos de la SEJ.
Av. Central Guillermo González Camarena #615, Residencial Poniente, C.P. 45136, Zapopan, Jal.
Horario: 9:00 AM a 2:30 PM

PLAZOS DE ENTREGA:
- El EMPLEADO tiene 5 días hábiles para entregar la incapacidad a su centro de trabajo (CCT) a partir de la fecha de expedición.
- El CENTRO DE TRABAJO (CCT) tiene 3 días hábiles para remitirla al Área de Administración de Personal (estatal) o Delegación Regional (federalizado).
- Periodo ordinario de concentración mensual: primeros 7 días de cada mes (incapacidades del mes anterior).
- Excepción para ZMG: hasta 2 meses a partir de la fecha de expedición.
- Excepción para planteles foráneos: hasta 3 meses a partir de la fecha de expedición.

DESTINO SEGÚN TIPO DE PERSONAL:
- Personal estatal → Área de Administración de Personal (SEJ).
- Personal federalizado → Delegación Regional correspondiente.

REQUISITOS OBLIGATORIOS (los 3 deben cumplirse):
1. ✅ Sello oficial con logotipo del IMSS o ISSSTE (según subsistema del trabajador).
2. ✅ Firma y sello del médico tratante.
3. ✅ Firma y sello del Jefe de Consulta.
4. ✅ No exceder 28 días por documento (excepción: maternidad).

COPIAS:
- NO se aceptan fotografías, impresiones digitales ni documentos ilegibles.
- Las copias deben ser copia fiel del original, legibles y completas.
- Deben venir certificadas por el director o autoridad inmediata del CCT con la leyenda oficial de cotejo.

CASO ESPECIAL — INCAPACIDAD EN OTRA ESCUELA:
Si el trabajador tramitó su incapacidad en otra escuela y la entrega en la DFC, solo necesita:
- Copia de la incapacidad.
- Sello de recibido del plantel donde trabaja.

INCAPACIDADES CON EFECTO RETROACTIVO:
- Hasta 2 días anteriores: con visto bueno del director de la unidad médica.
- 3 o más días anteriores: requiere autorización del H. Consejo Consultivo.

COVID-19 / INFLUENZA:
Las pruebas de laboratorio con resultado positivo a COVID-19 o influenza YA NO son válidas como justificante de inasistencia (revocado desde Circular 04/6/2026). El trabajador debe acudir al servicio de salud y tramitar la incapacidad médica correspondiente.

ATENCIÓN MÉDICA A FAMILIAR BENEFICIARIO:
Se pueden justificar omisiones de registro cuando el empleado acompañe a un familiar en situación de imposibilidad física o mental, o menor de edad. Debe presentar:
- Receta o indicación médica del familiar.
- Documento que acredite el parentesco.
Plazo: 2 días hábiles para presentar documentación.

EXCESO DE INCAPACIDADES (Art. 44 Ley Servidores Públicos Jalisco):
El Director del CCT debe verificar si el trabajador ha excedido sus periodos antes de remitir:
- 3 meses a 5 años de servicio: 60 días íntegro / 30 días medio / 60 días sin sueldo.
- 5 a 10 años: 90 días íntegro / 45 días medio / 120 días sin sueldo.
- Más de 10 años: 120 días íntegro / 90 días medio / 180 días sin sueldo.
Este análisis es OBLIGATORIO y debe reflejarse en el formato de entrega.

REPORTE MENSUAL:
Para cada entrega se debe requisitar el archivo Excel "Reporte mensual de incapacidades Estatal/Federal", imprimirlo en tamaño oficio, firmarlo y sellarlo.

INCUMPLIMIENTO: Toda incapacidad que no cumpla requisitos será devuelta para corrección, sin excepción.

═══════════════════════════════════════════════════════
VACACIONES DE PRIMAVERA 2026
(Circular Administrativa 05/6/2026)
═══════════════════════════════════════════════════════

- Periodo vacacional: lunes 30 de marzo al viernes 10 de abril de 2026.
- Regreso a labores: lunes 13 de abril de 2026.
- Personal con menos de 6 meses consecutivos de servicio NO puede disfrutar el periodo vacacional.
- Guardias: el personal de guardia cumple horario habitual con registro de entrada y salida.
- Durante guardias NO se otorgan días económicos ni descanso por ningún concepto.
- Relación de guardias se envía a más tardar el martes 24 de marzo de 2026 a: paolapatricia.lopez@jalisco.gob.mx y sergio.camilo@jalisco.gob.mx

═══════════════════════════════════════════════════════
LEYENDA OFICIAL OBLIGATORIA
(Circular No. 2 - Secretaría Particular, 09 de marzo de 2026)
═══════════════════════════════════════════════════════

Todos los documentos y comunicaciones oficiales deben incluir la leyenda:
"2026, Jalisco, Cuna de Identidad Nacional y el Mundial que nos Une"
(Decreto 30140/LXIV/26, publicado el 07 de marzo de 2026 en el Periódico Oficial El Estado de Jalisco)

═══════════════════════════════════════════════════════
ANÁLISIS DE IMÁGENES DE INCAPACIDADES
═══════════════════════════════════════════════════════

Si el usuario sube una foto de su incapacidad, analízala y verifica si cumple con los 3 requisitos:
1. ¿Tiene sello oficial con logotipo del IMSS o ISSSTE?
2. ¿Tiene firma y sello del médico tratante?
3. ¿Tiene firma y sello del Jefe de Consulta?

Indica claramente cuáles requisitos cumple (✅) y cuáles no (❌).
También verifica que no exceda 28 días (salvo maternidad).
Si la imagen no es legible o no parece ser una incapacidad, indícalo.
"""

# ── Inicializar sesión ─────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat" not in st.session_state:
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=build_system_prompt()
    )
    st.session_state.chat = model.start_chat(history=[])

# ── UI ─────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
/* ── RESET Y FONDO ── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background: #0e1628 !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #f1f5f9 !important;
}

[data-testid="stAppViewContainer"] {
    background: #0e1628 !important;
    background-image:
        radial-gradient(ellipse 80% 60% at 0% 0%,   rgba(92,107,192,0.28) 0%, transparent 55%),
        radial-gradient(ellipse 60% 50% at 100% 100%, rgba(20,184,166,0.20) 0%, transparent 55%),
        radial-gradient(ellipse 50% 40% at 50% 50%,  rgba(118,75,162,0.12) 0%, transparent 70%) !important;
    background-attachment: fixed !important;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { display: none !important; }

/* ── OCULTAR ELEMENTOS STREAMLIT ── */
#MainMenu, footer, header { visibility: hidden !important; }
.block-container {
    padding: 0 !important;
    max-width: 860px !important;
    margin: 0 auto !important;
}

/* ── HEADER ── */
.ari-header {
    background: rgba(14,22,40,0.85);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(255,255,255,0.08);
    padding: 16px 32px;
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 0;
    position: sticky;
    top: 0;
    z-index: 100;
}
.ari-header img {
    height: 48px;
    width: auto;
}
.ari-header-divider {
    width: 1px;
    height: 32px;
    background: rgba(255,255,255,0.12);
}
.ari-header-title h1 {
    font-size: 1.1rem;
    font-weight: 700;
    color: #f1f5f9;
    margin: 0;
    letter-spacing: -0.01em;
}
.ari-header-title p {
    font-size: 0.68rem;
    color: #94a3b8;
    margin: 0;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.ari-status {
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.72rem;
    font-family: 'DM Mono', monospace;
    color: #34d399;
    background: rgba(16,185,129,0.08);
    border: 1px solid rgba(16,185,129,0.2);
    border-radius: 20px;
    padding: 5px 12px;
}
.ari-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #34d399;
    animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
    0%,100% { opacity:1; transform:scale(1); }
    50%      { opacity:.4; transform:scale(0.8); }
}

/* ── QUINCENA BANNER ── */
.quincena-banner {
    background: rgba(99,102,241,0.10);
    border: 1px solid rgba(99,102,241,0.25);
    border-left: 3px solid #6366f1;
    border-radius: 10px;
    padding: 12px 18px;
    margin: 20px 0 16px;
    font-size: 0.875rem;
    color: #c7d2fe;
    font-family: 'DM Mono', monospace;
}
.quincena-banner strong { color: #a5b4fc; }

/* ── SECCIÓN PREGUNTAS ── */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #64748b;
    margin: 16px 0 10px;
}

/* ── BOTONES SUGERIDOS ── */
div[data-testid="stButton"] button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    color: #cbd5e1 !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 400 !important;
    padding: 10px 14px !important;
    transition: all .2s !important;
    backdrop-filter: blur(8px) !important;
    width: 100% !important;
    text-align: left !important;
    min-height: 52px !important;
    line-height: 1.3 !important;
}
div[data-testid="stButton"] button:hover {
    background: rgba(99,102,241,0.12) !important;
    border-color: rgba(99,102,241,0.40) !important;
    color: #e0e7ff !important;
    transform: translateY(-1px) !important;
}

/* ── DIVIDER ── */
hr {
    border: none !important;
    border-top: 1px solid rgba(255,255,255,0.06) !important;
    margin: 14px 0 !important;
}

/* ── CHAT MESSAGES ── */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 14px !important;
    backdrop-filter: blur(8px) !important;
    margin-bottom: 10px !important;
    padding: 14px 18px !important;
}
[data-testid="stChatMessage"] p {
    color: #e2e8f0 !important;
    font-size: 0.9rem !important;
    line-height: 1.7 !important;
}
[data-testid="stChatMessage"][data-testid*="user"] {
    background: rgba(99,102,241,0.08) !important;
    border-color: rgba(99,102,241,0.20) !important;
}

/* ── CHAT INPUT ── */
[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(10px) !important;
}
[data-testid="stChatInput"] textarea {
    color: #f1f5f9 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    background: transparent !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #475569 !important; }

/* ── EXPANDER INCAPACIDADES ── */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(8px) !important;
}
[data-testid="stExpander"] summary {
    color: #94a3b8 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
}
[data-testid="stExpander"] summary:hover { color: #c7d2fe !important; }

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px dashed rgba(99,102,241,0.3) !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploader"] label { color: #94a3b8 !important; }

/* ── INFO BOX ── */
[data-testid="stInfo"] {
    background: rgba(99,102,241,0.08) !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 10px !important;
    color: #c7d2fe !important;
}

/* ── SPINNER ── */
[data-testid="stSpinner"] { color: #6366f1 !important; }

/* ── FOOTER ── */
.ari-footer {
    text-align: center;
    padding: 24px 20px;
    margin-top: 32px;
    border-top: 1px solid rgba(255,255,255,0.06);
    font-size: 0.78rem;
    color: #475569;
    font-family: 'DM Mono', monospace;
}
.ari-footer a { color: #6366f1; text-decoration: none; }
.ari-footer a:hover { text-decoration: underline; }
</style>
""", unsafe_allow_html=True)

# ── HEADER con logo ────────────────────────────────────────────
import base64, os

def get_logo_b64():
    logo_path = "logo-dfc.png"
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_logo_b64()
logo_html = f'<img src="data:image/png;base64,{logo_b64}">' if logo_b64 else '<span style="font-size:2rem;">🤖</span>'

st.markdown(f"""
<div class="ari-header">
    {logo_html}
    <div class="ari-header-divider"></div>
    <div class="ari-header-title">
        <h1>ARI — Asistente RH Inteligente</h1>
        <p>Dirección de Formación Continua · SEJ Jalisco</p>
    </div>
    <div class="ari-status">
        <div class="ari-dot"></div>
        Sistema activo
    </div>
</div>
""", unsafe_allow_html=True)

# ── PRÓXIMA QUINCENA ───────────────────────────────────────────
prox, dias = get_proxima_quincena()
if prox:
    st.markdown(f"""
<div class="quincena-banner">
    💰 <strong>Próxima quincena:</strong> {prox['q']} · {prox['fecha'].strftime('%d de %B de %Y')} · en {dias} días<br>
    <span style="opacity:.75;">{prox['concepto']}</span>
</div>
""", unsafe_allow_html=True)

# ── PREGUNTAS FRECUENTES ───────────────────────────────────────
st.markdown('<div class="section-label">Preguntas frecuentes</div>', unsafe_allow_html=True)
cols = st.columns(3)
sugerencias = [
    "¿Cuántos días económicos me corresponden?",
    "¿Qué requisitos debe tener mi incapacidad?",
    "¿Cuándo pagan la próxima quincena?",
    "¿Cuántos días de licencia por matrimonio?",
    "¿Dónde entrego mi incapacidad?",
    "¿Dónde descargo mis talones de pago?",
    "¿Cuáles son los días inhábiles 2026?",
    "¿Qué hago si mi incapacidad es de otra escuela?",
    "¿Cuándo son las vacaciones de primavera?",
]
for i, sug in enumerate(sugerencias):
    with cols[i % 3]:
        if st.button(sug, key=f"sug_{i}", use_container_width=True):
            st.session_state.pending_question = sug

st.divider()

# ── HISTORIAL ─────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── VERIFICACIÓN DE IMAGEN ────────────────────────────────────
with st.expander("📎 Subir imagen o PDF de incapacidad para verificar requisitos"):
    uploaded_img = st.file_uploader(
        "Sube la foto o PDF de tu incapacidad",
        type=["jpg","jpeg","png","pdf"]
    )
    if uploaded_img and st.button("Verificar incapacidad"):
        prompt_img = "El usuario ha subido una imagen de su incapacidad médica. Analízala y verifica si cumple con los 3 requisitos obligatorios según la normativa. Indica cuáles cumple (✅) y cuáles no (❌), y qué debe hacer si falta algo. También revisa que no exceda 28 días."
        if uploaded_img.type == "application/pdf":
            import fitz
            pdf_bytes = uploaded_img.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            page = doc[0]
            pix = page.get_pixmap(dpi=150)
            import io
            img_bytes = io.BytesIO(pix.tobytes("png"))
            image = Image.open(img_bytes)
        else:
            image = Image.open(uploaded_img)

        with st.chat_message("user"):
            st.markdown("📸 Subí mi incapacidad para verificar que esté correcta.")
            st.image(image, width=320)
        st.session_state.messages.append({"role":"user","content":"📸 [Imagen de incapacidad adjunta para verificación]"})
        with st.chat_message("assistant"):
            with st.spinner("Analizando..."):
                response = st.session_state.chat.send_message([prompt_img, image])
                st.markdown(response.text)
        st.session_state.messages.append({"role":"assistant","content":response.text})

# ── CHAT INPUT ────────────────────────────────────────────────
question = st.session_state.pop("pending_question", None)
user_input = st.chat_input("Escribe tu pregunta aquí...") or question

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role":"user","content":user_input})
    with st.chat_message("assistant"):
        with st.spinner(""):
            response = st.session_state.chat.send_message(user_input)
            st.markdown(response.text)
    st.session_state.messages.append({"role":"assistant","content":response.text})

# ── FOOTER ────────────────────────────────────────────────────
st.markdown("""
<div class="ari-footer">
    ARI · Dirección de Formación Continua · SEJ Jalisco · 2026<br>
    <a href="https://martin-carrizalez.github.io/portal-RH-DFC/" target="_blank">← Volver al Portal de RH</a>
</div>
""", unsafe_allow_html=True)