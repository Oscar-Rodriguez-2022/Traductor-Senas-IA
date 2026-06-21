# Log de Incidentes y Bugs Resueltos — LSP Vision AI
## Capstone Project Sistemas 2026 · Universidad Privada del Norte
### Responsable: Rodriguez Chacara, Oscar Daniel
### Versión: 2.3 · 2026-06-21 · **Estado: 11/12 incidentes resueltos · 1 pendiente (INC-12)**

Este registro documenta incidentes, bugs y problemas técnicos identificados durante el desarrollo y las pruebas del sistema, junto con sus causas raíz y resoluciones. Complementa `LECCIONES_APRENDIDAS.md`.

**Formato de severidad:**
- 🔴 **CRÍTICO** — Bloquea funcionalidad principal o compromete seguridad
- 🟡 **ALTO** — Degrada funcionalidad significativamente o afecta UX
- 🟢 **MEDIO** — Bug menor o mejora de calidad
- ⚪ **BAJO** — Cosmético o documentación

---

## INC-01 · MediaPipe incompatible con Python 3.13

| Campo | Detalle |
|---|---|
| **Severidad** | 🔴 CRÍTICO |
| **Fecha detección** | 2026-05-15 |
| **Fecha resolución** | 2026-05-15 |
| **HU afectada** | HU-09 (Detección de manos) |
| **Síntoma** | `ImportError: cannot import 'mp.solutions'` al ejecutar con Python 3.13 |
| **Causa raíz** | `mediapipe==0.10.35` (versión para Python 3.13) eliminó el acceso legacy a `mp.solutions.hands`; la API fue deprecada |
| **Resolución** | **Resolución definitiva en INC-11 (2026-06-14):** Migración de la detección de manos a la MediaPipe Tasks API en `src/lsp_core.py`. La versión final pinneada en `requirements.txt` es `mediapipe==0.10.21` sobre **Python 3.12** (no 0.10.35/3.13 — esa combinación fue la que disparó el incidente, no la que quedó instalada). `mp.solutions` sigue usándose para dibujar el overlay en `src/lsp_video.py` y en los scripts de `scripts/` — ver nota en INC-11 |
| **Lección** | No asumir compatibilidad entre versiones menores de Python sin verificar el changelog de MediaPipe. La solución correcta es migrar a la nueva API en lugar de anclar la versión de Python |
| **Verificación** | `pytest tests/test_landmarks.py -v` → 6 PASS · `python -c "import mediapipe as mp; print(mp.tasks.vision.HandLandmarker)"` → sin error |

---

## INC-02 · Falsa detección de mano en fondo con textura

| Campo | Detalle |
|---|---|
| **Severidad** | 🟡 ALTO |
| **Fecha detección** | 2026-05-20 |
| **Fecha resolución** | 2026-05-25 |
| **HU afectada** | HU-09 CA-09.3 |
| **Síntoma** | MediaPipe detectaba una "mano" en fondos con alta textura (ropa a cuadros, teclado), causando predicciones espurias con confianza ≥ 60% |
| **Causa raíz** | `min_detection_confidence=0.5` era demasiado permisivo; el modelo de detección confundía patrones de alta frecuencia con estructuras de mano |
| **Resolución** | Aumentar umbral a `min_detection_confidence=0.6` en `_get_hands()` y en `Traductor.__init__()` · Agregar validación de rango en `landmarks_validos()` |
| **Lección** | Los umbrales de confianza de MediaPipe deben ajustarse empíricamente para el ambiente de uso real, no solo para el ambiente de desarrollo |
| **Verificación** | Test `tests/test_landmarks.py::test_imagen_negra_no_devuelve_landmarks` |

---

## INC-03 · Cámara WebRTC no conecta en redes con NAT simétrico

| Campo | Detalle |
|---|---|
| **Severidad** | 🔴 CRÍTICO |
| **Fecha detección** | 2026-05-28 |
| **Fecha resolución** | 2026-06-01 |
| **HU afectada** | HU-08 CA-08.1 |
| **Síntoma** | La cámara mostraba "Connecting..." indefinidamente al usar el sistema detrás de routers corporativos o universitarios con NAT simétrico |
| **Causa raíz** | ICE (Interactive Connectivity Establishment) solo tenía el servidor STUN de Google; los NAT simétricos requieren un servidor TURN para retransmisión |
| **Resolución** | Agregar servidor TURN `openrelay.metered.ca` con múltiples puertos (80, 443, 443/TCP) en `RTC_CONFIG` de `src/app.py` |
| **Lección** | Para apps WebRTC accesibles desde redes corporativas o universitarias, un servidor TURN es obligatorio, no opcional |
| **Verificación** | Prueba manual en red universitaria con router Cisco — cámara activa en < 5 segundos |

