# Historias de Usuario — LSP Vision AI
## Universidad Privada del Norte · Capstone Project Sistemas 2026
### Versión final unificada (documentación de planificación + features implementados)

Todas las historias siguen el formato: **"Como [rol], quiero [acción] para [beneficio]"**
con criterios de aceptación en formato Gherkin simplificado (Dado/Cuando/Entonces).

Prioridad MoSCoW: **M** = Must have · **S** = Should have · **C** = Could have · **W** = Won't have (esta versión)

---

## Planificación de Sprints

El proyecto se desarrolló en **5 Sprints** (> 3 requeridos por estándar académico UPN), más una fase de inicio previa:

| Sprint | Nombre | HUs | Entregable principal |
|---|---|---|---|
| **Sprint 1** | Planificación, Dataset y Modelo ML | HU-01, HU-02, HU-03, HU-04, HU-05, HU-06, HU-07 | Arquitectura definida, entorno configurado, dataset LSP y modelo SVM entrenado (≥ 85% accuracy) |
| **Sprint 2** | Aplicación Web, Calidad y Seguridad | HU-08, HU-09, HU-10, HU-11, HU-12, HU-13, HU-14, HU-17, HU-18, HU-22 | App Streamlit funcional, auth HMAC, auditoría, 31 tests automatizados y dashboard QA |
| **Sprint 3** | Ética, Accesibilidad y Despliegue | HU-15, HU-16, HU-19, HU-20, HU-21 | WCAG 2.1 AA, explicabilidad de IA, privacidad GDPR Art. 25 y despliegue web |

> Todos los Sprints tuvieron duración de 2-3 semanas con Sprint Review y Retrospectiva al final.
> El Definition of Done completo se encuentra en [`DEFINITION_OF_DONE.md`](DEFINITION_OF_DONE.md).

---

> **Nota de consolidación:** este documento combina las historias de la documentación del proyecto
> (proceso de desarrollo por sprints) con las historias de los features ya implementados en el código.
> Se renumeró de corrido para evitar colisiones de código y se eliminó la duplicación del pipeline
> de reconocimiento en tiempo real (antes repetido entre la HU de "traducción" y la HU de "clasificación").
> Los campos **Módulos** y **Estado** de las historias de desarrollo son inferidos: ajústalos contra tu repositorio real.

---

## HU-01 — Definición de Requerimientos y Alcance del Sistema
**Sprint:** 1 — Planificación y Arquitectura

> **Como** equipo de desarrollo,
> **quiero** tener claramente definidos los requerimientos funcionales y no funcionales del sistema,
> **para** poder planificar el desarrollo con precisión y alinearlo al objetivo general del proyecto.

**Prioridad:** M (Must have)
**Módulos:** `docs/requerimientos.md` (documentación)
**Estado:** ✅ Completada

### Criterios de Aceptación

**CA-01.1 — Cobertura de requerimientos**
- Dado que se elabora el documento de requerimientos,
- Cuando se revisa su contenido,
- Entonces lista al menos 15 requerimientos funcionales (RF01–RF15) y 15 no funcionales (RNF01–RNF15),
- Y cada requerimiento tiene código, tipo, nombre y descripción.

**CA-01.2 — Validación del documento**
- Dado que el documento de requerimientos está terminado,
- Cuando finaliza la fase de planificación,
- Entonces el documento es revisado y validado por el líder técnico,
- Y los requerimientos están alineados con el objetivo general del proyecto.

---

## HU-02 — Diseño de la Arquitectura Modular del Sistema
**Sprint:** 1 — Planificación y Arquitectura

> **Como** líder técnico,
> **quiero** diseñar la arquitectura del sistema en módulos independientes,
> **para** garantizar la mantenibilidad, escalabilidad y correcta integración entre componentes.

**Prioridad:** M (Must have)
**Módulos:** `docs/arquitectura/` (diagramas de componentes y casos de uso)
**Estado:** ✅ Completada

### Criterios de Aceptación

**CA-02.1 — Diagrama de componentes**
- Dado que se diseña la arquitectura,
- Cuando se documenta el diagrama de componentes,
- Entonces se identifican los 4 módulos principales: captura de video, detección de manos, clasificación y visualización.

**CA-02.2 — Casos de uso**
- Dado que se modela el comportamiento del sistema,
- Cuando se elabora el diagrama de casos de uso,
- Entonces incluye al menos 7 casos de uso identificados (UC-01 a UC-07).

**CA-02.3 — Tecnologías por módulo**
- Dado que se asigna la stack técnica,
- Cuando se revisa la arquitectura,
- Entonces especifica las tecnologías de cada módulo (OpenCV/WebRTC, MediaPipe, SVM, interfaz Streamlit),
- Y el diseño es aprobado por el equipo sin observaciones bloqueantes.

---

## HU-03 — Configuración del Entorno de Desarrollo y Repositorio
**Sprint:** 1 — Planificación y Arquitectura

> **Como** equipo de desarrollo,
> **quiero** tener el entorno de desarrollo configurado y el repositorio Git operativo,
> **para** trabajar de forma colaborativa y con control de versiones desde el inicio.

**Prioridad:** M (Must have)
**Módulos:** `requirements.txt`, `README.md`, repositorio Git
**Estado:** ✅ Completada

### Criterios de Aceptación

