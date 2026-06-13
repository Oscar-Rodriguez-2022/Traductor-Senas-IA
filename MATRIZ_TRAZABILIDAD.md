# Matriz de Trazabilidad — LSP Vision AI
## Función de Código → Historia de Usuario → Criterio de Aceptación → Test
### Universidad Privada del Norte · Capstone Project Sistemas 2026
### Versión: 1.0 · Fecha: 2026-06-12

> Esta matriz vincula cada función/componente principal del código fuente con las
> Historias de Usuario (HU), sus Criterios de Aceptación (CA) y los tests que
> verifican el cumplimiento. Permite auditar la cobertura de requerimientos.

---

## 1. Módulo `lsp_core.py`

| Función | HU | CA | Test |
|---------|----|----|------|
| `cargar_modelo(path)` | HU-07, HU-10 | CA-07.3 (persistencia), CA-10.1 (carga al iniciar) | `test_modelo.py::test_cargar_modelo` |
| `_get_hands(static_image_mode)` | HU-09 | CA-09.1 (MediaPipe inicializado), CA-09.3 (ROI estable) | `test_landmarks.py::test_mediapipe_inicializa` |
| `extraer_landmarks(img, mode)` | HU-06, HU-09 | CA-06.1 (extracción), CA-06.2 (normalización), CA-09.1 (21 puntos) | `test_landmarks.py::test_extraer_landmarks_imagen_valida` |
| `extraer_landmarks_de_archivo(path)` | HU-06 | CA-06.1 (extracción de archivo PNG), CA-06.3 (integridad) | `test_landmarks.py::test_extraer_landmarks_de_archivo` |
| `landmarks_validos(landmarks)` | HU-06, HU-10 | CA-06.3 (integridad), CA-10.2 (validación antes de predecir) | `test_modelo.py::test_landmarks_validos_*` |
| `predecir(modelo, landmarks)` | HU-07, HU-10 | CA-07.2 (precisión), CA-10.2 (respuesta ≤0.4s), CA-10.3 (confianza%) | `test_modelo.py::test_prediccion_retorna_letra_y_confianza` |
| `cargar_dataset(folder, limite)` | HU-05, HU-07 | CA-05.3 (formato y etiquetado), CA-07.1 (división entrenamiento) | `test_validacion.py::test_cargar_dataset_formato` |
| `imagenes_disponibles(folder)` | HU-04 | CA-04.2 (organización en carpetas) | `test_validacion.py::test_imagenes_disponibles` |
| `close_hands()` | HU-22 | CA-22.3 (sin fugas de recursos) | `test_errores.py::test_close_hands_libera_recursos` |

---

## 2. Módulo `lsp_video.py`

| Función / Clase | HU | CA | Test |
|-----------------|----|----|------|
| `Traductor.__init__(modelo)` | HU-08, HU-09 | CA-08.1 (stream inicia), CA-09.1 (MediaPipe listo) | `test_integracion.py::test_traductor_inicializa` |
| `Traductor.recv(frame)` | HU-08, HU-09, HU-10 | CA-08.3 (procesa frames), CA-09.2 (dibuja skeleton), CA-10.2 (≤0.4s) | `test_integracion.py::test_recv_retorna_frame_anotado` |
| `Traductor.recv` → `_get_hands` | HU-09 | CA-09.3 (ROI estable) | — (cubierto por `test_integracion.py`) |
| `Traductor.recv` → `predecir()` | HU-10 | CA-10.3 (confianza %), CA-10.4 (FPS ≥24) | `test_modelo.py`, `qa/fps_test.py` |
| `Traductor.fps` (EMA) | HU-22 | CA-22.1 (FPS ≥24 en 60s) | `qa/fps_test.py` |
| `Traductor.lock` (thread-safety) | HU-08 | CA-08.4 (rendimiento, sin race conditions) | `test_integracion.py::test_thread_safety` |

---

## 3. Módulo `lsp_auth.py`

| Función | HU | CA | Test |
|---------|----|----|------|
| `hash_password(password)` | HU-13 | CA-13.1 (hash seguro PBKDF2) | `test_auth.py::test_hash_password_produce_hex` |
| `generar_token_sesion(pwd, hash)` | HU-13 | CA-13.2 (token emitido en login exitoso) | `test_auth.py::test_generar_token_formato_correcto` |
| `verificar_token(token)` | HU-13 | CA-13.3 (rechaza tokens expirados/manipulados) | `test_auth.py::test_token_expirado`, `test_auth.py::test_token_manipulado` |
| `login_requerido(st_state)` | HU-13 | CA-13.4 (guard de acceso), CA-13.5 (redirige sin auth) | `test_auth.py::test_login_requerido_*` |
| `_render_login(st, st_state)` | HU-13, HU-15 | CA-13.2 (formulario funcional), CA-15.1 (accesibilidad del form) | `test_auth.py::test_render_login_*` |
| `_firmar(ts_str, nonce)` | HU-13 | CA-13.6 (firma HMAC-SHA256 resistente a XSS/inyección) | `test_auth.py::test_firma_resiste_inyeccion_xss` |

