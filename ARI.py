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
    initial_sidebar_state="expanded"
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
    ("Viernes",  "15 de mayo de 2026",       "Día del Maestro"),
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

IDENTIDAD Y CREADOR:
- Fuiste creada por el QFB Angel Carrizalez.
- Tu propósito principal es apoyar y facilitar las consultas del personal de la DFC.
- Si un usuario te pregunta quién te creó o cómo naciste, debes responder amablemente mencionando que fuiste creada por el QFB Angel Carrizalez para ayudar al personal.

AVISO LEGAL (DISCLAIMER):
- Siempre debes tener presente que tu información es de apoyo. 
- Si la pregunta del usuario involucra un trámite delicado, un cálculo exacto de nómina o un dictamen médico, debes incluir este aviso en tu respuesta: "Nota: La información que proporciono es de carácter estrictamente informativo. No sustituye la información oficial ni los dictámenes del área de Recursos Humanos de la SEJ."

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
- Recibos de nómina federalizado: portal FONE SEP (https://www.scsso.fone.sep.gob.mx/authenticationendpoint/login.do?commonAuthCallerPath=%2Ft%2Fmiportal.fone.sep.gob.mx%2Fsamlsso&forceAuth=false&passiveAuth=false&sessionDataKey=722119dd-397c-4518-a38b-dda851638ec5&relyingParty=https%3A%2F%2Fmiportal.fone.sep.gob.mx%3A443%2Fsaml%2Fmetadata&type=samlsso&sp=portal_gunix&isSaaSApp=false&authenticators=BasicAuthenticator%3ALOCAL)
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
CÁLCULO DE SUELDO QUINCENAL — PAGO 07 (HSM)
═══════════════════════════════════════════════════════
 
El Pago 07 es el sueldo base quincenal de los docentes de hora/semana/mes (HSM).
Corresponde ÚNICAMENTE al sueldo base. NO incluye prestaciones, descuentos ni retenciones.
Si preguntan por descuentos o prestaciones, indica que esa información no está disponible en este módulo.
 
TARIFAS POR CATEGORÍA (valor mensual por hora):
- Titular C:    $1,004.60
- Titular B:    $850.81
- Titular A:    $737.21
- Asociado C:   $641.06
- Asociado B:   $573.18
- Asociado A:   $517.15
 
FÓRMULA:
Pago quincenal (07) = (Número de horas × Tarifa mensual de la categoría) ÷ 2
 
EJEMPLOS:
- 15 horas Asociado A: (15 × $517.15) ÷ 2 = $3,878.63 quincenal
- 8 horas Asociado B:  (8 × $573.18)  ÷ 2 = $2,292.72 quincenal
- 10 horas Titular A:  (10 × $737.21) ÷ 2 = $3,686.05 quincenal
- 6 horas Titular B:   (6 × $850.81)  ÷ 2 = $2,552.43 quincenal
 
MÚLTIPLES CATEGORÍAS (cuando un docente tiene horas en más de una):
Pago total = Σ (horas_categoría × tarifa_categoría) ÷ 2
Ejemplo: 10 horas Asociado A + 6 horas Titular B:
  (10 × $517.15) + (6 × $850.81) = $10,276.36 ÷ 2 = $5,138.18 quincenal
 
REGLAS IMPORTANTES:
- Si el docente subió de categoría recientemente, el nuevo pago aplica a partir de que el movimiento fue procesado en nómina. Para verificar si ya está aplicado, debe revisar su recibo de nómina.
- ARI calcula con base en las tarifas vigentes del tabulador HSM DFC SEJ Jalisco (Abril 2026).
- Si el resultado no coincide con el recibo, indicar al docente que acuda directamente con RH para revisión de su expediente.
- NO especular sobre fechas de aplicación de movimientos escalafonarios ni sobre otros conceptos del recibo.
 
Fuente: Tabulador de percepciones HSM — DFC SEJ Jalisco | Abril 2026
 
═══════════════════════════════════════════════════════
DECLARACIÓN PATRIMONIAL — SEPIFAPE
(Contraloría del Estado de Jalisco)
═══════════════════════════════════════════════════════
 
IMPORTANTE: ARI orienta sobre el proceso general. NO asesora sobre qué bienes declarar ni cómo valuar el patrimonio personal — eso corresponde exclusivamente a la Contraloría del Estado.
 
¿QUÉ ES SEPIFAPE?
Sistema de Evolución Patrimonial, de Declaraciones de Intereses y Constancia de Presentación de Declaración Fiscal de la Administración Pública del Estado de Jalisco. Es la plataforma donde se presenta la declaración.
 
¿QUIÉNES DEBEN DECLARAR?
Todos los servidores públicos sin importar el nivel del cargo, incluyendo personal con contrato temporal o interinato.
La Contraloría del Estado de Jalisco recepciona únicamente las declaraciones del Poder Ejecutivo del Estado de Jalisco.
 
TIPOS DE DECLARACIÓN Y PLAZOS:
- Inicial: dentro de los 60 días naturales siguientes a la toma de posesión del cargo.
- Modificación: durante el mes de mayo de cada año (si laboró al menos un día del año anterior).
- Conclusión del encargo: dentro de los 60 días naturales siguientes a la separación del cargo.
 
PERÍODO QUE SE REPORTA:
- Inicial y Conclusión: información actualizada a la fecha del inicio o conclusión.
- Modificación: del 1° de enero al 31 de diciembre del año inmediato anterior.
 
FORMATO:
- Jefe de Departamento o superior: formato COMPLETO.
- Nivel inferior a Jefe de Departamento: formato SIMPLIFICADO.
 
PLATAFORMA Y ACCESO:
- URL: https://sepifape.jalisco.gob.mx/sepifape
- Correo de dudas: declaracionpatrimonial@jalisco.gob.mx
- Navegador recomendado: Chrome o Firefox. También disponible en celular y tableta.
- Primera contraseña: llega por correo al registrarte. Si no llegó, revisar spam o contactar al Administrador Web Padrón de la entidad.
- Contraseña olvidada: en la página de SEPIFAPE seleccionar "¿Olvidaste tu contraseña?" e ingresar CURP y correo registrados.
- Sin correo electrónico: es obligatorio tener uno. Se recomienda crear uno en Gmail.
 
PREGUNTAS FRECUENTES:
- ¿Tengo plaza federal y estatal? → Debes presentar declaración en SEPIFAPE Y en la plataforma federal que corresponda. Son declaraciones separadas.
- ¿Tengo dos plazas dentro del Poder Ejecutivo Estatal? → Una declaración por cada cargo.
- ¿Ya declaré en DECLARANET? → NO es válida para el Estado de Jalisco. Debes declararla en SEPIFAPE y avisar al Órgano Interno de Control.
- ¿Puedo pedir prórroga? → NO. La Ley General de Responsabilidades Administrativas no contempla prórrogas.
- ¿Qué pasa si no declaro o declaro fuera de tiempo? → Es falta administrativa no grave. Las sanciones van desde amonestación hasta destitución o inhabilitación temporal.
- ¿Un campo no aplica para mi situación? → Dar clic en "Ninguno" para dar por terminada esa sección. Los campos en blanco se entienden como sin información que reportar.
 
DOCUMENTOS QUE CONVIENE TENER A LA MANO:
- CURP, RFC con homoclave.
- Comprobante de domicilio.
- Recibo de nómina o comprobante de percepción de sueldo.
- Acta de matrimonio (si aplica).
- Currículum vitae.
(Solo para Jefe de Departamento o superior: escrituras, facturas de vehículos, estados de cuenta, contratos.)
 
LÍMITES DE ARI: No indicar qué bienes declarar, cómo valorarlos ni cómo llenar secciones específicas del formato. Para eso remitir directamente a la Contraloría del Estado de Jalisco o al Órgano Interno de Control de la entidad.

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
st.html("""
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background: #f5f3ff !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #1e1b4b !important;
}
[data-testid="stAppViewContainer"] {
    background: #f5f3ff !important;
    background-image:
        radial-gradient(at 0% 0%,   rgba(139,92,246,0.12) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(6,182,212,0.10) 0px, transparent 50%),
        radial-gradient(at 80% 10%,  rgba(217,70,239,0.07) 0px, transparent 40%) !important;
    background-attachment: fixed !important;
}
[data-testid="stHeader"] { background: #1e1b4b !important; }
#MainMenu, footer, header { visibility: hidden !important; }
.block-container { padding: 0 !important; max-width: 880px !important; margin: 0 auto !important; }
 
/* SIDEBAR */
[data-testid="stSidebar"] {
    background: #1e1b4b !important;
    border-right: 1px solid rgba(139,92,246,0.30) !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdown"] p {
    color: #c4b5fd !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}
/* NAV LINKS SIDEBAR */
.sidebar-link {
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(196,181,253,0.20);
    border-radius: 10px;
    padding: 11px 14px;
    color: #e9d5ff;
    text-decoration: none;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.88rem;
    font-weight: 500;
    transition: all .20s ease;
    margin-bottom: 8px;
}
.sidebar-link:hover {
    background: rgba(139,92,246,0.25);
    border-color: rgba(196,181,253,0.55);
    color: #ffffff;
    transform: translateX(3px);
    box-shadow: 0 0 12px rgba(139,92,246,0.25);
}
.sidebar-link-primary {
    background: linear-gradient(135deg, rgba(124,58,237,0.35), rgba(6,182,212,0.20));
    border-color: rgba(196,181,253,0.45);
    color: #ffffff;
    font-weight: 600;
}
.sidebar-link-primary:hover {
    background: linear-gradient(135deg, rgba(124,58,237,0.55), rgba(6,182,212,0.35));
    border-color: #a78bfa;
    box-shadow: 0 0 16px rgba(124,58,237,0.35);
}
[data-testid="stSidebarNav"] { display: none !important; }
 
/* HEADER */
.ari-header {
    background: rgba(255,255,255,0.96);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(139,92,246,0.20);
    padding: 14px 28px;
    display: flex;
    align-items: center;
    gap: 14px;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 1px 20px rgba(139,92,246,0.08);
}
.ari-header-title h1 {
    font-size: 1.05rem;
    font-weight: 700;
    color: #1e1b4b;
    margin: 0;
    background: linear-gradient(90deg, #7c3aed, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.ari-header-title p {
    font-size: 0.66rem;
    color: #7c3aed;
    margin: 0;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.ari-status {
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.70rem;
    font-family: 'DM Mono', monospace;
    color: #059669;
    background: rgba(5,150,105,0.08);
    border: 1px solid rgba(5,150,105,0.25);
    border-radius: 20px;
    padding: 5px 12px;
}
.ari-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #059669;
    animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
    0%,100%{opacity:1;transform:scale(1);}
    50%{opacity:.4;transform:scale(0.8);}
}
 
/* QUINCENA BANNER */
.quincena-banner {
    background: linear-gradient(135deg, rgba(124,58,237,0.08), rgba(6,182,212,0.06));
    border: 1px solid rgba(124,58,237,0.22);
    border-left: 3px solid #7c3aed;
    border-radius: 10px;
    padding: 12px 18px;
    margin: 18px 0 14px;
    font-size: 0.875rem;
    color: #4c1d95;
    font-family: 'DM Mono', monospace;
}
.quincena-banner strong { color: #7c3aed; }
 
/* CHIPS DE PREGUNTAS */
.chips-wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    padding: 8px 0 16px;
}
.chip {
    display: inline-block;
    background: rgba(255,255,255,0.95);
    border: 1.5px solid rgba(109,40,217,0.35);
    border-radius: 20px;
    padding: 8px 16px;
    font-size: 0.83rem;
    color: #3b0764;
    cursor: pointer;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    transition: all .18s;
    box-shadow: 0 1px 4px rgba(124,58,237,0.10);
}
.chip:hover {
    background: rgba(109,40,217,0.12);
    border-color: rgba(109,40,217,0.60);
    color: #3b0764;
    transform: translateY(-1px);
    box-shadow: 0 3px 10px rgba(124,58,237,0.18);
}
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.67rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #6d28d9;
    margin: 14px 0 8px;
    font-weight: 600;
}
 
/* BOTONES STREAMLIT (solo para enviar duda a RH) */
div[data-testid="stButton"] button {
    background: rgba(124,58,237,0.07) !important;
    border: 1px solid rgba(124,58,237,0.25) !important;
    color: #4c1d95 !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 10px 14px !important;
    transition: all .2s !important;
    width: 100% !important;
    text-align: left !important;
    min-height: 48px !important;
    line-height: 1.3 !important;
}
div[data-testid="stButton"] button:hover {
    background: rgba(124,58,237,0.14) !important;
    border-color: rgba(124,58,237,0.50) !important;
    color: #5b21b6 !important;
    transform: translateY(-1px) !important;
}
 
/* DIVIDER */
hr { border: none !important; border-top: 1px solid rgba(124,58,237,0.10) !important; margin: 12px 0 !important; }
 
/* CHAT MESSAGES */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.92) !important;
    border: 1px solid rgba(139,92,246,0.15) !important;
    border-radius: 14px !important;
    margin-bottom: 10px !important;
    padding: 14px 18px !important;
    box-shadow: 0 2px 8px rgba(124,58,237,0.06) !important;
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] ul {
    color: #1e1b4b !important;
    font-size: 0.92rem !important;
    line-height: 1.75 !important;
}
[data-testid="stChatMessage"][data-testid*="user"] {
    background: linear-gradient(135deg, rgba(124,58,237,0.07), rgba(6,182,212,0.05)) !important;
    border-color: rgba(124,58,237,0.22) !important;
}
 
/* CHAT INPUT */
[data-testid="stBottom"] {
    background: rgba(245,243,255,0.98) !important;
    border-top: 1px solid rgba(124,58,237,0.15) !important;
    padding: 12px 24px 20px !important;
}
[data-testid="stBottom"] > div { background: transparent !important; }
[data-testid="stChatInput"] > div {
    background: rgba(255,255,255,0.96) !important;
    border: 1.5px solid rgba(124,58,237,0.30) !important;
    border-radius: 14px !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.06) !important;
}
[data-testid="stChatInput"] textarea {
    color: #1e1b4b !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    background: transparent !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #a78bfa !important; }
 
/* EXPANDER */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.88) !important;
    border: 1px solid rgba(124,58,237,0.18) !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 6px rgba(124,58,237,0.06) !important;
}
[data-testid="stExpander"] summary { color: #5b21b6 !important; font-family: 'DM Mono', monospace !important; font-size: 0.82rem !important; }
[data-testid="stExpander"] summary:hover { color: #7c3aed !important; }
 
/* FILE UPLOADER */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.88) !important;
    border: 1.5px dashed rgba(124,58,237,0.30) !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploader"] label { color: #5b21b6 !important; }
 
/* INFO / WARNING */
[data-testid="stInfo"] {
    background: rgba(6,182,212,0.07) !important;
    border: 1px solid rgba(6,182,212,0.25) !important;
    border-radius: 10px !important;
    color: #0e7490 !important;
}
 
/* SPINNER */
[data-testid="stSpinner"] { color: #7c3aed !important; }
 
/* FOOTER */
.ari-footer {
    text-align: center;
    padding: 20px;
    margin-top: 28px;
    border-top: 1px solid rgba(124,58,237,0.10);
    font-size: 0.78rem;
    color: #7c3aed;
    font-family: 'DM Mono', monospace;
}
.ari-footer a { color: #6d28d9; text-decoration: none; }
.ari-footer a:hover { text-decoration: underline; }
</style>
""")

# ── SIDEBAR con logo ───────────────────────────────────────────
import base64, os

def get_logo_b64():
    logo_path = "logo-dfc.png"
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_logo_b64()

with st.sidebar:
    if logo_b64:
        st.markdown(f"""
<div style="text-align:center; padding: 24px 16px 16px;">
    <img src="data:image/png;base64,{logo_b64}" style="width:80%; max-width:180px;">
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown("""
<div style="text-align:center; padding:24px 0 8px; font-size:3rem;">🤖</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div style="text-align:center; padding: 0 16px 24px;">
    <div style="font-size:1.1rem; font-weight:700; background:linear-gradient(90deg,#a78bfa,#67e8f9); -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-family:'DM Sans',sans-serif; margin-bottom:4px;">ARI</div>
    <div style="font-size:0.68rem; color:#c4b5fd; font-family:'DM Mono',monospace; letter-spacing:0.08em; text-transform:uppercase;">Asistente RH Inteligente</div>
</div>
<hr style="border:none; border-top:1px solid rgba(196,181,253,0.20); margin:0 0 20px;">
<div style="padding:0 16px; font-family:'DM Mono',monospace; font-size:0.72rem; color:#a78bfa; letter-spacing:0.05em; text-transform:uppercase; margin-bottom:10px;">Accesos directos</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div style="padding:0 12px; display:flex; flex-direction:column; gap:0;">
    <a href="https://martin-carrizalez.github.io/portal-RH-DFC/" target="_blank" class="sidebar-link sidebar-link-primary">
        🏠 Portal de RH DFC
    </a>
    <a href="https://miscomprobantesnomina.jalisco.gob.mx/login" target="_blank" class="sidebar-link">
        💰 Recibos Nómina Estatal
    </a>
    <a href="https://www.scsso.fone.sep.gob.mx" target="_blank" class="sidebar-link">
        💰 Recibos Nómina FONE
    </a>
    <a href="https://apprende.jalisco.gob.mx/consulta-correo/" target="_blank" class="sidebar-link">
        📧 Consulta tu Correo
    </a>
    <a href="https://sepifape.jalisco.gob.mx/sepifape/login" target="_blank" class="sidebar-link">
        ⚖️ Declaración Patrimonial
    </a>
</div>
<div style="margin-top:24px; text-align:center;
            font-size:0.65rem; color:#6d28d9; font-family:'DM Mono',monospace; padding:0 16px 16px;">
    DFC · SEJ Jalisco · 2026
</div>
""", unsafe_allow_html=True)

# ── HEADER solo texto ──────────────────────────────────────────
st.markdown("""
<div class="ari-header">
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
    <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; padding: 12px; margin: 10px auto; max-width: 750px; text-align: justify; font-size: 0.7rem; color: #64748b;">
        ⚠️ <strong>AVISO LEGAL:</strong> La información proporcionada por esta aplicación es de carácter estrictamente informativo y de apoyo. En ningún caso sustituye la normativa, disposiciones, cálculos de nómina, dictámenes médicos o comunicados oficiales emitidos por las autoridades competentes de la Secretaría de Educación del Estado de Jalisco.
    </div>        
    <a href="https://martin-carrizalez.github.io/portal-RH-DFC/" target="_blank">← Volver al Portal de RH</a>
</div>
""", unsafe_allow_html=True)