**CA-03.1 — Repositorio y ramas**
- Dado que se inicia el proyecto,
- Cuando se crea el repositorio en GitHub,
- Entonces existe con estructura de ramas definida (`main`, `develop`, `feature/*`).

**CA-03.2 — Dependencias fijadas**
- Dado que el proyecto requiere librerías externas,
- Cuando se revisa `requirements.txt`,
- Entonces lista todas las dependencias con versiones fijas.

**CA-03.3 — Verificación multi-equipo**
- Dado que el entorno está configurado,
- Cuando al menos 3 integrantes realizan un commit inicial,
- Entonces se verifica que el entorno funciona en sus equipos,
- Y el `README` describe propósito, instrucciones de instalación y estructura de carpetas.

**CA-03.4 — Versiones de referencia**
- Dado que se valida el entorno,
- Cuando se comprueban las versiones,
- Entonces el sistema funciona en Python 3.10+ con OpenCV 4.x, MediaPipe 0.10+ y Scikit-learn 1.x.

---

## HU-04 — Recolección Inicial del Dataset de Señas LSP
**Sprint:** 1 — Planificación, Dataset y Modelo ML

> **Como** ML Lead,
> **quiero** capturar un conjunto inicial de imágenes de señas LSP organizadas por letra,
> **para** poder iniciar el entrenamiento del modelo en el siguiente sprint.

**Prioridad:** M (Must have)
**Módulos:** `A.py` (script de recolección), `data/`
**Estado:** ✅ Completada

### Criterios de Aceptación

**CA-04.1 — Conjunto inicial de letras**
- Dado que se inicia la recolección,
- Cuando se capturan las señas,
- Entonces se obtienen imágenes de al menos 5 letras del abecedario LSP como conjunto inicial,
- Y cada letra tiene un mínimo de 100 imágenes en condiciones variadas de iluminación y posición.

**CA-04.2 — Organización del dataset**
- Dado que se capturan las imágenes,
- Cuando se almacenan,
- Entonces quedan organizadas en carpetas etiquetadas por seña (ej. `data/a/`, `data/b/`).

**CA-04.3 — Ejecución y depuración**
- Dado que el script `A.py` se ejecuta,
- Cuando se prueba en al menos 2 equipos distintos del equipo,
- Entonces corre sin errores,
- Y se descartan las imágenes con errores de detección de manos por MediaPipe.

---

## HU-05 — Construcción Completa del Dataset LSP
**Sprint:** 1 — Planificación, Dataset y Modelo ML

> **Como** responsable del desarrollo del modelo de IA,
> **quiero** construir un dataset representativo de señas de la Lengua de Señas Peruana,
> **para** entrenar el modelo de reconocimiento con un nivel adecuado de precisión y confiabilidad.

**Prioridad:** M (Must have)
**Módulos:** `data/`, scripts de captura
**Estado:** ✅ Completada

### Criterios de Aceptación

**CA-05.1 — Representatividad**
- Dado que se construye el dataset completo,
- Cuando se revisa su contenido,
- Entonces contiene imágenes de las letras implementadas del alfabeto LSP,
- Y cada categoría cuenta con un número suficiente de muestras para entrenamiento y validación.

**CA-05.2 — Diversidad de datos**
- Dado que se capturan las muestras,
- Cuando se consideran las condiciones de captura,
- Entonces se incluyen diferentes usuarios, condiciones de iluminación y fondos.

**CA-05.3 — Formato, etiquetado y depuración**
- Dado que el dataset está construido,
- Cuando se valida su calidad,
- Entonces las imágenes están en formatos compatibles, correctamente organizadas y etiquetadas por seña,
- Y se depuran las muestras con errores de captura o detección.

---

## HU-06 — Extracción de Landmarks y Preprocesamiento para Entrenamiento
**Sprint:** 1 — Planificación, Dataset y Modelo ML

> **Como** responsable del modelo de IA,
> **quiero** extraer y normalizar los puntos clave de las imágenes capturadas,
> **para** generar vectores de características adecuados para el entrenamiento del clasificador SVM.

**Prioridad:** M (Must have)
**Módulos:** script de extracción/preprocesamiento, `lsp_core.py`
**Estado:** ✅ Completada

### Criterios de Aceptación

**CA-06.1 — Extracción de landmarks**
- Dado que se procesan las imágenes del dataset,
- Cuando se ejecuta la extracción,
- Entonces se obtienen correctamente los puntos clave (landmarks) de la mano detectada.

**CA-06.2 — Normalización**
- Dado que se obtienen los landmarks,
- Cuando se transforman los datos,
- Entonces se normalizan en un formato compatible con el modelo de clasificación.

**CA-06.3 — Persistencia e integridad**
- Dado que se generan los vectores y etiquetas,
- Cuando finaliza el preprocesamiento,
- Entonces se almacenan correctamente para entrenamiento y validación,
- Y el sistema verifica la integridad de los datos, evitando registros incompletos o inconsistentes.

---

## HU-07 — Entrenamiento y Validación del Modelo SVM
**Sprint:** 1 — Planificación, Dataset y Modelo ML

> **Como** responsable del desarrollo del modelo de IA,
> **quiero** entrenar y validar el clasificador SVM con el dataset procesado,
> **para** garantizar un reconocimiento de señas preciso y funcional en tiempo real.