---

## 4. Módulo `lsp_audit.py`

| Función | HU | CA | Test |
|---------|----|----|------|
| `registrar_acceso(evento, detalle, st_state)` | HU-14 | CA-14.1 (registra evento), CA-14.2 (sin PII) | `test_audit.py::test_registrar_acceso_crea_entrada` |
| `leer_log_reciente(n)` | HU-14, HU-17 | CA-14.3 (log legible), CA-17.3 (dashboard lee log) | `test_audit.py::test_leer_log_reciente_retorna_lista` |
| `purgar_log_antiguo(dias)` | HU-14 | CA-14.4 (retención 7 días), HU-20 (privacidad) | `test_audit.py::test_purgar_log_elimina_antiguos` |
| `_id_sesion(st_state)` | HU-14 | CA-14.2 (ID anónimo, no reversible) | `test_audit.py::test_id_sesion_es_anonimo` |

---

## 5. Módulo `lsp_ui.py`

| Función | HU | CA | Test |
|---------|----|----|------|
| `render_estilos()` | HU-15 | CA-15.2 (contraste ≥4.5:1), CA-15.3 (skip-nav CSS) | Verificación manual (Chrome DevTools) |
| `render_skip_nav()` | HU-15 | CA-15.3 (WCAG 2.4.1 — enlace skip-nav) | Verificación manual (Tab focus) |
| `render_topbar(n_senas)` | HU-12 | CA-12.2 (interfaz muestra estado) | — |
| `render_hero()` | HU-12 | CA-12.2 (bienvenida e instrucciones) | — |
| `render_resultado(letra, conf, mano)` | HU-10, HU-15 | CA-10.3 (borde rojo/amarillo), CA-15.1 (aria-live="polite") | Verificación manual |
| `render_pipeline_explicado()` | HU-16 | CA-16.1 (explicabilidad del pipeline), CA-16.2 (accesible) | Verificación manual |
| `render_estado_sistema(n_senas, modelo_cargado)` | HU-12 | CA-12.3 (estado del sistema visible) | — |
| `render_estadisticas(n_senas, fps_real)` | HU-17 | CA-17.1 (métricas visibles al usuario) | — |
| `render_footer()` | HU-15 | CA-15.1 (role="contentinfo") | Verificación manual |

---

## 6. `app.py` — Orquestador

| Componente | HU | CA | Test |
|------------|----|----|------|
| `st.set_page_config(...)` | HU-12 | CA-12.1 (coexistencia de módulos) | — |
| `cargar_modelo()` (`@st.cache_resource`) | HU-10 | CA-10.1 (carga al iniciar) | `test_modelo.py::test_cargar_modelo` |
| Guard `lsp_auth.login_requerido(...)` | HU-13 | CA-13.4 (guard de acceso en app principal) | `test_auth.py::test_login_requerido_*` |
| `lsp_audit.registrar_acceso(...)` | HU-14 | CA-14.1 (registra PAGINA_VISITADA) | `test_audit.py` |
| `webrtc_streamer(Traductor)` | HU-08 | CA-08.1 (stream de video activado) | `test_integracion.py` |
| `panel_resultado()` (`@st.fragment`) | HU-10, HU-11 | CA-10.2 (actualización ≤0.4s), CA-11.1 (historial) | `test_integracion.py` |
| `lsp_ui.render_pipeline_explicado()` | HU-16 | CA-16.1 (explicabilidad) | Verificación manual |

---

## 7. `pages/1_Metricas_QA.py` — Dashboard

