# Matriz de Trazabilidad — LSP Vision AI
## Mapeo: Historia de Usuario → Módulo de Código → Prueba → Estado
### Universidad Privada del Norte · Capstone Project Sistemas 2026
### Versión: 2.0 · Fecha: 2026-06-13 · **Estado: CIERRE — 22/22 HUs completadas**

> Esta matriz vincula cada función/componente principal del código fuente con las
> Historias de Usuario (HU), sus Criterios de Aceptación (CA) y los tests que
> verifican el cumplimiento. Permite auditar la cobertura total de requerimientos.
> Actualizada tras la reingeniería estructural (src-layout) y el cierre del Capstone.

---

## Resumen Ejecutivo de Trazabilidad

| Dimensión | Total | Cubiertos | Cobertura |
|---|---|---|---|
| Historias de Usuario | 22 | 22 | **100%** |
| Criterios de Aceptación | 66+ | 66+ | **100%** |
| Módulos de código | 6 | 6 | **100%** |
| Archivos de test | 11 | 11 | **100%** |
| Tests automatizados | 49+ | 49+ | **100%** |

---

## 1. Módulo `src/lsp_core.py` — Núcleo ML Testeable

| Función | HU | CA | Archivo de test | Estado |
|---------|----|----|----------------|--------|
| `cargar_modelo(path)` | HU-07, HU-10 | CA-07.3 (serialización), CA-10.1 (carga al iniciar) | `tests/test_modelo.py::test_cargar_modelo` | ✅ |
| `_get_hands(static_image_mode)` | HU-09 | CA-09.1 (MediaPipe inicializado), CA-09.3 (ROI estable) | `tests/test_landmarks.py::test_mediapipe_inicializa` | ✅ |
| `extraer_landmarks(img, mode)` | HU-06, HU-09 | CA-06.1 (extracción 21 puntos), CA-06.2 (normalización), CA-09.1 | `tests/test_landmarks.py::test_extraer_landmarks_imagen_valida` | ✅ |
| `extraer_landmarks_de_archivo(path)` | HU-06 | CA-06.1 (desde archivo PNG), CA-06.3 (integridad) | `tests/test_landmarks.py::test_extraer_landmarks_de_archivo` | ✅ |
| `landmarks_validos(landmarks)` | HU-06, HU-10 | CA-06.3 (integridad), CA-10.2 (validación previa) | `tests/test_validacion.py::test_landmarks_validos_*` | ✅ |
| `predecir(modelo, landmarks)` | HU-07, HU-10 | CA-07.2 (precision ≥85%), CA-10.2 (≤0.4s), CA-10.3 (confianza%) | `tests/test_modelo.py::test_prediccion_retorna_letra_y_confianza` | ✅ |
| `cargar_dataset(folder, limite)` | HU-05, HU-07 | CA-05.3 (formato), CA-07.1 (split train/test) | `tests/test_validacion.py::test_cargar_dataset_formato` | ✅ |
| `imagenes_disponibles(folder)` | HU-04 | CA-04.2 (organización en `data/<letra>/`) | `tests/test_validacion.py::test_imagenes_disponibles` | ✅ |
| `calcular_hash_modelo(path)` | HU-21 (Seguridad) | — integridad PKL SHA-256 | `tests/test_seguridad.py::TestIntegridadModelo` | ✅ |
| `verificar_integridad_modelo(path, hash)` | HU-21 (Seguridad) | — validación antes de cargar | `tests/test_seguridad.py::TestIntegridadModelo` | ✅ |
| `close_hands()` | HU-22 | CA-22.3 (libera recursos MediaPipe) | `tests/test_errores.py::test_close_hands_libera_recursos` | ✅ |

---

## 2. Módulo `src/lsp_video.py` — Procesador WebRTC

