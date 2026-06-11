# Registro de Lecciones Aprendidas — LSP Vision AI
## Universidad Privada del Norte · Capstone Project Sistemas 2026
### Autor: Rodriguez Chacara, Oscar Daniel

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
**Decisión:** el script `A.py` descarta automáticamente frames donde MediaPipe reporta confianza de detección < 0.7.
**Motivación:** sin este filtro, el dataset contenía imágenes con manos parcialmente detectadas que introducían ruido en el entrenamiento.
**Resultado:** dataset más limpio y reducción del tiempo de depuración manual.
**Lección:** la calidad del dataset tiene más impacto en el rendimiento final que los hiperparámetros del modelo. Invertir tiempo en curation del dataset es siempre rentable.

### Obstáculos

#### OB-01: Desequilibrio de clases en el dataset inicial
**Problema:** las primeras letras capturadas (A, B, C) tenían 150+ muestras, mientras que letras capturadas al final (N, O) tenían menos de 20. Esto causó que la validación cruzada K-Fold fallara (`k > n_samples` para algunas clases).
**Solución:** se implementó el sistema de captura colaborativa por CSV (`entrenar_desde_csv.py`) para que los compañeros de equipo pudieran contribuir muestras de las letras faltantes sin instalar el entorno completo.
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

## Mejoras identificadas para versiones futuras

| ID | Mejora | Motivación | Prioridad |
|----|--------|------------|-----------|
| MJ-01 | Soporte para letras dinámicas (J, Z) usando secuencias de landmarks | El alfabeto LSP completo incluye letras con movimiento; el sistema actual solo reconoce gestos estáticos. | Alta |
| MJ-02 | Botón de cierre de sesión explícito | Actualmente la sesión solo expira por tiempo o recarga de página. | Media |
| MJ-03 | Balanceo del dataset con data augmentation | Algunas clases tienen pocas muestras; técnicas como rotación y variación de brillo mejorarían la generalización. | Alta |
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
| **Total** | **8 decisiones documentadas** | **6 obstáculos resueltos** | **+5 días** |

> Los 5 días de trabajo extra fueron absorbidos por la holgura planificada en los sprints (capacidad conservadora vs. velocidad real del equipo).

---

*Documento elaborado por el equipo de desarrollo · Capstone Project UPN Sistemas 2026*
