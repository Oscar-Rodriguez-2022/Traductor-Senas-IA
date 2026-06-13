# Registro de Lecciones Aprendidas — LSP Vision AI
## Universidad Privada del Norte · Capstone Project Sistemas 2026
### Autor: Rodriguez Chacara, Oscar Daniel · Versión 2.0 · 2026-06-13

> **Estado: CIERRE DE PROYECTO** — 22 Historias de Usuario completadas · 137 SP totales.
> 4 sprints regulares + 1 Sprint de Reingeniería = retrospectiva técnica integral.

Este documento registra las decisiones técnicas tomadas durante el desarrollo,
los obstáculos enfrentados y las mejoras identificadas en cada Sprint.
Sirve como referencia para futuros proyectos de visión artificial y sistemas web con IA.

---

## Sprint 1 — Planificación, Dataset y Modelo ML

### Decisiones técnicas

#### DT-01: Landmarks en lugar de píxeles en bruto para el clasificador
**Decisión:** usar los 21 puntos clave (landmarks) de MediaPipe como vector de entrada al SVM en lugar de pasar imágenes completas.
**Motivación:** los modelos que procesan matrices de píxeles (CNN, SVM sobre imagen) requerían tiempos de entrenamiento de 30+ minutos en las laptops del equipo, con baja generalización ante cambios de iluminación o fondo.
**Resultado:** el entrenamiento se redujo a menos de 3 segundos y la accuracy en validación alcanzó 92.9%, con mejor resistencia a variaciones de fondo porque los landmarks son independientes del color del pixel.
**Lección:** la reducción dimensional geométrica (pasar de millones de píxeles a 42 coordenadas) es una estrategia efectiva para proyectos con hardware limitado y alta variabilidad visual.

#### DT-02: Padding de 30 px en el recorte de la ROI
**Decisión:** agregar 30 píxeles de margen al recuadro de recorte automático generado por MediaPipe.
**Motivación:** durante las pruebas iniciales, los dedos en posición extendida quedaban cortados en los bordes del ROI, causando que MediaPipe perdiera los landmarks de las puntas.
**Resultado:** eliminación de fallos de detección en señas con dedos extendidos (A, B, C, D).
**Lección:** los algoritmos de detección de bounding box suelen ser conservadores; siempre agregar margen de seguridad en aplicaciones de reconocimiento de gestos.

#### DT-03: Umbral mínimo de confianza del 70% en captura del dataset
**Decisión:** el script `scripts/capturar_dataset.py` descarta automáticamente frames donde MediaPipe reporta confianza de detección < 0.7.
**Motivación:** sin este filtro, el dataset contenía imágenes con manos parcialmente detectadas que introducían ruido en el entrenamiento.
**Resultado:** dataset más limpio y reducción del tiempo de depuración manual.
**Lección:** la calidad del dataset tiene más impacto en el rendimiento final que los hiperparámetros del modelo. Invertir tiempo en curation del dataset es siempre rentable.

### Obstáculos

#### OB-01: Desequilibrio de clases en el dataset inicial
**Problema:** las primeras letras capturadas (A, B, C) tenían 150+ muestras, mientras que letras capturadas al final (N, O) tenían menos de 20. Esto causó que la validación cruzada K-Fold fallara (`k > n_samples` para algunas clases).
**Solución:** se implementó el sistema de captura colaborativa por CSV (`scripts/entrenar_desde_csv.py`) para que los compañeros de equipo pudieran contribuir muestras de las letras faltantes sin instalar el entorno completo.
**Impacto en tiempo:** +3 días al Sprint 1 para desarrollar y documentar el sistema colaborativo.

#### OB-02: Incompatibilidad entre Python 3.13 y MediaPipe 0.10
**Problema:** al configurar el entorno con Python 3.13 (versión más reciente en ese momento), MediaPipe lanzaba errores de importación por módulos binarios incompatibles.
**Solución:** downgrade a Python 3.12, que es la versión LTS compatible con MediaPipe 0.10.21 y scikit-learn 1.x.
**Lección:** en proyectos con dependencias de visión artificial (OpenCV, MediaPipe), fijar la versión de Python en `requirements.txt` o `pyproject.toml` desde el primer día para evitar divergencias entre entornos del equipo.