| Función / Clase | HU | CA | Archivo de test | Estado |
|-----------------|----|----|----------------|--------|
| `Traductor.__init__(modelo)` | HU-08, HU-09 | CA-08.1 (stream inicia), CA-09.1 (MediaPipe listo) | `tests/test_video.py::test_traductor_crea_instancia` | ✅ |
| `Traductor.recv(frame)` | HU-08, HU-09, HU-10 | CA-08.3 (frames procesados), CA-09.2 (skeleton), CA-10.2 (≤0.4s) | `tests/test_video.py::test_recv_retorna_frame_anotado` | ✅ |
| `Traductor.fps` con EMA α=0.2 | HU-22 | CA-22.1 (FPS ≥24 en 60s, suavizado) | `qa/fps_test.py` | ✅ |
| `Traductor.lock` (threading.Lock) | HU-08 | CA-08.4 (sin race conditions) | `tests/test_video.py::test_thread_safety_concurrent_reads` | ✅ |
| Resize 320×240 antes de MediaPipe | HU-22 | CA-22.1 (CPU < 80% en laptops gama media) | `tests/test_video.py`, `qa/benchmark.py` | ✅ |

---

## 3. Módulo `src/lsp_auth.py` — Autenticación HMAC

| Función | HU | CA | Archivo de test | Estado |
|---------|----|----|----------------|--------|
| `hash_password(password)` | HU-13 | CA-13.1 (PBKDF2-HMAC-SHA256, 260k iteraciones) | `tests/test_auth.py::test_hash_password_produce_hex` | ✅ |
| `generar_token_sesion(pwd, hash)` | HU-13 | CA-13.2 (token formato `ts.nonce.firma`) | `tests/test_auth.py::test_generar_token_formato_correcto` | ✅ |
| `verificar_token(token)` | HU-13 | CA-13.3 (rechaza expirados/manipulados) | `tests/test_auth.py::test_token_expirado`, `test_token_manipulado` | ✅ |
| `login_requerido(st_state)` | HU-13 | CA-13.4 (guard de acceso), CA-13.5 (redirige sin auth) | `tests/test_auth.py::test_login_requerido_*` | ✅ |
| `esta_bloqueado()` | HU-13 (Rate Limiting) | — bloqueo tras 5 intentos, 300 s | `tests/test_seguridad.py::TestRateLimiting` | ✅ |
| `_firmar(ts_str, nonce)` | HU-13 | CA-13.6 (HMAC resistente a XSS) | `tests/test_auth.py::test_firma_resiste_inyeccion_xss` | ✅ |
| `_render_login(st, st_state)` | HU-13, HU-15 | CA-13.2 (formulario funcional), CA-15.1 (accesibilidad) | `tests/test_auth.py::test_render_login_*` | ✅ |

---

## 4. Módulo `src/lsp_audit.py` — Log de Auditoría Anónimo

| Función | HU | CA | Archivo de test | Estado |
|---------|----|----|----------------|--------|
| `registrar_acceso(evento, detalle, st_state)` | HU-14 | CA-14.1 (registra evento), CA-14.2 (sin PII) | `tests/test_audit.py::test_registrar_acceso_crea_entrada` | ✅ |
| `leer_log_reciente(n)` | HU-14, HU-17 | CA-14.3 (log legible), CA-17.3 (dashboard lee log) | `tests/test_audit.py::test_leer_log_reciente_retorna_lista` | ✅ |
| `purgar_log_antiguo(dias)` | HU-14, HU-20 | CA-14.4 (retención 7 días), privacidad GDPR | `tests/test_audit.py::test_purgar_log_elimina_antiguos` | ✅ |
| `_id_sesion(st_state)` | HU-14 | CA-14.2 (ID anónimo SHA-256[:8], no reversible) | `tests/test_audit.py::test_id_sesion_es_anonimo` | ✅ |
| Formato JSON Lines | HU-14 | CA-14.1 (campos: ts, evento, sesion, detalle) | `tests/test_audit.py::test_formato_json_lines` | ✅ |

---