**Prioridad:** M (Must have)
**Módulos:** script de entrenamiento, modelo entrenado (`.pkl`), `qa/evaluate.py`
**Estado:** ✅ Completada

### Criterios de Aceptación

**CA-07.1 — División y entrenamiento**
- Dado que el dataset está procesado,
- Cuando se entrena el modelo,
- Entonces se divide en conjuntos de entrenamiento y prueba,
- Y el SVM se entrena con los vectores de características generados.

**CA-07.2 — Precisión mínima**
- Dado que el modelo está entrenado,
- Cuando se evalúa sobre el conjunto de prueba,
- Entonces alcanza una precisión mínima del 85% en las pruebas de clasificación,
- Y los resultados incluyen métricas de precisión, recall y F1-score.

**CA-07.3 — Estabilidad y persistencia**
- Dado que se valida el modelo,
- Cuando se aplican técnicas de validación,
- Entonces se verifica su estabilidad y consistencia,
- Y el modelo entrenado se almacena correctamente para su uso en reconocimiento en tiempo real.

---

## HU-08 — Captura de Video en Tiempo Real
**Sprint:** 2 — Aplicación Web, Calidad y Seguridad

> **Como** usuario del sistema,
> **quiero** que la aplicación active la cámara web al iniciar,
> **para** poder capturar mis señas sin realizar configuraciones manuales.

**Prioridad:** M (Must have)
**Módulos:** `lsp_video.py`
**Estado:** ✅ Implementada

### Criterios de Aceptación

**CA-08.1 — Inicio del stream**
- Dado que el usuario abre la aplicación y concede permiso de cámara,
- Cuando la página carga,
- Entonces el sistema inicia la cámara y muestra el flujo de video en tiempo real.

**CA-08.2 — Manejo de errores**
- Dado que la cámara no está disponible o presenta errores de acceso,
- Cuando se intenta iniciar el stream,
- Entonces el sistema muestra un mensaje descriptivo sin interrumpir la ejecución de la aplicación.

**CA-08.3 — Calidad y procesamiento de frames**
- Dado que el stream está activo,
- Cuando se capturan los fotogramas,
- Entonces se procesan correctamente antes de enviarse al módulo de detección,
- Y la resolución mínima de captura es 640×480 píxeles.

**CA-08.4 — Rendimiento mínimo de captura**
- Dado que el sistema corre en un equipo con Intel Core i5 / AMD Ryzen 5 y 8 GB RAM,
- Cuando se mide la captura,
- Entonces mantiene una tasa mínima de 20 FPS,
- Y se valida con pruebas unitarias que verifican la obtención de fotogramas consecutivos.

---

## HU-09 — Detección de Manos con MediaPipe
**Sprint:** 2 — Aplicación Web, Calidad y Seguridad

> **Como** usuario del sistema,
> **quiero** que la aplicación detecte automáticamente mi mano y sus puntos clave,
> **para** que el sistema pueda interpretar correctamente las señas realizadas.

**Prioridad:** M (Must have)
**Módulos:** `lsp_video.py`, `lsp_core.py` (MediaPipe)
**Estado:** ✅ Implementada

### Criterios de Aceptación

**CA-09.1 — Detección y landmarks**
- Dado que hay una mano en el área de captura,
- Cuando se procesa el frame,
- Entonces el sistema detecta la mano y obtiene los 21 puntos clave (landmarks).

**CA-09.2 — Visualización de la mano**
- Dado que la mano está detectada,
- Cuando se renderiza el video,
- Entonces se muestran las conexiones y puntos de referencia en tiempo real sobre el flujo.

**CA-09.3 — ROI y estabilidad**
- Dado que se detecta la mano,
- Cuando se prepara para clasificación,
- Entonces la región de interés (ROI) se delimita correctamente,
- Y la detección se mantiene estable en condiciones moderadas de iluminación (aulas u oficinas),
- Y se valida con pruebas unitarias que verifican la extracción de landmarks en imágenes de prueba.

---

## HU-10 — Reconocimiento y Traducción en Tiempo Real con Confianza Visible
**Sprint:** 2 — Aplicación Web, Calidad y Seguridad

> **Como** persona sorda o con dificultades auditivas,
> **quiero** que el sistema reconozca mis señas LSP en tiempo real y muestre su interpretación con el nivel de confianza,
> **para** poder comunicarme con personas que no conocen la LSP.

**Prioridad:** M (Must have)
**Módulos:** `app.py`, `lsp_video.py`, `lsp_core.py`, `lsp_ui.py`
**Estado:** ✅ Implementada

> *Historia consolidada: une la HU de traducción en tiempo real (features) con la HU de clasificación/reconocimiento (documentación), que describían la misma funcionalidad.*

### Criterios de Aceptación

**CA-10.1 — Carga del modelo**
- Dado que la aplicación inicia,
- Cuando se prepara el reconocimiento,
- Entonces carga correctamente el modelo de clasificación entrenado.

**CA-10.2 — Detección en tiempo real**
- Dado que el modelo está cargado y se reciben frames del stream WebRTC,
- Cuando se procesa la mano detectada,
- Entonces el panel de resultado se actualiza cada ≤ 0.4 segundos con la letra y confianza detectadas,
- Y el tiempo de respuesta total entre seña y visualización es inferior a 2 segundos en condiciones normales.