---

## Sprint 2 — Aplicación Web, Calidad y Seguridad

### Decisiones técnicas

#### DT-04: HMAC-SHA256 propio en lugar de JWT
**Decisión:** implementar tokens de sesión con firma HMAC-SHA256 (`timestamp.nonce.firma`) usando solo la stdlib de Python, en lugar de una librería JWT.
**Motivación:** el entorno académico con instalación simplificada desaconsejaba agregar dependencias externas (PyJWT). Además, el formato JWT es más complejo de auditar sin herramientas externas.
**Resultado:** `lsp_auth.py` con 0 dependencias externas, 6 criterios de aceptación cubiertos y 14 tests automatizados.
**Lección:** para proyectos académicos o internos con requisitos de seguridad moderados, las primitivas criptográficas de la stdlib son suficientes y evitan la superficie de ataque de dependencias de terceros.

#### DT-05: Auditoría con IDs de sesión anónimos (SHA-256[:8])
**Decisión:** el log de auditoría (`audit_log.jsonl`) registra solo los primeros 8 caracteres del hash SHA-256 del token, nunca la IP ni el user-agent.
**Motivación:** cumplimiento con GDPR Artículo 25 (privacidad por diseño). El proyecto procesa imágenes de usuarios reales y era importante demostrar que no se almacenan datos identificables.
**Resultado:** auditoría funcional para trazabilidad académica sin ningún dato personal.
**Lección:** diseñar la privacidad desde el día uno es más eficiente que agregar controles de privacidad al final. La anonimización a nivel de ID de sesión cuesta poco y elimina riesgos legales.

#### DT-06: TDD estricto para módulos de seguridad
**Decisión:** los módulos `lsp_auth.py` y `lsp_audit.py` se desarrollaron con TDD estricto: primero se escribieron los tests en estado FAIL (commit separado), luego se implementó el código hasta que todos pasaron.
**Motivación:** los módulos de autenticación y auditoría son los de mayor criticidad en el sistema; un error en ellos compromete tanto la seguridad como la trazabilidad del proyecto.
**Resultado:** 14 + 9 = 23 tests automatizados con cobertura del 100% de los casos especificados en los criterios de aceptación.
**Lección:** TDD no solo verifica la corrección del código; también obliga a definir el comportamiento esperado antes de escribir una línea de lógica, lo que clarifica los requisitos y reduce la reescritura.

### Obstáculos

#### OB-03: Latencia inicial del pipeline por resolución de captura
**Problema:** en las primeras versiones, el pipeline procesaba frames a resolución completa (1280×720), lo que causaba latencias de 80–120 ms solo en el paso de MediaPipe.
**Solución:** reducir la resolución de procesamiento a 640×480 y activar el modo rápido de MediaPipe (`model_complexity=0`). La resolución de visualización se mantiene alta para la UX.
**Resultado:** latencia del paso MediaPipe reducida a ~15 ms. Pipeline completo: ~18 ms/predicción.
**Lección:** en sistemas de visión en tiempo real, separar la resolución de procesamiento de la resolución de visualización es una optimización de alto impacto y bajo costo de implementación.

#### OB-04: WebRTC y restricciones de cámara en Streamlit
**Problema:** el acceso a la cámara web en Streamlit requiere `streamlit-webrtc`, que tiene comportamiento diferente en localhost versus Streamlit Cloud (servidores STUN/TURN).
**Solución:** documentar la configuración de ICE servers en `TUTORIAL_DESPLIEGUE_WEB.md` y testear en Streamlit Cloud antes de considerar la HU-21 como completada.
**Lección:** las dependencias que dependen de infraestructura de red (WebRTC) deben validarse en el entorno de producción desde las primeras iteraciones, no solo en localhost.

---

## Sprint 3 — Ética, Accesibilidad y Despliegue

### Decisiones técnicas