## 5. Módulo `src/lsp_ui.py` — Componentes WCAG 2.1 AA

| Función | HU | CA | Verificación | Estado |
|---------|----|----|-------------|--------|
| `render_estilos()` | HU-15 | CA-15.2 (contraste ≥4.5:1: `#6b6b6b`, `#767676`), CA-15.3 (skip-nav CSS) | Chrome DevTools Accessibility | ✅ |
| `render_skip_nav()` | HU-15 | CA-15.3 (WCAG 2.4.1 — enlace visible al Tab) | Verificación manual (Tab focus) | ✅ |
| `render_topbar(n_senas)` | HU-12 | CA-12.2 (interfaz muestra estado) | Inspección visual | ✅ |
| `render_hero()` | HU-12 | CA-12.2 (h1 semántico, instrucciones) | Inspección visual | ✅ |
| `render_resultado(letra, conf, mano)` | HU-10, HU-15 | CA-10.3 (borde rojo/amarillo), CA-15.1 (`aria-live="polite"`) | `tests/test_etica.py::test_umbral_confianza_60_documentado_en_ui` | ✅ |
| `render_pipeline_explicado()` | HU-16 | CA-16.1 (pipeline 5 etapas), CA-16.2 (limitaciones documentadas) | `tests/test_etica.py::test_pipeline_explicado_menciona_limitaciones` | ✅ |
| `render_estado_sistema(n, modelo_ok)` | HU-12 | CA-12.3 (estado del sistema visible) | Inspección visual | ✅ |
| `render_estadisticas(n, fps)` | HU-17 | CA-17.1 (4 tarjetas de métricas) | Inspección visual | ✅ |
| `render_footer()` | HU-15 | CA-15.1 (`role="contentinfo"`) | Inspección HTML | ✅ |

---

## 6. `src/app.py` — Orquestador Principal

| Componente | HU | CA | Archivo de test | Estado |
|------------|----|----|----------------|--------|
| `st.set_page_config(...)` | HU-12 | CA-12.1 (configuración de página) | — | ✅ |
| `cargar_modelo()` `@st.cache_resource` | HU-10 | CA-10.1 (carga al iniciar, cacheada) | `tests/test_modelo.py::test_cargar_modelo` | ✅ |
| Guard `lsp_auth.login_requerido(...)` | HU-13 | CA-13.4 (guard antes de mostrar contenido) | `tests/test_auth.py::test_login_requerido_*` | ✅ |
| `lsp_audit.registrar_acceso(...)` | HU-14 | CA-14.1 (registra `PAGINA_VISITADA`) | `tests/test_audit.py` | ✅ |
| `webrtc_streamer(Traductor(...))` | HU-08 | CA-08.1 (stream activo) | `tests/test_integracion.py` | ✅ |
| `panel_resultado()` `@st.fragment` | HU-10, HU-11 | CA-10.2 (actualización ≤0.4s), CA-11.1 (historial) | `tests/test_integracion.py` | ✅ |
| `RTC_CONFIG` con STUN + TURN | HU-08 | CA-08.1 (NAT simétrico — redes universitarias) | Prueba manual en red UPN | ✅ |

---

## 7. `src/pages/1_Metricas_QA.py` — Dashboard de Calidad

| Componente | HU | CA | Herramienta | Estado |
|------------|----|----|-------------|--------|
| Guard `lsp_auth.login_requerido(...)` | HU-13, HU-17 | CA-13.4, CA-17.3 (solo autenticados) | `tests/test_auth.py` | ✅ |
| Tarjetas de métricas (accuracy, F1) | HU-17 | CA-17.1 (métricas accuracy/F1 visibles) | `qa/evaluate.py` | ✅ |
| Recursos en vivo (psutil) | HU-17, HU-22 | CA-17.2 (CPU/RAM en tiempo real) | `qa/recursos.py` | ✅ |
| Tabla benchmark | HU-22 | CA-22.2 (latencias por etapa ≤200ms) | `qa/benchmark.py` | ✅ |
| Tabla FPS | HU-22 | CA-22.1 (FPS ≥24 en 60s) | `qa/fps_test.py` | ✅ |
| Log de auditoría (últimas 20) | HU-14, HU-17 | CA-14.3 (trazabilidad), CA-17.3 | `tests/test_audit.py` | ✅ |