**CA-10.3 — Indicador de confianza**
- Dado que el modelo ha clasificado un frame,
- Cuando la confianza es ≥ 60%,
- Entonces el borde de la tarjeta es rojo (#E30613) y se muestra la letra en 120px.
- Y cuando la confianza es < 60% con una mano visible,
- Entonces el borde de la tarjeta cambia a amarillo (#f0a500) como indicador visual de ambigüedad.

**CA-10.4 — Rendimiento sostenido**
- Dado que el sistema está en ejecución durante 30 segundos continuos,
- Cuando se mide con `qa/fps_test.py`,
- Entonces el FPS promedio es ≥ 24,
- Y el flujo completo (captura → detección → clasificación → visualización) funciona de forma continua y estable en sesiones prolongadas.

**Tests de referencia:** `tests/test_modelo.py`, `tests/test_integracion.py`

---

## HU-11 — Historial de Señas y Construcción de Texto
**Sprint:** 2 — Aplicación Web, Calidad y Seguridad

> **Como** usuario con discapacidad auditiva,
> **quiero** que el sistema almacene las señas reconocidas en un historial de texto,
> **para** poder formar palabras y mensajes durante la interacción con el sistema.

**Prioridad:** S (Should have)
**Módulos:** `lsp_ui.py`, `lsp_core.py`
**Estado:** ✅ Implementada

### Criterios de Aceptación

**CA-11.1 — Acumulación por umbral**
- Dado que una seña se reconoce con confianza superior al umbral configurado,
- Cuando se procesa la predicción,
- Entonces se agrega automáticamente al historial de texto,
- Y el texto generado se muestra en tiempo real en el panel principal de traducción.

**CA-11.2 — Control del historial**
- Dado que el usuario interactúa con la interfaz,
- Cuando presiona el botón de limpiar,
- Entonces se reinicia el texto acumulado sin detener la captura de video,
- Y el usuario puede configurar el umbral mínimo de confianza para aceptar una predicción.

**CA-11.3 — Rendimiento del historial**
- Dado que el historial se actualiza,
- Cuando se acumulan señas,
- Entonces mantiene un registro limitado de las últimas señas para evitar sobrecarga visual,
- Y la actualización no afecta el rendimiento del reconocimiento en tiempo real.

---

## HU-12 — Integración Completa de Módulos del Sistema
**Sprint:** 2 — Aplicación Web, Calidad y Seguridad

> **Como** líder técnico del proyecto,
> **quiero** integrar los módulos de captura, detección, clasificación y visualización en un flujo unificado,
> **para** garantizar el funcionamiento integral y continuo del sistema de reconocimiento de señas.

**Prioridad:** M (Must have)
**Módulos:** `app.py` (orquestación de `lsp_video.py`, `lsp_core.py`, `lsp_ui.py`)
**Estado:** ✅ Implementada

### Criterios de Aceptación

**CA-12.1 — Coexistencia de módulos**
- Dado que los módulos están desarrollados,
- Cuando se ejecutan en un mismo entorno,
- Entonces funcionan sin conflictos de dependencias,
- Y el flujo de datos entre captura, detección, clasificación y visualización se ejecuta de forma continua y sin errores.

**CA-12.2 — Interfaz y controles**
- Dado que el sistema está integrado,
- Cuando el usuario interactúa,
- Entonces la interfaz actualiza el historial de señas reconocidas,
- Y los controles principales responden adecuadamente a las acciones del usuario.

**CA-12.3 — Estado y validación**
- Dado que el sistema está en ejecución,
- Cuando se observa la interfaz,
- Entonces muestra en todo momento el estado actual de funcionamiento,
- Y las pruebas de integración verifican el flujo desde la captura de video hasta el resultado final.

---

## HU-13 — Acceso Controlado mediante Clave de Sesión Académica
**Sprint:** 2 — Aplicación Web, Calidad y Seguridad

> **Como** administrador del sistema académico,
> **quiero** que el acceso a la aplicación requiera una clave de sesión,
> **para** demostrar controles de seguridad (DevSecOps) en el proyecto Capstone.

**Prioridad:** S (Should have)
**Módulos:** `lsp_auth.py`
**Estado:** ✅ Implementada

> **Decisión técnica — HMAC-SHA256 vs JWT:** el prompt original indicaba "autenticación JWT".
> Se optó por tokens HMAC-SHA256 propios (formato `timestamp.nonce.firma`) para evitar
> dependencias externas (PyJWT) en el entorno académico, mantener total control del
> formato del payload y simplificar la validación sin sacrificar seguridad. La biblioteca
> `hmac` + `hashlib` de la stdlib de Python provee garantías equivalentes para este alcance.

### Criterios de Aceptación

**CA-13.1 — Formulario de login antes del contenido**
- Dado que el usuario abre la aplicación sin sesión activa,
- Cuando la página carga,
- Entonces se muestra únicamente el formulario de acceso (sin revelar el contenido de la app).

**CA-13.2 — Autenticación exitosa**
- Dado que el usuario ingresa la clave correcta (configurada en `st.secrets` o demo "UPN2026"),
- Cuando presiona "Ingresar",
- Entonces se genera un token de sesión HMAC-SHA256 en `st.session_state["lsp_token"]`,
- Y se redirige al contenido completo de la aplicación.

**CA-13.3 — Rechazo de clave incorrecta**
- Dado que el usuario ingresa una clave incorrecta,
- Cuando presiona "Ingresar",
- Entonces aparece el mensaje "Clave incorrecta. Intenta nuevamente.",
- Y no se expone ninguna traza de excepción ni información técnica del sistema.

**CA-13.4 — Expiración de sesión**
- Dado que el token fue generado hace más de 60 minutos,
- Cuando se verifica con `lsp_auth.verificar_token()`,
- Entonces retorna False y el usuario debe autenticarse nuevamente.

**CA-13.5 — Resistencia a manipulación**
- Dado que un token es generado correctamente,
- Cuando se modifica cualquier parte del payload (timestamp, nonce o firma),
- Entonces `verificar_token()` retorna False.

**CA-13.6 — Sanitización de inputs en el formulario de acceso**
- Dado que un usuario ingresa caracteres especiales, HTML o intentos de XSS en el campo de clave,
- Cuando presiona "Ingresar",
- Entonces el sistema los trata como texto plano sin interpolarlos en el HTML de respuesta,
- Y no se expone ningún carácter especial en el mensaje de error ni en el DOM de la página.

**Tests de referencia:** `tests/test_auth.py` (14 tests)

---

## HU-14 — Registro Anónimo de Accesos (Auditoría)
**Sprint:** 2 — Aplicación Web, Calidad y Seguridad

> **Como** responsable académico del proyecto,
> **quiero** que el sistema registre los eventos de acceso sin almacenar datos personales,
> **para** cumplir con GDPR Artículo 25 (privacidad por diseño) y demostrar trazabilidad.

**Prioridad:** S (Should have)
**Módulos:** `lsp_audit.py`
**Estado:** ✅ Implementada

### Criterios de Aceptación

**CA-14.1 — Registro de eventos**
- Dado que ocurre un evento del sistema (LOGIN_OK, LOGIN_FAIL, PAGINA_VISITADA, etc.),
- Cuando se llama a `lsp_audit.registrar_acceso()`,
- Entonces se escribe una línea JSON en `audit_log.jsonl` con campos: `ts`, `evento`, `sesion`, `detalle`.

**CA-14.2 — Anonimato del ID de sesión**
- Dado que se registra cualquier evento,
- Cuando se lee el campo `sesion`,
- Entonces contiene exactamente 8 caracteres hexadecimales (SHA-256[:8] del token),
- Y no contiene IP, user-agent, nombre de usuario ni ningún dato de identificación personal.

**CA-14.3 — Mantenimiento del log**
- Dado que el log contiene entradas con más de 7 días de antigüedad,
- Cuando se ejecuta `lsp_audit.purgar_log_antiguo(dias=7)`,
- Entonces las entradas antiguas son eliminadas y las recientes se conservan.

**CA-14.4 — Log efímero en Streamlit Cloud**
- Dado que la app se ejecuta en Streamlit Cloud,
- Cuando el servidor reinicia (filesystem efímero),
- Entonces el log se pierde correctamente — comportamiento esperado (documentado en `SEGURIDAD.md`).

**Tests de referencia:** `tests/test_audit.py` (9 tests)

---

## HU-15 — Interfaz Accesible para Usuarios con Discapacidad
**Sprint:** 3 — Ética, Accesibilidad y Despliegue

> **Como** usuario con discapacidad visual o motora,
> **quiero** que la interfaz sea compatible con tecnologías de asistencia,
> **para** poder usar el traductor con un lector de pantalla o navegación por teclado.

**Prioridad:** S (Should have)
**Módulos:** `lsp_ui.py`
**Estado:** ✅ Implementada

### Criterios de Aceptación

**CA-15.1 — Anuncio automático de letras (aria-live)**
- Dado que el usuario utiliza un lector de pantalla (NVDA, VoiceOver),
- Cuando el modelo detecta una nueva letra,
- Entonces el lector la anuncia sin que el usuario tenga que navegar al elemento
- (gracias a `role="status"` y `aria-live="polite"` en el div `.result-letter`).

**CA-15.2 — Contraste de colores (WCAG 1.4.3 — Nivel AA)**
- Dado que se inspeccionan los colores del CSS,
- Cuando se verifica el contraste de todo el texto visible,
- Entonces el ratio mínimo es ≥ 4.5:1 para texto normal
- (correcciones: `#888`/`#777`/`#aaa` → `#6b6b6b`/`#767676`).

**CA-15.3 — Enlace de saltar navegación (WCAG 2.4.1 — Nivel A)**
- Dado que el usuario presiona Tab al cargar la página,
- Cuando recibe el foco el primer elemento,
- Entonces aparece visualmente el enlace "Saltar al contenido" con fondo rojo.

**CA-15.4 — Roles semánticos en regiones**
- Dado que se inspecciona el HTML generado,
- Cuando se buscan los elementos topbar y footer,
- Entonces se encuentran con `role="banner"` y `role="contentinfo"` respectivamente.

**CA-15.5 — Barra de confianza accesible**
- Dado que se inspecciona el HTML de la barra de confianza,
- Cuando se lee el elemento `.bar-bg`,
- Entonces tiene `role="progressbar"`, `aria-valuenow`, `aria-valuemin="0"`, `aria-valuemax="100"`.

---

## HU-16 — Explicación Transparente del Sistema de IA
**Sprint:** 3 — Ética, Accesibilidad y Despliegue

> **Como** usuario general o evaluador académico,
> **quiero** entender cómo la IA toma sus decisiones de clasificación,
> **para** poder interpretar los resultados y confiar en el sistema.

**Prioridad:** C (Could have)
**Módulos:** `lsp_ui.render_pipeline_explicado()`
**Estado:** ✅ Implementada

### Criterios de Aceptación

**CA-16.1 — Diagrama de pipeline visible**
- Dado que el usuario abre la aplicación,
- Cuando hace scroll hacia abajo,
- Entonces ve el diagrama con las 5 etapas: Cámara → MediaPipe → Landmarks → SVM → Predicción.

**CA-16.2 — Expander de explicabilidad**
- Dado que el usuario hace clic en "¿Cómo decide la IA?",
- Cuando el expander se despliega,
- Entonces lee una explicación en lenguaje accesible sobre:
  - Qué son los 21 landmarks y los 42 números
  - Cómo el SVM usa hiperplanos para clasificar
  - Qué significa la "confianza" (probabilidad de Platt)
  - Las limitaciones honestas del modelo (letras similares, imbalance de clases)

**CA-16.3 — Indicador de baja confianza**
- Dado que la confianza de la predicción es < 60% con una mano visible,
- Cuando se renderiza el panel de resultado,
- Entonces el borde de la tarjeta cambia a amarillo (#f0a500) como alerta visual.

---

## HU-17 — Dashboard de Métricas de Calidad
**Sprint:** 2 — Aplicación Web, Calidad y Seguridad

> **Como** docente o evaluador del Capstone,
> **quiero** visualizar las métricas de calidad del sistema en una página dedicada,
> **para** verificar que el sistema cumple con los estándares académicos de ISO/Scrum.

**Prioridad:** M (Must have)
**Módulos:** `pages/1_Metricas_QA.py`, `qa/`
**Estado:** ✅ Implementada

### Criterios de Aceptación

**CA-17.1 — Métricas del modelo visibles**
- Dado que el usuario navega a la página "Métricas QA",
- Cuando la página carga,
- Entonces ve tablas con: Accuracy, Precision, Recall, F1 (del último `qa/evaluate.py`).

**CA-17.2 — Métricas de rendimiento**
- Dado que se han ejecutado `qa/benchmark.py` y `qa/fps_test.py`,
- Cuando se visualiza el dashboard,
- Entonces aparecen las latencias por etapa y los FPS sostenidos.

**CA-17.3 — Log de auditoría visible**
- Dado que el usuario está autenticado y ha interactuado con la app,
- Cuando visita la página de Métricas QA,
- Entonces ve las últimas 20 entradas del `audit_log.jsonl` de la sesión actual.

---

## HU-18 — Pruebas Unitarias Automatizadas del Sistema
**Sprint:** 2 — Aplicación Web, Calidad y Seguridad

> **Como** responsable de calidad del proyecto,
> **quiero** ejecutar pruebas unitarias sobre los diferentes módulos del sistema,
> **para** verificar que cada componente funcione correctamente de forma independiente antes de la integración final.

**Prioridad:** M (Must have)
**Módulos:** `tests/`
**Estado:** ✅ Implementada

### Criterios de Aceptación

**CA-18.1 — Cobertura por módulo**
- Dado que se desarrolla la suite de pruebas,
- Cuando se revisan los tests,
- Entonces existen pruebas unitarias para los módulos principales: captura de video, detección de manos, clasificación y visualización de resultados.

**CA-18.2 — Detección temprana de errores**
- Dado que las pruebas están implementadas,
- Cuando se ejecutan antes del despliegue,
- Entonces permiten identificar errores funcionales,
- Y alcanzan un nivel de cobertura adecuado para los componentes críticos.

**CA-18.3 — Registro y gate de calidad**
- Dado que las pruebas se ejecutan,
- Cuando se genera la versión final,
- Entonces los resultados se registran y documentan,
- Y todas las pruebas críticas deben ejecutarse satisfactoriamente antes de liberar.

---

## HU-19 — Pruebas de Aceptación con Usuarios Finales
**Sprint:** 3 — Ética, Accesibilidad y Despliegue

> **Como** responsable de calidad del proyecto,
> **quiero** realizar pruebas de aceptación con usuarios potenciales del sistema,
> **para** validar la usabilidad, accesibilidad y funcionamiento del reconocimiento de señas en condiciones reales de uso.

**Prioridad:** S (Should have)
**Módulos:** documentación de QA / evidencias
**Estado:** ⏳ Por confirmar

### Criterios de Aceptación

**CA-19.1 — Participantes representativos**
- Dado que se planifican las pruebas,
- Cuando se realizan,
- Entonces participan usuarios oyentes y personas con discapacidad auditiva,
- Y evalúan facilidad de uso, claridad visual, accesibilidad y tiempo de respuesta.

**CA-19.2 — Instrumento de satisfacción**
- Dado que los participantes usan el prototipo,
- Cuando finaliza cada sesión,
- Entonces se aplica un cuestionario de satisfacción,
- Y la mayoría evalúa el sistema de forma satisfactoria en usabilidad y experiencia.

**CA-19.3 — Registro de observaciones**
- Dado que se realizan las sesiones de validación,
- Cuando se recogen los resultados,
- Entonces las observaciones y sugerencias se registran y documentan para futuras mejoras,
- Y el sistema demuestra un nivel adecuado de reconocimiento durante la validación.

---

## HU-20 — Validación de Privacidad y Protección de Datos
**Sprint:** 3 — Ética, Accesibilidad y Despliegue

> **Como** equipo de desarrollo,
> **quiero** verificar que el sistema proteja adecuadamente la información procesada durante la interacción,
> **para** garantizar el cumplimiento de los principios de privacidad y protección de datos del proyecto.

**Prioridad:** S (Should have)
**Módulos:** `SEGURIDAD.md`, `lsp_audit.py`
**Estado:** ✅ Implementada

### Criterios de Aceptación

**CA-20.1 — No persistencia de imágenes**
- Dado que el sistema procesa video y señas,
- Cuando se ejecuta el reconocimiento,
- Entonces las imágenes y datos procesados no se almacenan automáticamente,
- Y no se genera transmisión innecesaria de información hacia redes externas.

**CA-20.2 — Documentación de privacidad**
- Dado que se documenta el sistema,
- Cuando se revisa la documentación técnica,
- Entonces incluye una sección de consideraciones de privacidad y protección de datos implementadas.

**CA-20.3 — Verificación en validación**
- Dado que se realizan las pruebas de validación,
- Cuando participan usuarios,
- Entonces manifiestan conformidad respecto al manejo de la información,
- Y las medidas de privacidad implementadas se verifican durante las pruebas.

---

## HU-21 — Despliegue del Sistema
**Sprint:** 3 — Ética, Accesibilidad y Despliegue

> **Como** equipo de desarrollo,
> **quiero** desplegar el sistema para usuarios finales,
> **para** facilitar su distribución y uso sin requerir configuraciones complejas.

**Prioridad:** M (Must have)
**Módulos:** configuración de despliegue (Streamlit Cloud), `requirements.txt`
**Estado:** 🔄 En progreso / Por confirmar

> ⚠️ **Discrepancia a resolver:** la documentación original (Sprint 4) describía el despliegue como un
> **ejecutable portable para Windows** (sin instalar Python). Sin embargo, el sistema implementado es una
> **aplicación web Streamlit** (Streamlit Cloud, WebRTC, `st.secrets`, `pages/`). Los criterios siguientes
> reflejan el despliegue web real; confirma con el equipo cuál es el objetivo vigente (o si ambos aplican).

### Criterios de Aceptación

**CA-21.1 — Disponibilidad de la aplicación**
- Dado que el sistema está terminado,
- Cuando se despliega,
- Entonces queda accesible para usuarios finales sin instalación local compleja,
- Y el modelo de reconocimiento entrenado está integrado correctamente en el despliegue.

**CA-21.2 — Arranque y cámara**
- Dado que un usuario accede a la aplicación desplegada,
- Cuando la inicia,
- Entonces el sistema arranca correctamente y activa la cámara web en un tiempo adecuado.

**CA-21.3 — Validación y evidencias**
- Dado que el despliegue está disponible,
- Cuando se prueba en equipos distintos al de desarrollo,
- Entonces funciona satisfactoriamente,
- Y el proceso de despliegue y validación se documenta con evidencias y capturas.

**CA-21.4 — Manual de Usuario Preliminar**
- Dado que el sistema está desplegado y validado,
- Cuando se elabora la documentación de entrega,
- Entonces existe un Manual de Usuario Preliminar que describe: inicio de sesión, uso del traductor, interpretación del indicador de confianza, borrado del historial y acceso al dashboard de métricas,
- Y existe un Registro de Lecciones Aprendidas que documenta decisiones técnicas, obstáculos enfrentados y mejoras identificadas durante el proyecto.

---

## HU-22 — Pruebas de Rendimiento, Carga y Estrés
**Sprint:** 2 — Aplicación Web, Calidad y Seguridad

> **Como** responsable de calidad del proyecto,
> **quiero** ejecutar pruebas de rendimiento, carga y estrés sobre el sistema,
> **para** asegurar su estabilidad y capacidad de respuesta bajo condiciones de uso intensivo y sostenido.

**Prioridad:** S (Should have)
**Módulos:** `qa/benchmark.py`, `qa/fps_test.py`
**Estado:** ✅ Implementada

### Criterios de Aceptación

**CA-22.1 — Benchmark por etapa del pipeline**
- Dado que el sistema está en ejecución,
- Cuando se ejecuta `qa/benchmark.py`,
- Entonces se miden y reportan las latencias individuales de cada etapa: captura, detección MediaPipe, extracción de landmarks, clasificación SVM y renderizado,
- Y ninguna etapa supera 200 ms de latencia promedio en hardware de referencia (Intel Core i5 / AMD Ryzen 5, 8 GB RAM).

**CA-22.2 — FPS sostenido bajo carga (prueba de resistencia)**
- Dado que el sistema está activo y procesando señas de forma continua,
- Cuando se ejecuta `qa/fps_test.py` durante una sesión de 60 segundos,
- Entonces el FPS promedio se mantiene ≥ 24,
- Y el FPS mínimo durante la sesión no desciende por debajo de 15 (sin caídas abruptas).

**CA-22.3 — Estabilidad en sesiones prolongadas (prueba de estrés)**
- Dado que el sistema está en ejecución continua,
- Cuando se ejecuta una sesión de estrés de 300 segundos (5 minutos) con captura activa,
- Entonces la memoria RAM utilizada no crece más de 50 MB respecto al estado inicial (sin memory leaks),
- Y el sistema no lanza excepciones no controladas ni se interrumpe.

**CA-22.4 — Degradación controlada ante señas ambiguas**
- Dado que se presentan señas con baja calidad (mano parcialmente visible, iluminación deficiente),
- Cuando el clasificador no supera el umbral de confianza del 60%,
- Entonces el sistema muestra el indicador amarillo de baja confianza en lugar de una predicción falsa,
- Y no se producen errores en el pipeline de procesamiento.

---

## Resumen de Cobertura de Tests

Leyenda de estado: ✅ Verificado · 🔄 En progreso · ⏳ Por confirmar
Tipo de verificación: **Automatizada** (`pytest`) · **QA** (scripts de medición) · **Manual** (checklist/revisión)

| HU | Historia | Verificación | Tipo | Estado |
|---|---|---|---|---|
| HU-01 | Definición de requerimientos y alcance | Revisión y validación del líder técnico | Manual | ✅ |
| HU-02 | Arquitectura modular | Revisión de diagramas (componentes, casos de uso) en Sprint Review | Manual | ✅ |
| HU-03 | Entorno de desarrollo y repositorio | Verificación de `requirements.txt` y commits en ≥3 equipos | Manual | ✅ |
| HU-04 | Recolección inicial del dataset | Inspección del dataset y ejecución de `A.py` en ≥2 equipos | Manual | ✅ |
| HU-05 | Dataset completo LSP | Inspección, etiquetado y depuración del dataset | Manual | ✅ |
| HU-06 | Extracción de landmarks y preprocesamiento | Validación de integridad de vectores y etiquetas | Manual | ✅ |
| HU-07 | Entrenamiento y validación del SVM | `qa/evaluate.py` (accuracy, precision, recall, F1 ≥ 85%) | QA | ✅ |
| HU-08 | Captura de video en tiempo real | `tests/test_integracion.py` (frames consecutivos) | Automatizada | ✅ |
| HU-09 | Detección de manos con MediaPipe | `tests/test_modelo.py` (extracción de los 21 landmarks) | Automatizada | ✅ |
| HU-10 | Reconocimiento y traducción en tiempo real | `tests/test_modelo.py` (5), `tests/test_integracion.py` (3), `qa/fps_test.py` (FPS ≥ 24) | Automatizada + QA | ✅ |
| HU-11 | Historial de señas y construcción de texto | `tests/test_integracion.py` + revisión funcional | Automatizada + Manual | ✅ |
| HU-12 | Integración completa de módulos | `tests/test_integracion.py` (flujo extremo a extremo) | Automatizada | ✅ |
| HU-13 | Acceso por clave de sesión | `tests/test_auth.py` (14 tests: login, token HMAC, expiración, manipulación, sanitización XSS) | Automatizada | ✅ 14/14 |
| HU-14 | Registro anónimo de accesos (auditoría) | `tests/test_audit.py` (9 tests: anonimato, purga, formato JSONL) | Automatizada | ✅ 9/9 |
| HU-15 | Interfaz accesible (WCAG) | Checklist manual WCAG (contraste, aria-live, roles, skip-link) | Manual | ✅ |
| HU-16 | Explicación transparente de la IA | Checklist manual de UI (pipeline, expander, baja confianza) | Manual | ✅ |
| HU-17 | Dashboard de métricas QA | `qa/evaluate.py`, `qa/benchmark.py`, `qa/fps_test.py` | QA | ✅ |
| HU-18 | Pruebas unitarias automatizadas | Suite completa `tests/` (gate de calidad pre-release) | Automatizada | ✅ |
| HU-19 | Pruebas de aceptación con usuarios | Sesiones con usuarios oyentes y sordos + cuestionario de satisfacción | Manual | ⏳ |
| HU-20 | Validación de privacidad y protección de datos | Revisión de `SEGURIDAD.md` + verificación en pruebas | Manual | ✅ |
| HU-21 | Despliegue del sistema | Evidencias de despliegue, pruebas en equipos distintos y Manual de Usuario Preliminar | Manual | 🔄 |
| HU-22 | Pruebas de rendimiento, carga y estrés | `qa/benchmark.py` (latencias por etapa), `qa/fps_test.py` (FPS ≥ 24 en 60 s), sesión de estrés 300 s | QA | ✅ |

### Totales

| Suite | Archivo | N.º de tests | Resultado |
|---|---|---|---|
| Modelo | `tests/test_modelo.py` | 5 | ✅ Pasan |
| Integración | `tests/test_integracion.py` | 3 | ✅ Pasan |
| Autenticación | `tests/test_auth.py` | 14 | ✅ Pasan |
| Auditoría | `tests/test_audit.py` | 9 | ✅ Pasan |
| **Total automatizadas** | — | **31** | **✅ 31/31** |
| QA scripts | `qa/benchmark.py`, `qa/fps_test.py` | 3 métricas | ✅ HU-22 |

**Entorno de referencia:** Python 3.12 + MediaPipe 0.10.21.
**Scripts de QA (no unitarios):** `qa/evaluate.py`, `qa/benchmark.py`, `qa/fps_test.py` — generan reportes de métricas, latencias y FPS.

> **Nota:** la asignación de tests a las historias de pipeline (HU-08 a HU-12) es inferida a partir de los nombres de archivo conocidos; confírmala contra el contenido real de tu carpeta `tests/`.