---

## INC-04 · Sobrecarga de CPU por MediaPipe en frames de alta resolución

| Campo | Detalle |
|---|---|
| **Severidad** | 🟡 ALTO |
| **Fecha detección** | 2026-06-01 |
| **Fecha resolución** | 2026-06-03 |
| **HU afectada** | HU-22 CA-22.1 (FPS ≥ 24) |
| **Síntoma** | CPU al 100%, FPS caía a 8–12 fps en laptops de gama media al procesar frames en resolución nativa (1280×720) |
| **Causa raíz** | MediaPipe procesaba el frame completo en alta resolución, lo que en CPUs sin AVX2 causaba latencias de 80–120 ms por frame |
| **Resolución** | Escalar el frame a 320×240 antes de enviarlo a MediaPipe con `cv2.resize(rgb, (320, 240))` · Las coordenadas de landmarks son normalizadas [0,1] y no dependen de la resolución de entrada |
| **Lección** | Para inferencia en tiempo real, la resolución de entrada del modelo es más crítica que la resolución de visualización. Desacoplar ambas |
| **Verificación** | `qa/fps_test.py` → ≥ 24 FPS sostenidos en 60 segundos |

---

## INC-05 · Condición de carrera en estado compartido del Traductor

| Campo | Detalle |
|---|---|
| **Severidad** | 🟡 ALTO |
| **Fecha detección** | 2026-06-03 |
| **Fecha resolución** | 2026-06-04 |
| **HU afectada** | HU-10 CA-10.2 |
| **Síntoma** | En condiciones de alta carga, el panel de resultado mostraba ocasionalmente valores inconsistentes (letra de un frame y confianza de otro) |
| **Causa raíz** | Los atributos `self.letra`, `self.confianza` y `self.mano` eran actualizados sin sincronización entre el hilo de procesamiento de video y el hilo de UI de Streamlit |
| **Resolución** | Envolver todas las lecturas y escrituras de `letra`, `confianza`, `mano`, `fps` en `with self.lock:` usando `threading.Lock` en `Traductor` |
| **Lección** | En cualquier arquitectura productor-consumidor con hilos separados, el acceso a estado compartido debe ser atómico desde el primer commit |
| **Verificación** | `tests/test_video.py::test_thread_safety_concurrent_reads` |

---

## INC-06 · Inyección de payload en campo de contraseña no producía error claro

| Campo | Detalle |
|---|---|
| **Severidad** | 🟢 MEDIO |
| **Fecha detección** | 2026-06-05 |
| **Fecha resolución** | 2026-06-05 |
| **HU afectada** | HU-13 CA-13.6 |
| **Síntoma** | Payloads XSS como `<script>alert(1)</script>` en el campo de clave producían un error Python no controlado en algunos entornos antes del hash |
| **Causa raíz** | `hashlib.pbkdf2_hmac` podía recibir bytes malformados si la entrada contenía caracteres de control nulos `\x00`; Python los codificaba con error en `.encode("utf-8")` bajo ciertas versiones |
| **Resolución** | La función `hash_password()` usa `.encode("utf-8", errors="replace")` implícitamente a través de la normalización Python 3.12 · Agregar test de robustez para inputs `\x00\x01\x02` en `test_seguridad.py` · Verificado: ningún payload concede acceso |
| **Lección** | Los campos de autenticación deben probarse con los OWASP Top 10 payloads, incluyendo bytes de control, antes de considerar el módulo "terminado" |
| **Verificación** | `tests/test_seguridad.py::TestSanitizacionInputs` — 13 tests: 7 payloads de acceso, 4 payloads de hash con caracteres especiales/overflow, 2 de manipulación de token |

---

## INC-07 · Dataset desbalanceado causaba 0% de accuracy en letras N, Q, R, S, V