#### DT-07: Accesibilidad implementada en la capa de UI, no en CSS externo
**Decisión:** los atributos ARIA (`aria-live`, `role="progressbar"`, `aria-valuenow`) se inyectan mediante `st.markdown(..., unsafe_allow_html=True)` dentro de `lsp_ui.py`, no a través de CSS externo.
**Motivación:** Streamlit no expone acceso directo al DOM HTML; la única vía de agregar atributos semánticos es via inyección de HTML. Se decidió centralizar toda la lógica de accesibilidad en `lsp_ui.py` para facilitar auditorías futuras.
**Resultado:** cumplimiento WCAG 2.1 Nivel AA verificado con Chrome DevTools Accessibility.
**Lección:** los frameworks de alto nivel como Streamlit simplifican el desarrollo pero limitan el control sobre el HTML generado. Es importante verificar tempranamente si el framework permite cumplir con estándares de accesibilidad, no en el último sprint.

#### DT-08: Explicabilidad de IA como sección obligatoria de la UI
**Decisión:** incluir una sección permanente en la interfaz que explica el pipeline del modelo (diagrama Cámara → MediaPipe → Landmarks → SVM → Predicción) y un expander *"¿Cómo decide la IA?"* con explicación en lenguaje accesible.
**Motivación:** los principios de IA ética exigen que los usuarios entiendan cómo el sistema toma decisiones. En el contexto de personas sordas usando la aplicación, la transparencia del sistema aumenta la confianza y la correcta interpretación de los resultados.
**Resultado:** HU-16 completada, con explicación de landmarks, SVM, probabilidad de Platt y limitaciones honestas del modelo.
**Lección:** la explicabilidad no es un extra opcional; es un requisito de diseño que debe planificarse desde la arquitectura de la UI, no añadirse a último momento.

### Obstáculos

#### OB-05: Contrastes de color insuficientes en el diseño inicial
**Problema:** los colores `#888`, `#777` y `#aaa` usados para texto secundario en la UI original no cumplían el ratio mínimo de contraste 4.5:1 exigido por WCAG 1.4.3.
**Solución:** reemplazar con `#6b6b6b`, `#767676` y equivalentes que sí cumplen el estándar. Verificación con Chrome DevTools → Accessibility.
**Impacto:** 1 día adicional de ajustes de CSS en `lsp_ui.py`.
**Lección:** usar un verificador de contraste WCAG desde el primer prototipo de la interfaz ahorra iteraciones de corrección en sprints finales.

#### OB-06: Coordinación de participantes para las pruebas UAT
**Problema:** la HU-19 requería sesiones con usuarios oyentes y personas con discapacidad auditiva. Coordinar la disponibilidad de participantes sordos fue más difícil de lo anticipado porque implicó contactar a organizaciones externas al equipo.
**Solución:** dividir las pruebas en dos fases — primero con compañeros oyentes de la facultad (verificación de usabilidad general) y luego con participantes sordos (verificación de relevancia y accesibilidad).
**Lección:** en proyectos orientados a comunidades específicas (personas sordas, adultos mayores, etc.), planificar el reclutamiento de participantes para pruebas desde el Sprint 1, no dejarlo para el último sprint.

---

## Sprint 4 — Trazabilidad, Calidad y Cierre de Capstone

### Decisiones técnicas

#### DT-09: Separación de artefactos de arquitectura en `docs/`
**Decisión:** crear la carpeta `docs/` con `requerimientos.md` (15 RF + 15 RNF), `docs/arquitectura/COMPONENTES.md` (diagramas Mermaid) y `docs/arquitectura/MODELO_DATOS.md` (modelo de datos incremental).
**Motivación:** las HU-01 y HU-02 referenciaban `docs/requerimientos.md` y `docs/arquitectura/` que no existían. Los evaluadores y futuros integrantes necesitan encontrar la documentación en rutas predecibles.
**Resultado:** trazabilidad completa CA-01.1 (15 RF + 15 RNF), CA-02.1/02.2/02.3 (diagramas de componentes y casos de uso) verificables mediante links en `HISTORIAS_USUARIO.md`.
**Lección:** los artefactos de documentación referenciados en las HUs deben existir como archivos reales desde el Sprint en que se crea la HU. Un link roto es evidencia de deuda técnica de documentación.

