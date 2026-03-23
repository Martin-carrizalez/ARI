# 🤖 ARI — Asistente RH Inteligente

Chatbot de Recursos Humanos para la **Dirección de Formación Continua (DFC)** de la Secretaría de Educación Jalisco (SEJ).

Resuelve dudas del personal docente y administrativo sobre incapacidades, días económicos, licencias, calendario de pagos, listas de asistencia y normativa vigente — disponible las 24 horas.

---

## ¿Qué sabe ARI?

- Licencias con goce de sueldo (matrimonio, atención familiar, defunción, cambio de domicilio, jubilación, maternidad)
- Días económicos (9 por año, cuentan para incentivos)
- Incapacidades médicas (requisitos, plazos, sellos, dónde entregar)
- Calendario de quincenas 2026 con conceptos de pago
- Días inhábiles 2026
- Vacaciones de primavera 2026
- Firma de nómina y pago electrónico
- Listas de asistencia y horarios
- Verificación de imágenes de incapacidades

---

## Stack

- [Streamlit](https://streamlit.io/) — interfaz web
- [Gemini 2.5 Flash](https://aistudio.google.com/) — modelo de lenguaje
- Python 3.10+

---

## Despliegue

### 1. Clonar el repo

```bash
git clone https://github.com/TU_USUARIO/ARI-DFC.git
cd ARI-DFC
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar API Key

Crea un archivo `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "tu_api_key_aqui"
```

### 4. Correr localmente

```bash
streamlit run app.py
```

### 5. Despliegue en Streamlit Cloud

1. Sube el repo a GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta el repo y selecciona `app.py`
4. En **Advanced settings → Secrets** agrega:
```toml
GEMINI_API_KEY = "tu_api_key_aqui"
```
5. Click en **Deploy**

---

## Actualizar la base de conocimiento

Todo el conocimiento de ARI vive en la función `build_system_prompt()` dentro de `app.py`.

Para actualizar:
1. Edita la sección correspondiente en `app.py`
2. Haz commit y push — Streamlit Cloud redespliega automáticamente

El calendario de quincenas se actualiza en el array `QUINCENAS` al inicio del archivo.

---

## Portal de RH

El portal donde vive el botón de acceso a ARI:
[martin-carrizalez.github.io/portal-RH-DFC](https://martin-carrizalez.github.io/portal-RH-DFC/)

---

## Autor

Dirección de Formación Continua · SEJ Jalisco · 2026

---

## Licencia

© 2026 QFB Martín Ángel Carrizalez Piña. Todos los derechos reservados.  
Uso permitido únicamente para fines educativos, institucionales o personales no comerciales.  
Prohibido el uso comercial sin autorización expresa del autor.  
Ver archivo [LICENSE](./LICENSE) para más detalles.