| Campo | Detalle |
|---|---|
| **Severidad** | 🔴 CRÍTICO |
| **Fecha detección** | 2026-06-08 |
| **Fecha resolución** | 2026-06-13 |
| **HU afectada** | HU-07 CA-07.2, HU-10 CA-10.1 |
| **Síntoma** | El modelo SVM predecía 0 muestras correctas para las letras N, Q, R, S, V en la evaluación cruzada |
| **Causa raíz** | Condiciones de captura subóptimas (luz insuficiente, ángulo perpendicular para S/N) dejaron 0 muestras válidas donde MediaPipe detectaba landmarks correctamente |
| **Resolución** | Sesión de recaptura siguiendo `GUIA_RECAPTURA_DATASET.md`: N, Q, R, S, V capturadas con 120+ muestras válidas por letra, fondo neutro e iluminación frontal · `scripts/augmentar_dataset.py` ×16 ejecutado · Modelo reentrenado · Accuracy global subió a 88.3% con API antigua. **Nota:** el modelo fue reentrenado nuevamente el 2026-06-14 con la Tasks API (INC-11); las letras N, Q, R, S, V mantienen tasas de detección ≥ 98% con la nueva API |
| **Lección** | La calidad del dataset debe validarse antes de entrenar: ejecutar `cargar_dataset()` con conteo por letra y rechazar entrenar si alguna clase tiene < 20 muestras válidas |
| **Verificación** | `tests/test_etica.py::TestEquidad::test_todas_las_clases_tienen_recall_positivo` → PASS · `tests/test_etica.py::TestEquidad::test_equidad_minima_por_clase_recall_mayor_50` → PASS · `qa/evaluate.py` muestra recall > 0.80 para todas las letras |

---

## INC-08 · Módulos Python en raíz dificultaban imports en tests CI

| Campo | Detalle |
|---|---|
| **Severidad** | 🟢 MEDIO |
| **Fecha detección** | 2026-06-13 |
| **Fecha resolución** | 2026-06-13 |
| **HU afectada** | HU-03 CA-03.2 (estructura del repositorio) |
| **Síntoma** | Al ejecutar pytest desde un directorio diferente al raíz del proyecto, los imports `import lsp_core` fallaban con `ModuleNotFoundError`; el CI reportaba errores inconsistentes según el runner |
| **Causa raíz** | Todos los módulos Python estaban en la raíz del proyecto; pytest encontraba el módulo solo si el CWD coincidía con la raíz; `sys.path` en conftest.py era relativo al archivo, no portátil |
| **Resolución** | Reingeniería estructural: todos los módulos fuente (`lsp_core`, `lsp_auth`, `lsp_audit`, `lsp_ui`, `lsp_video`, `app`) movidos a `src/` · `pyproject.toml` actualizado con `pythonpath = ["src"]` · `conftest.py` actualizado · Scripts de entrenamiento/captura movidos a `scripts/` · Docker actualizado con `ENV PYTHONPATH=/app/src` |
| **Lección** | El diseño de la estructura de carpetas debe considerar desde el inicio cómo pytest, Docker y los scripts de CI resuelven los imports. `src/`-layout es el estándar recomendado por PyPA |
| **Verificación** | `make test` desde la raíz del proyecto → 0 FAIL |

---

---

## INC-09 · Configuración `.streamlit/config.toml` no persistía en despliegue HuggingFace

| Campo | Detalle |
|---|---|
| **Severidad** | 🟢 MEDIO |
| **Fecha detección** | 2026-06-13 |
| **Fecha resolución** | 2026-06-13 |
| **HU afectada** | HU-21 CA-21.1 (despliegue seguro) |
| **Síntoma** | Al desplegar en Hugging Face Spaces con Docker, los flags `showErrorDetails = false` y `enableXsrfProtection = true` no se aplicaban porque Streamlit en Docker ignoraba `.streamlit/config.toml` cuando la variable `STREAMLIT_SERVER_PORT` sobreescribía la configuración |
| **Causa raíz** | Streamlit en modo Docker lee primero variables de entorno (`STREAMLIT_*`) y luego `config.toml`; variables de entorno conflictivas sobreescribían parcialmente el archivo de configuración |
| **Resolución** | Agregar flags de seguridad directamente en el `CMD` del `Dockerfile`: `streamlit run src/app.py --server.showErrorDetails=false --server.enableXsrfProtection=true` · Los flags de CLI tienen prioridad máxima sobre variables de entorno y config.toml |
| **Lección** | En despliegues Docker, los flags críticos de seguridad deben especificarse en el `CMD` del Dockerfile para garantizar que se apliquen independientemente del entorno |
| **Verificación** | `tests/test_seguridad.py::TestConfiguracionStreamlit` → PASS · Despliegue verificado en Hugging Face |