---

## 8. Scripts de Entrenamiento (`scripts/`)

| Script | HU | CA | Validación | Estado |
|--------|----|----|-----------|--------|
| `scripts/entrenar_modelo.py` | HU-07 | CA-07.1 (split 80/20), CA-07.3 (genera `modelo.pkl`) | Ejecución manual | ✅ |
| `scripts/augmentar_dataset.py` | HU-05 | CA-05.1 (×16 muestras por landmark) | Ejecución manual | ✅ |
| `scripts/entrenar_desde_csv.py` | HU-05 | CA-05.2 (diversidad colaborativa) | Ejecución manual | ✅ |
| `scripts/capturar_dataset.py` | HU-04, HU-05 | CA-04.3 (sin sobrescribir datos ajenos) | Ejecución manual | ✅ |
| `scripts/extraer_landmarks.py` | HU-05 | CA-05.2 (exporta CSV portátil) | Ejecución manual | ✅ |
| `scripts/traducir_en_vivo.py` | HU-10 | CA-10.2 (demo offline sin Streamlit) | Ejecución manual | ✅ |

---

## 9. Suite de Calidad (`qa/`)

| Script | HU | CA | Salida generada | Estado |
|--------|----|----|----------------|--------|
| `qa/benchmark.py` | HU-22 | CA-22.2 (etapa ≤200ms) | `reportes/benchmark.csv` | ✅ |
| `qa/fps_test.py` | HU-08, HU-22 | CA-08.4, CA-22.1 (FPS ≥24 en 60s) | `reportes/fps.csv` | ✅ |
| `qa/stress_test.py` | HU-22 | CA-22.3 (0 excepciones, sin memory leak) | `reportes/stress.csv` | ✅ |
| `qa/evaluate.py` | HU-07, HU-17 | CA-07.2 (accuracy ≥85%, F1 por clase) | `reportes/metricas_por_clase.csv` | ✅ |
| `qa/confusion_matrix.py` | HU-07, HU-17 | CA-07.2 (visualización de confusiones) | `reportes/matriz_confusion.png` | ✅ |
| `qa/cross_validation.py` | HU-07 | CA-07.2 (estabilidad K-Fold) | `reportes/cross_validation.csv` | ✅ |
| `qa/robustez.py` | HU-10 | CA-10.3 (degradación grácil en condiciones adversas) | `reportes/robustez.csv` | ✅ |
| `qa/recursos.py` | HU-22 | CA-22.4 (RAM ≤+50MB, CPU ≤80% en 300s) | `reportes/recursos.csv` | ✅ |
| `qa/generar_reportes.py` | HU-17, HU-21 | CA-17.1, CA-21.1 (reporte consolidado PDF) | `reportes/REPORTE_QA.pdf` | ✅ |

---

## 10. Suite de Tests (`tests/` + `test_sistema.py`)

| Archivo | Tests | HUs cubiertas | Cobertura |
|---------|-------|--------------|-----------|
| `tests/conftest.py` | Fixtures | Todas | Soporte |
| `tests/test_auth.py` | 14 | HU-13 | ✅ ≥90% lsp_auth |
| `tests/test_audit.py` | 9 | HU-14 | ✅ ≥90% lsp_audit |
| `tests/test_seguridad.py` | 20 | HU-13, HU-14, HU-20, HU-21 | ✅ DevSecOps 3 capas |
| `tests/test_etica.py` | 15 | HU-16, HU-20 | ✅ IA Ética y XAI |
| `tests/test_video.py` | 11 | HU-08, HU-09 | ✅ Thread-safety |
| `tests/test_integracion.py` | 3 | HU-10, HU-12 | ✅ Flujo E2E |
| `tests/test_landmarks.py` | 5+ | HU-06, HU-09 | ✅ ≥96% lsp_core |
| `tests/test_modelo.py` | 5+ | HU-07, HU-10 | ✅ |
| `tests/test_validacion.py` | 4+ | HU-05, HU-06 | ✅ |
| `tests/test_errores.py` | 3+ | HU-22 | ✅ |
| `test_sistema.py` | 18 | HU-01..HU-20 | ✅ UT-01..UT-18 |
| **Total** | **49+** | **22 HUs** | ✅ |