#### DT-10: Reemplazo de tests-stub por assertions reales (XP — Honestidad)
**Decisión:** reescribir los 18 tests en `test_sistema.py` que usaban `assertTrue(True)` y variables hardcoded (`precision_obtenida = 0.87; assertGreaterEqual(precision_obtenida, 0.85)`).
**Motivación:** los tests que siempre pasan sin ejecutar código real violan el principio XP de *feedback honesto*. Proporcionan falsa confianza al equipo y al evaluador.
**Resultado:** 15 de los 18 tests ahora llaman a `lsp_core`, `lsp_auth` o `sklearn` directamente. Los 3 tests dependientes de hardware físico (cámara) llevan `@pytest.mark.skip` con justificación explícita.
**Lección:** en revisiones de código, buscar activamente el patrón `assert True` o variables locales hardcodeadas como evidencia de tests stub. Un test stub que siempre pasa es peor que no tener test: crea una falsa sensación de cobertura.

#### DT-11: Rate limiting como control de seguridad en capa de aplicación
**Decisión:** añadir protección anti-fuerza-bruta en `lsp_auth.py`: bloqueo automático tras 5 intentos fallidos consecutivos durante 5 minutos, con reset automático en login exitoso y en expiración del período.
**Motivación:** la ausencia de rate limiting dejaba abierto un vector de ataque de diccionario contra la clave académica, que es intrínsecamente menos compleja que una clave de producción.
**Resultado:** `esta_bloqueado()`, `_registrar_fallo()` y `_resetear_intentos()` añadidos con estado de módulo thread-safe. 5 tests TDD en `tests/test_seguridad.py::TestRateLimiting`.
**Lección:** los controles de seguridad de nivel de aplicación (rate limiting, lockout) son tan importantes como los criptográficos (HMAC). Ambos deben estar en el DoD desde el primer sprint que incluya autenticación.

#### DT-12: Verificación de integridad del modelo PKL como control de cadena de suministro
**Decisión:** añadir `calcular_hash_modelo()` y `verificar_integridad_modelo()` en `lsp_core.py` para detectar manipulación del archivo `modelo.pkl` antes de cargarlo.
**Motivación:** la deserialización de pickles arbitrarios es una vulnerabilidad conocida (OWASP CWE-502). El modelo se genera localmente pero podría ser reemplazado por un archivo malicioso en un entorno compartido o comprometido.
**Resultado:** función SHA-256 en bloques de 64 KB disponible para verificación manual y automatizada. Documentada en `SEGURIDAD.md` v2.0.
**Lección:** los archivos binarios generados durante el desarrollo (modelos, librerías) son parte de la cadena de suministro del software. Calcular y distribuir sus hashes es una práctica de DevSecOps de bajo costo y alto impacto.

#### DT-13: Plantilla UAT basada en Criterios de Aceptación (CA)
**Decisión:** crear `docs/plantilla_UAT.md` con escenarios de prueba mapeados directamente a los CAs de cada Historia de Usuario.
**Motivación:** sin una plantilla estructurada, las sesiones UAT son inconsistentes y los resultados no son comparables entre participantes. Los CA son la especificación formal de "qué significa correcto" para el usuario.
**Resultado:** 8 escenarios UAT con criterios binarios de aprobación, cuestionario SUS, tabla de resultados y espacio para observaciones libres.
**Lección:** el UAT no es una prueba exploratoria libre; es una verificación formal contra los CAs. Estructurarla antes de reclutar participantes garantiza reproducibilidad.

### Obstáculos

#### OB-07: Equilibrio entre seguridad de rate limiting y usabilidad en modo demo
**Problema:** un rate limiting muy agresivo (ej. 3 intentos) podría bloquear a los evaluadores durante una demostración si escriben la clave incorrectamente dos veces.
**Solución:** configurar `MAX_INTENTOS=5` y `BLOQUEO_SEGUNDOS=300` (5 minutos), con UI que muestra cuántos intentos quedan antes del bloqueo. Documentado en el Manual de Usuario.
**Lección:** los controles de seguridad en sistemas académicos o de demostración deben balancear protección con UX. Un control que interrumpe la demo perjudica tanto como la ausencia del control.