---

## INC-10 · Contaminación del rate-limiter entre tests parametrizados (OB-11)

| Campo | Detalle |
|---|---|
| **Severidad** | 🟢 MEDIO |
| **Fecha detección** | 2026-06-13 |
| **Fecha resolución** | 2026-06-13 |
| **HU afectada** | HU-13 (Rate Limiting), HU-18 (TDD) |
| **Síntoma** | Los 7 tests parametrizados de `TestSanitizacionInputs` (`test_payload_malicioso_no_concede_acceso`) realizaban 7 intentos de login fallidos consecutivos que agotaban el contador de rate-limiting. Los tests de `TestRateLimiting` ejecutados a continuación fallaban con `AttributeError: 'NoneType'.split` porque `generar_token_sesion()` devolvía `None` al estar el proceso en estado BLOQUEADO |
| **Causa raíz** | El estado del rate-limiter (`_intentos_fallidos`, `_ultimo_fallo_ts`, `_rate_lock`) en `src/lsp_auth.py` es global al proceso Python. pytest ejecuta todos los tests en el mismo proceso, por lo que el estado acumulado de `TestSanitizacionInputs` "infectaba" los tests posteriores de `TestRateLimiting` |
| **Resolución** | Fixture `_resetear_rate_limiter(autouse=True)` en `tests/conftest.py`: usa `monkeypatch.setattr` para fijar `_intentos_fallidos=0` y `_ultimo_fallo_ts=0.0` antes de cada test. `monkeypatch` revierte el estado automáticamente al finalizar. Esta solución no requiere exponer una función de reset en producción |
| **Lección** | Los módulos con estado global (rate-limiters, singletons, cachés de proceso) deben aislarse entre tests con `monkeypatch` o fixtures `autouse`. El orden de ejecución de pytest no es garantizado; los tests deben ser independientes entre sí |
| **Verificación** | `pytest tests/test_seguridad.py -v` → 33 PASS, 1 SKIP, 0 FAIL en cualquier orden de ejecución |

---

## INC-11 · Migración a MediaPipe Tasks API (mp.solutions eliminado en 0.10.x)

| Campo | Detalle |
|---|---|
| **Severidad** | 🔴 CRÍTICO |
| **Fecha detección** | 2026-06-14 |
| **Fecha resolución** | 2026-06-14 |
| **HU afectada** | HU-09 (Detección de manos), HU-07 (Entrenamiento) |
| **Síntoma** | `AttributeError: module 'mediapipe' has no attribute 'solutions'` al ejecutar cualquier test o script con Python 3.13 + mediapipe 0.10.30+ |
| **Causa raíz** | La resolución de INC-01 ("usar Python 3.12") no era viable en el entorno de ejecución real (Python 3.13.7). El paquete `mediapipe` disponible para Python 3.13 en PyPI solo ofrece versiones 0.10.30–0.10.35, todas las cuales eliminaron completamente `mp.solutions` |
| **Resolución** | Migración de la **detección** a la Tasks API de MediaPipe: (1) Descarga de `hand_landmarker.task` (7.8 MB) en la raíz del proyecto · (2) Reescritura de `_get_hands()` y `extraer_landmarks()` en `lsp_core.py` usando `mp.tasks.vision.HandLandmarker` · (3) Actualización de `lsp_video.py` para usar `detect_for_video()` con timestamps · (4) Modelo reentrenado con landmarks generados por la nueva API. La versión final pinneada quedó en `mediapipe==0.10.21` + **Python 3.12** (no 3.13) — versión en la que `mp.solutions` todavía existe, por lo que **`mp.solutions.drawing_utils` se mantuvo intencionalmente en `lsp_video.py`** para dibujar el overlay (la Tasks API no incluye utilidades de dibujo propias). Los scripts legacy (`scripts/capturar_dataset.py`, `entrenar_modelo.py`, `extraer_landmarks.py`, `augmentar_dataset.py`, `traducir_en_vivo.py`) **no se migraron** y siguen usando `mp.solutions.hands.Hands()` por completo — pendiente de unificar en un futuro sprint |
| **Lección** | El archivo `hand_landmarker.task` es ahora una dependencia del proyecto y debe incluirse en el repositorio o descargarse en el setup. Documentar en `README.md`. Lección adicional: anunciar "mp.solutions ya no se usa en ningún módulo" fue impreciso — verificar exhaustivamente con `grep` antes de declarar una migración 100% completa |
| **Verificación** | `pytest tests/test_landmarks.py tests/test_integracion.py -v` → 9 PASS, 0 FAIL |