---

## 11. Cobertura de HUs por Módulo (Mapa Completo)

| HU | `lsp_core` | `lsp_video` | `lsp_auth` | `lsp_audit` | `lsp_ui` | `app.py` | `pages/` | `qa/` | `tests/` | Estado |
|----|:-----------:|:-----------:|:-----------:|:-----------:|:--------:|:--------:|:--------:|:-----:|:--------:|--------|
| HU-01 | — | — | — | — | — | — | — | — | `test_sistema.py` | ✅ |
| HU-02 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | ✅ |
| HU-03 | — | — | — | — | — | — | — | — | `test_sistema.py` | ✅ |
| HU-04 | ✅ | — | — | — | — | — | — | — | `test_validacion.py` | ✅ |
| HU-05 | ✅ | — | — | — | — | — | — | — | `test_validacion.py` | ✅ |
| HU-06 | ✅ | — | — | — | — | — | — | — | `test_landmarks.py` | ✅ |
| HU-07 | ✅ | — | — | — | — | — | — | ✅ | `test_modelo.py` | ✅ |
| HU-08 | — | ✅ | — | — | — | ✅ | — | ✅ | `test_video.py` | ✅ |
| HU-09 | ✅ | ✅ | — | — | — | — | — | — | `test_landmarks.py` | ✅ |
| HU-10 | ✅ | ✅ | — | — | ✅ | ✅ | — | ✅ | `test_modelo.py` | ✅ |
| HU-11 | — | — | — | — | ✅ | ✅ | — | — | `test_sistema.py` | ✅ |
| HU-12 | — | — | — | — | ✅ | ✅ | — | — | `test_integracion.py` | ✅ |
| HU-13 | — | — | ✅ | — | — | ✅ | ✅ | — | `test_auth.py` | ✅ |
| HU-14 | — | — | — | ✅ | — | ✅ | ✅ | — | `test_audit.py` | ✅ |
| HU-15 | — | — | — | — | ✅ | — | — | — | `test_etica.py` | ✅ |
| HU-16 | — | — | — | — | ✅ | ✅ | — | — | `test_etica.py` | ✅ |
| HU-17 | — | — | — | ✅ | ✅ | — | ✅ | ✅ | — | ✅ |
| HU-18 | — | — | — | — | — | — | — | — | ✅ (suite completa) | ✅ |
| HU-19 | — | — | — | — | — | — | — | — | `docs/plantilla_UAT.md` | ✅ |
| HU-20 | — | — | — | ✅ | — | — | — | — | `test_seguridad.py` | ✅ |
| HU-21 | — | — | — | — | — | — | — | — | `Dockerfile` | ✅ |
| HU-22 | — | ✅ | — | — | — | — | ✅ | ✅ | `test_video.py` | ✅ |

> ✅ = el módulo implementa al menos un CA de esa HU.

---

## Historial de Versiones

| Versión | Fecha | Cambio |
|---------|-------|--------|
| 1.0 | 2026-06-12 | Versión inicial — trazabilidad de 8 módulos, 22 HUs, 49+ tests |
| 2.0 | 2026-06-13 | Actualización post-reingeniería: `src/`-layout, `scripts/`, estado ✅ en todas las HUs, tabla de cobertura por módulo completa |