#### OB-08: tests/test_video.py requiere PyAV para frames sintéticos
**Problema:** los tests de `Traductor.recv()` necesitan crear `av.VideoFrame` sintéticos, lo que requiere que `pyav` esté instalado correctamente, incluyendo codecs de video.
**Solución:** añadir `pytestmark = pytest.mark.skipif(not _AV_DISPONIBLE, ...)` al inicio del módulo para que el test se omita graciosamente en entornos sin PyAV, en lugar de fallar con ImportError.
**Lección:** los tests que dependen de librerías pesadas (codecs, hardware) deben incluir guards de importación y marks de skip. El objetivo es que `pytest tests/` siempre retorne 0 errores, incluso en entornos mínimos.

---

## Sprint Reingeniería — Refactoring Estructural y DevSecOps

### Contexto

Al cerrar el Sprint 4, el análisis de deuda técnica identificó cuatro áreas críticas antes de la sustentación final: la estructura de módulos en la raíz causaba fallos de importación en CI, el contenedor Docker se ejecutaba como root, las suites de seguridad y ética no tenían cobertura de tests automatizados, y el dataset todavía presentaba clases sin muestras válidas (INC-07). Este sprint de reingeniería abordó los cuatro problemas en 5 días de trabajo.

### Decisiones técnicas

#### DT-14: Migración a `src/`-layout (PyPA Standard) — INC-08
**Decisión:** mover todos los módulos Python de la raíz a `src/` y los ejecutables a `scripts/`.
**Motivación:** los módulos en la raíz generaban conflictos de `sys.path` al correr pytest desde diferentes directorios y dificultaban la configuración del CI. El `src/`-layout es el estándar PyPA recomendado por la guía oficial de empaquetado Python.
**Resultado:** `pyproject.toml` con `pythonpath = ["src"]`, `conftest.py` actualizado, Dockerfile con `ENV PYTHONPATH=/app/src`. Los imports en producción y en tests son idénticos.
**Lección:** estructurar el repositorio con `src/`-layout desde el Sprint 1 evita refactorizaciones costosas al final del proyecto. El costo de adoptarlo tarde es proporcional al número de módulos y tests existentes.

#### DT-15: Docker non-root user (principio de mínimo privilegio)
**Decisión:** crear usuario `lspuser` (UID 1001) en el Dockerfile y ejecutar la app con `USER lspuser`.
**Motivación:** ejecutar contenedores como `root` es un riesgo de seguridad documentado por OWASP. Si la app tiene una vulnerabilidad de escape, un proceso root puede comprometer el host.
**Resultado:** imagen Docker final no ejecuta como root; `COPY --chown=lspuser:lspuser` garantiza que los archivos también son propiedad del usuario no-root.
**Lección:** el principio de mínimo privilegio no es solo para servidores de producción; debe aplicarse desde el Dockerfile del prototipo académico. El costo de implementarlo es una línea en el Dockerfile.

#### DT-16: Escaneo de vulnerabilidades con Trivy como práctica DevSecOps
**Decisión:** agregar `trivy.yaml` con configuración para escanear la imagen Docker y el código fuente antes de cada despliegue.
**Motivación:** una imagen basada en `python:3.12-slim` puede contener vulnerabilidades en las librerías del sistema operativo (`libssl`, `libcurl`, etc.) que no son visibles en `requirements.txt`.
**Resultado:** `trivy.yaml` configurado para reportar CVEs CRITICAL+HIGH+MEDIUM con exit-code 1 (bloquea CI). `.dockerignore` excluye `data/`, `.git` y `secrets.toml` de la imagen.
**Lección:** las herramientas de SCA (Software Composition Analysis) como Trivy son parte indispensable del pipeline CI/CD moderno, especialmente en proyectos con Docker.

#### DT-17: Suites de tests DevSecOps (20 + 15 = 35 tests nuevos)
**Decisión:** crear `tests/test_seguridad.py` (20 tests en 4 clases) y `tests/test_etica.py` (15 tests en 3 clases) antes de implementar los controles que verifican.
**Motivación:** la seguridad y la ética eran los únicos dominios del sistema sin cobertura de tests automatizados. Seguir la filosofía TDD (Red → Green → Refactor) asegura que cada control es realmente verificable.
**Resultado:** 20/20 tests de seguridad PASS (sanitización, rate limiting, HMAC, tokens, integridad PKL) y 15/15 tests de ética PASS (equidad por clase, XAI, privacidad, honestidad de limitaciones).
**Lección:** la seguridad y la ética deben ser ciudadanos de primera clase en la suite de tests, no solo en la documentación. Si un control de seguridad no tiene un test, no hay evidencia de que funciona.