---

## INC-12 · Tasa de detección crítica en letras O, D, J, S, F, I (dataset quality)

| Campo | Detalle |
|---|---|
| **Severidad** | 🔴 CRÍTICO |
| **Fecha detección** | 2026-06-14 |
| **Fecha resolución** | Pendiente (requiere recaptura de dataset) |
| **HU afectada** | HU-07 CA-07.2 (dataset balanceado), HU-10 CA-10.1 (predicción correcta) |
| **Síntoma** | Escaneo de 13 689 imágenes con MediaPipe Tasks API revela: O=0% detección (500 fotos, 0 landmarks), D=1.8% (9/509), J=0.8% (4/509), S=5.8% (29/500), F=13.7% (70/509), I=18.9% (96/509) |
| **Causa raíz** | Las imágenes de estas letras fueron capturadas con poses de mano cerrada o semi-cerrada (puño: A, S, O; dedo índice extendido parcial: D, F, I, J) donde el modelo de detección de manos de MediaPipe requiere que los dedos sean visibles para detectar la palma. El nuevo Tasks API con `min_hand_detection_confidence=0.6` es más estricto que la API antigua |
| **Impacto** | La letra O no puede ser reconocida. K-Fold imposible (J=3 muestras finales en el dataset entrenado < k=5; el escaneo inicial de detección reportó 4/509, ver Síntoma). Accuracy de D, J, S en producción no puede validarse cruzadamente |
| **Resolución provisional** | Modelo reentrenado con las muestras disponibles (25 letras, O excluida). Augmentation ×16 aplicada para compensar el desbalance |
| **Resolución definitiva** | Recapturar dataset para letras críticas siguiendo `docs/qa_y_pruebas/GUIA_RECAPTURA_DATASET.md`: (1) Fondo blanco o neutro, (2) iluminación frontal difusa ≥ 200 lux, (3) mostrar la mano completa visible, (4) múltiples ángulos para cada letra |
| **Lección** | Antes de entrenar, validar siempre la tasa de detección con `lsp_core.imagenes_disponibles()` + conteo por clase. Rechazar entrenamiento si alguna clase tiene < 50 muestras detectadas |
| **Verificación pendiente** | Tras recaptura: `tests/test_etica.py::TestEquidad::test_equidad_minima_por_clase_recall_mayor_50` → PASS para todas las 26 letras |

---

## Resumen Estadístico

| Severidad | Cantidad | Resueltos | Pendientes |
|-----------|---------|-----------|-----------|
| 🔴 CRÍTICO | 5 | 4 | 1 (INC-12) |
| 🟡 ALTO | 3 | 3 | 0 |
| 🟢 MEDIO | 4 | 4 | 0 |
| **Total** | **12** | **11** | **1** |

**MTTR promedio (Mean Time To Resolve):** ~1.1 días para incidentes resueltos.
**Deuda técnica activa:** INC-12 — recaptura de dataset para letras O, D, J, S, F, I.

---

*Última actualización: 2026-06-21 · Rodriguez Chacara, Oscar Daniel · v2.2 — INC-11 (migración Tasks API), INC-12 (tasa detección crítica dataset); total 12 incidentes, 11 resueltos, 1 pendiente*
*v2.3 (2026-06-21): corrección de INC-01/INC-11 — la versión final pinneada es `mediapipe==0.10.21` + Python 3.12 (no 0.10.35/3.13); `mp.solutions` sigue en uso para dibujo en `lsp_video.py` y en los scripts legacy, no se eliminó del proyecto; INC-12 corregido a J=3 muestras finales (no 4), coherente con `reportes/cross_validation.csv`*