| Componente | HU | CA | Test |
|------------|----|----|------|
| Guard `lsp_auth.login_requerido(...)` | HU-13, HU-17 | CA-13.4 (guard), CA-17.3 (solo autenticados) | `test_auth.py` |
| Tarjetas de métricas (accuracy, F1, etc.) | HU-17 | CA-17.1 (métricas accuracy/F1 visibles) | `qa/evaluate.py` |
| Recursos en vivo (psutil) | HU-17, HU-22 | CA-17.2 (CPU/RAM en tiempo real) | `qa/recursos.py` |
| `mostrar_tabla("benchmark.csv")` | HU-22 | CA-22.2 (latencias por etapa) | `qa/benchmark.py` |
| `mostrar_tabla("fps.csv")` | HU-22 | CA-22.1 (FPS ≥24) | `qa/fps_test.py` |
| Log de auditoría (`lsp_audit.leer_log_reciente`) | HU-14, HU-17 | CA-14.3, CA-17.3 | `test_audit.py` |

---

## 8. Scripts de Entrenamiento y QA

| Script | HU | CA | Herramienta validación |
|--------|----|----|------------------------|
| `entrenar_modelo.py` | HU-07 | CA-07.1, CA-07.3 | — (script de uso) |
| `augmentar_dataset.py` | HU-05 | CA-05.1 (más muestras) | — |
| `entrenar_desde_csv.py` | HU-05 | CA-05.2 (diversidad colaborativa) | — |
| `A.py` | HU-04, HU-15 | CA-04.3 (sin sobreescribir) | Manual |
| `qa/evaluate.py` | HU-07, HU-17 | CA-07.2 (accuracy ≥85%) | `make evaluate` |
| `qa/benchmark.py` | HU-22 | CA-22.2 (etapa ≤200ms) | `make benchmark` |
| `qa/fps_test.py` | HU-08, HU-22 | CA-08.4, CA-22.1 (FPS ≥24 en 60s) | `make fps` |
| `qa/stress_test.py` | HU-22 | CA-22.3 (sin memory leak 300s) | `make stress` |
| `qa/cross_validation.py` | HU-07 | CA-07.2 (estabilidad K-Fold) | `make crossval` |
| `qa/confusion_matrix.py` | HU-07, HU-17 | CA-07.2 (por clase), CA-17.1 | `make confusion` |
| `qa/robustez.py` | HU-10 | CA-10.3 (degradación graceful) | `make robustez` |
| `qa/recursos.py` | HU-22 | CA-22.4 (RAM ≤512MB, CPU ≤80%) | `make recursos` |

---

## 9. Cobertura de HUs por Módulo

| HU | `lsp_core` | `lsp_video` | `lsp_auth` | `lsp_audit` | `lsp_ui` | `app.py` | `pages/` | `qa/` | `tests/` |
|----|:-----------:|:-----------:|:-----------:|:-----------:|:--------:|:--------:|:--------:|:-----:|:--------:|
| HU-01 | — | — | — | — | — | — | — | — | — |
| HU-02 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| HU-03 | — | — | — | — | — | — | — | — | — |
| HU-04 | ✅ | — | — | — | — | — | — | — | — |
| HU-05 | ✅ | — | — | — | — | — | — | — | — |
| HU-06 | ✅ | — | — | — | — | — | — | — | ✅ |
| HU-07 | ✅ | — | — | — | — | — | — | ✅ | ✅ |
| HU-08 | — | ✅ | — | — | — | ✅ | — | ✅ | ✅ |
| HU-09 | ✅ | ✅ | — | — | — | — | — | — | ✅ |
| HU-10 | ✅ | ✅ | — | — | ✅ | ✅ | — | ✅ | ✅ |
| HU-11 | — | — | — | — | ✅ | ✅ | — | — | — |
| HU-12 | — | — | — | — | ✅ | ✅ | — | — | ✅ |
| HU-13 | — | — | ✅ | — | — | ✅ | ✅ | — | ✅ |
| HU-14 | — | — | — | ✅ | — | ✅ | ✅ | — | ✅ |
| HU-15 | — | — | — | — | ✅ | — | — | — | — |
| HU-16 | — | — | — | — | ✅ | ✅ | — | — | — |
| HU-17 | — | — | — | ✅ | ✅ | — | ✅ | ✅ | — |
| HU-18 | — | — | — | — | — | — | — | — | ✅ |
| HU-19 | — | — | — | — | — | — | — | — | — |
| HU-20 | — | — | — | ✅ | — | — | — | — | — |
| HU-21 | — | — | — | — | — | — | — | — | — |
| HU-22 | — | ✅ | — | — | — | — | ✅ | ✅ | — |

> ✅ = el módulo implementa al menos un CA de esa HU.

---

## Historial de Versiones

| Versión | Fecha | Cambio |
|---------|-------|--------|
| 1.0 | 2026-06-12 | Versión inicial — trazabilidad completa de 8 módulos, 22 HUs y 49 tests |