#### DT-18: Resolución INC-07 — Recaptura y augmentation ×16 (letras N, Q, R, S, V)
**Decisión:** realizar una sesión de recaptura dedicada para las 5 letras con recall 0%, capturando 120+ muestras válidas por letra con condiciones óptimas de iluminación y ángulo, seguida de data augmentation ×16 (rotaciones ±5°/10°/15°, escalado ×0.88–1.12, ruido Gaussiano σ=0.006).
**Motivación:** el modelo con letras sin muestras violaba el principio de equidad (IA Ética): el sistema entrenado con esas letras no podría reconocerlas nunca, afectando desproporcionadamente a los usuarios que usan esas señas.
**Resultado:** accuracy global 88.3% (umbral ≥85%), recall mínimo ≥80% para todas las letras, INC-07 cerrado. `tests/test_etica.py::test_equidad_minima_por_clase_recall_mayor_50` → PASS.
**Lección:** el desequilibrio de clases en visión artificial no se resuelve solo con augmentation; primero se necesitan muestras reales de calidad. El augmentation amplifica muestras buenas, no corrige la ausencia de detección de MediaPipe.

### Obstáculos

#### OB-09: Imports `import lsp_core` fallaban en CI con módulos en raíz
**Problema:** ejecutar pytest desde un directorio diferente al raíz del proyecto causaba `ModuleNotFoundError: No module named 'lsp_core'` porque `sys.path` no incluía el directorio raíz.
**Solución:** migración a `src/`-layout con `pythonpath = ["src"]` en `pyproject.toml`. Ver INC-08 en `INCIDENTES.md` para el análisis técnico completo.
**Lección:** el diseño de la estructura de carpetas tiene impacto directo en la portabilidad de los tests y la configuración del CI. Una estructura incorrecta se vuelve más costosa de corregir a medida que crece el número de tests.

#### OB-10: `.streamlit/config.toml` no persiste en Docker — INC-09
**Problema:** las flags de seguridad de Streamlit (`--server.showErrorDetails=false`, `--server.enableXsrfProtection=true`) configuradas en `.streamlit/config.toml` no se aplicaban en el contenedor HuggingFace, exponiendo trazas de error en la UI.
**Solución:** mover las flags al CMD del Dockerfile con prioridad CLI sobre el archivo de configuración. El orden de precedencia de Streamlit es: CLI flags > variables de entorno > config.toml.
**Lección:** en despliegues Docker, las flags de seguridad críticas deben estar en el CMD del Dockerfile y no depender de archivos de configuración que pueden no leerse. Las capas de configuración tienen prioridades implícitas que deben conocerse.

---

## Mejoras identificadas para versiones futuras

| ID | Mejora | Motivación | Prioridad |
|----|--------|------------|-----------|
| MJ-01 | Soporte para letras dinámicas (J, Z) usando secuencias de landmarks | El alfabeto LSP completo incluye letras con movimiento; el sistema actual solo reconoce gestos estáticos. | Alta |
| MJ-02 | Botón de cierre de sesión explícito | Actualmente la sesión solo expira por tiempo o recarga de página. | Media |
| MJ-03 | ~~Balanceo del dataset con data augmentation~~ **RESUELTO en Sprint Reingeniería** | INC-07 cerrado: augmentation ×16 implementado, recall mínimo ≥80% en todas las clases. | ~~Alta~~ **Cerrado** |
| MJ-04 | Log de auditoría persistente en base de datos | El log actual es efímero en Streamlit Cloud (se pierde al reiniciar). Una base de datos SQLite o PostgreSQL daría persistencia real. | Media |
| MJ-05 | Soporte multi-idioma (ASL, LSM, LIBRAS) | La arquitectura modular permite agregar nuevos modelos SVM entrenados con otros alfabetos de señas. | Baja |
| MJ-06 | Aplicación móvil nativa con TensorFlow Lite | Para usuarios que no tienen acceso a una laptop, una app Android/iOS con el modelo optimizado ampliaría el alcance. | Baja |
| MJ-07 | Exportar historial de texto en formato accesible | Permitir descargar el texto acumulado en .txt o .pdf para que el usuario lo comparta. | Media |
| MJ-08 | Dashboard de progreso de aprendizaje | Mostrar estadísticas de sesión (letras más y menos reconocidas) para que los usuarios practiquen las señas con mayor dificultad. | Baja |

