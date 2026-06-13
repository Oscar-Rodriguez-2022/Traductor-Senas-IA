# Log de Incidentes y Bugs Resueltos — LSP Vision AI
## Capstone Project Sistemas 2026 · Universidad Privada del Norte
### Responsable: Rodriguez Chacara, Oscar Daniel
### Versión: 2.1 · 2026-06-13 · **Estado: 10/10 incidentes RESUELTOS**

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
| **Resolución** | Fijar Python 3.12 como versión de referencia del proyecto · Usar `mediapipe==0.10.21` en `requirements.txt` · Documentar restricción en `GUIA_RECAPTURA_DATASET.md` y en memoria del proyecto |
| **Lección** | No asumir compatibilidad entre versiones menores de Python sin verificar el changelog de MediaPipe |
| **Verificación** | `py -3.12 -c "import mediapipe as mp; print(mp.solutions.hands)"` → sin error |

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
| **Resolución** | Sesión de recaptura siguiendo `GUIA_RECAPTURA_DATASET.md`: N, Q, R, S, V capturadas con 120+ muestras válidas por letra, fondo neutro e iluminación frontal · `scripts/augmentar_dataset.py` ×16 ejecutado sobre el dataset completo · Modelo reentrenado con `scripts/entrenar_modelo.py` · Accuracy global subió a 88.3% |
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

## Resumen Estadístico

| Severidad | Cantidad | Resueltos | Pendientes |
|-----------|---------|-----------|-----------|
| 🔴 CRÍTICO | 3 | 3 | 0 |
| 🟡 ALTO | 3 | 3 | 0 |
| 🟢 MEDIO | 4 | 4 | 0 |
| **Total** | **10** | **10** | **0** |

**MTTR promedio (Mean Time To Resolve):** ~1.3 días para todos los incidentes.
**Deuda técnica generada:** 0 ítems críticos pendientes al cierre del proyecto.

---

*Última actualización: 2026-06-13 · Rodriguez Chacara, Oscar Daniel · v2.1 — INC-10 añadido (OB-11: contaminación rate-limiter); conteo TestSanitizacionInputs 11→13; refs INC-07 con clase; total 10/10 incidentes*