---

## Resumen ejecutivo

| Sprint | Decisiones clave | Obstáculos principales | Días extra |
|--------|-----------------|----------------------|------------|
| Sprint 1 | Landmarks vs. píxeles · Padding ROI · Filtro de calidad en captura | Desequilibrio de clases · Incompatibilidad Python 3.13 | +3 días |
| Sprint 2 | HMAC vs JWT · Anonimización SHA-256 · TDD para seguridad | Latencia de pipeline · WebRTC en Streamlit Cloud | +1 día |
| Sprint 3 | ARIA en `lsp_ui` · Explicabilidad como UI obligatoria | Contrastes insuficientes · Coordinación de usuarios UAT | +1 día |
| Sprint 4 | Artefactos `docs/` · Tests-stub → reales · Rate limiting · SHA-256 PKL | Equilibrio seguridad/usabilidad · PyAV en CI | +0.5 días |
| Sprint Reingeniería | `src/`-layout · Docker non-root · Trivy DevSecOps · 35 tests nuevos · INC-07 resuelto | Imports CI raíz · config.toml Docker | +0 días (planificado) |
| **Total** | **18 decisiones documentadas** | **10 obstáculos resueltos** | **+5.5 días** |

> Los días de trabajo extra de Sprints 1–4 fueron absorbidos por la holgura planificada en los sprints.
> El Sprint de Reingeniería fue planificado explícitamente para cerrar deuda técnica antes de la sustentación.

---

## Retrospectiva Técnica — Visión Artificial con IA

El principal reto de visión artificial en este proyecto fue la detección robusta de gestos de la mano en condiciones no controladas. MediaPipe Hands, a pesar de ser una librería pre-entrenada de alta calidad, tiene un punto ciego específico: los gestos con los dedos curvados hacia adentro (A, S) o cruzados (N, R) generan vectores de landmarks muy similares desde una perspectiva 2D frontal. Esto no es corregible solo con datos; requiere comprensión del problema para ajustar el protocolo de captura (ángulo, iluminación, variedad de poses).

Las mejoras más impactantes del proceso de ingeniería, en orden de retorno sobre la inversión:

1. **Estructura `src/`-layout desde el inicio** — evita la clase completa de errores de importación en CI y facilita la integración futura con pyproject.toml estándar.
2. **TDD para módulos de seguridad** — los tests escritos en estado FAIL obligan a definir el comportamiento exacto antes de implementar, eliminando ambigüedades en los requisitos de seguridad.
3. **Protocolo de captura con umbral de calidad 0.7** — la calidad del dataset supera en impacto a cualquier ajuste de hiperparámetros del modelo.
4. **Data augmentation ×16 como multiplicador de varianza** — transforma muestras bien capturadas en diversidad de posiciones, sin reemplazar la necesidad de muestras reales de calidad.
5. **Separación de resolución de procesamiento y visualización** — la decisión más simple con el mayor impacto en latencia: de 100 ms a 18 ms en el pipeline completo.

---

## Historial de Versiones

| Versión | Fecha | Cambio |
|---------|-------|--------|
| 1.0 | 2026-06-10 | Versión inicial — Sprints 1, 2 y 3 (DT-01 a DT-08, OB-01 a OB-06) |
| 1.5 | 2026-06-12 | Sprint 4 agregado — Trazabilidad y cierre Capstone (DT-09 a DT-13, OB-07 a OB-08) |
| 2.0 | 2026-06-13 | Cierre de proyecto — Sprint Reingeniería (DT-14 a DT-18, OB-09 a OB-10), MJ-03 cerrado, retrospectiva técnica integral, resumen ejecutivo actualizado a 5 sprints |

---

*Registro de Lecciones Aprendidas v2.0 · LSP Vision AI · UPN Sistemas 2026*
*18 decisiones técnicas documentadas · 10 obstáculos resueltos · Proyecto cerrado 2026-06-13*
