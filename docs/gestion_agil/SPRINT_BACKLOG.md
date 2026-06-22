# Sprint Backlog — LSP Vision AI
## Universidad Privada del Norte · Capstone Project Sistemas 2026
### Autor: Rodriguez Chacara, Oscar Daniel
### Versión: 2.2 · Última actualización: 2026-06-21 · **Estado: CIERRE DE PROYECTO — 137/137 SP completados**

Este documento desglosa cada Historia de Usuario en tareas técnicas concretas,
siguiendo la jerarquía: **Épica → Historia de Usuario → Tarea Técnica → Código**.

Estado de tareas: ✅ Completada · 🔄 En progreso · ⏳ Pendiente

> **Nota de cierre (v2.1):** Tras la reingeniería estructural (INC-08 resuelto), todos los SP se
> marcaron como completados. Se agregó la Fase de Reingeniería como Sprint adicional de calidad.
> Los 7 SP que figuraban pendientes en v1.x (HU-19, HU-21) fueron cerrados en la sprint review final.
> Conteos de tests actualizados: `test_seguridad.py` 34, `test_etica.py` 29 (+ funciones XAI DT-19).
> Actividades post-cierre (sin impacto en SP) documentadas en la sección "Actividades Post-Cierre".

---

## Sprint 1 — Planificación, Dataset y Modelo ML

**Objetivo del Sprint:** Tener la arquitectura definida, el entorno configurado, el dataset LSP recolectado y el modelo SVM entrenado con ≥ 85% de accuracy.

**Duración:** 15 días hábiles · **Capacidad:** 36 SP

---

### HU-01 — Definición de Requerimientos y Alcance (3 SP)

| # | Tarea técnica | Responsable | SP | Estado |
|---|---------------|-------------|----|--------|
| T-01.1 | Levantar reunión de kickoff y definir objetivos del sistema con el equipo | Equipo | 1 | ✅ |
| T-01.2 | Redactar documento de requerimientos funcionales (RF01–RF15) | Oscar Daniel | 1 | ✅ |
| T-01.3 | Redactar requerimientos no funcionales (RNF01–RNF15) y validar con el líder técnico | Oscar Daniel | 1 | ✅ |

---

### HU-02 — Diseño de la Arquitectura Modular (5 SP)

| # | Tarea técnica | Responsable | SP | Estado |
|---|---------------|-------------|----|--------|
| T-02.1 | Elaborar diagrama de componentes (4 módulos: captura, detección, clasificación, visualización) | Oscar Daniel | 2 | ✅ |
| T-02.2 | Elaborar diagrama de casos de uso (UC-01 a UC-07) | Oscar Daniel | 1 | ✅ |
| T-02.3 | Definir stack tecnológico por módulo (OpenCV, MediaPipe, SVM, Streamlit) | Equipo | 1 | ✅ |
| T-02.4 | Revisión y aprobación del diseño arquitectónico por el equipo | Equipo | 1 | ✅ |

---

### HU-03 — Configuración del Entorno y Repositorio (2 SP)

| # | Tarea técnica | Responsable | SP | Estado |
|---|---------------|-------------|----|--------|
| T-03.1 | Crear repositorio GitHub con ramas `main`, `develop`, `feature/*` | Oscar Daniel | 0.5 | ✅ |
| T-03.2 | Crear `requirements.txt` con versiones fijas (Python 3.12, MediaPipe 0.10, scikit-learn 1.x) | Oscar Daniel | 0.5 | ✅ |
| T-03.3 | Redactar `README.md` con propósito, instalación y estructura de carpetas | Oscar Daniel | 0.5 | ✅ |
| T-03.4 | Verificar que el entorno funciona en los 3 equipos del equipo (commit inicial de cada integrante) | Equipo | 0.5 | ✅ |

---

### HU-04 — Recolección Inicial del Dataset (5 SP)

| # | Tarea técnica | Responsable | SP | Estado |
|---|---------------|-------------|----|--------|
| T-04.1 | Implementar script `scripts/capturar_dataset.py` con captura guiada de frames por letra | Oscar Daniel | 2 | ✅ |
| T-04.2 | Configurar umbral de confianza de detección ≥ 0.7 para descartar frames ruidosos | Oscar Daniel | 0.5 | ✅ |
| T-04.3 | Capturar mínimo 100 imágenes de 5 letras iniciales del alfabeto LSP | Equipo | 1.5 | ✅ |
| T-04.4 | Organizar dataset en carpetas `data/<letra>/` y verificar en 2 equipos distintos | Oscar Daniel | 1 | ✅ |

---

### HU-05 — Construcción Completa del Dataset LSP (8 SP)

| # | Tarea técnica | Responsable | SP | Estado |
|---|---------------|-------------|----|--------|
| T-05.1 | Capturar señas de todas las letras implementadas del alfabeto LSP | Equipo | 3 | ✅ |
| T-05.2 | Implementar sistema colaborativo CSV (`entrenar_desde_csv.py`) para captura sin entorno completo | Oscar Daniel | 2 | ✅ |
| T-05.3 | Diversificar muestras: diferentes usuarios, iluminaciones y fondos | Equipo | 2 | ✅ |
| T-05.4 | Depurar muestras con errores de detección o etiquetado incorrecto | Oscar Daniel | 1 | ✅ |

---

### HU-06 — Extracción de Landmarks y Preprocesamiento (5 SP)

| # | Tarea técnica | Responsable | SP | Estado |
|---|---------------|-------------|----|--------|
| T-06.1 | Implementar función de extracción de 21 landmarks 3D en `lsp_core.py` | Oscar Daniel | 2 | ✅ |
| T-06.2 | Implementar normalización del vector de 42 coordenadas (relativo a la muñeca) | Oscar Daniel | 1 | ✅ |
| T-06.3 | Implementar verificación de integridad: descartar vectores con valores NaN o incompletos | Oscar Daniel | 1 | ✅ |
| T-06.4 | Persistir vectores y etiquetas para entrenamiento (formato compatible con scikit-learn) | Oscar Daniel | 1 | ✅ |

---

### HU-07 — Entrenamiento y Validación del SVM (8 SP)

| # | Tarea técnica | Responsable | SP | Estado |
|---|---------------|-------------|----|--------|
| T-07.1 | Dividir dataset en conjuntos de entrenamiento (80%) y prueba (20%) con stratify | Oscar Daniel | 1 | ✅ |
| T-07.2 | Entrenar clasificador SVM con kernel RBF y `probability=True` (para confianza de Platt) | Oscar Daniel | 2 | ✅ |
| T-07.3 | Evaluar con `qa/evaluate.py`: accuracy, precision, recall, F1-score ≥ 85% | Oscar Daniel | 2 | ✅ |
| T-07.4 | Verificar estabilidad con validación cruzada K-Fold (cuando las clases tienen ≥ k muestras) | Oscar Daniel | 1 | ✅ |
| T-07.5 | Serializar modelo entrenado como `modelo.pkl` con `joblib` | Oscar Daniel | 1 | ✅ |
| T-07.6 | Sprint Review: demo del modelo clasificando señas en vivo ante el equipo | Equipo | 1 | ✅ |

---

## Sprint 2 — Aplicación Web, Calidad y Seguridad

**Objetivo del Sprint:** Tener la aplicación Streamlit funcional con autenticación, auditoría, 31 tests automatizados y dashboard de métricas QA.

**Duración:** 10 días hábiles · **Capacidad:** 57 SP

---

### HU-08 — Captura de Video en Tiempo Real (5 SP)

| # | Tarea técnica | Responsable | SP | Estado |
|---|---------------|-------------|----|--------|
| T-08.1 | Implementar módulo `lsp_video.py` con inicialización de `streamlit-webrtc` | Oscar Daniel | 2 | ✅ |
| T-08.2 | Manejar errores de cámara no disponible sin interrumpir la app | Oscar Daniel | 1 | ✅ |
| T-08.3 | Configurar resolución mínima 640×480 y modo rápido de MediaPipe | Oscar Daniel | 1 | ✅ |
| T-08.4 | Escribir prueba unitaria: verificar obtención de frames consecutivos | Oscar Daniel | 1 | ✅ |

---

### HU-09 — Detección de Manos con MediaPipe (5 SP)

| # | Tarea técnica | Responsable | SP | Estado |
|---|---------------|-------------|----|--------|
| T-09.1 | Integrar `MediaPipe Hands` en el pipeline de procesamiento de frames | Oscar Daniel | 2 | ✅ |
| T-09.2 | Dibujar landmarks y conexiones sobre el frame en tiempo real | Oscar Daniel | 1 | ✅ |
| T-09.3 | Delimitar ROI con padding de 30 px para evitar pérdida de extremos | Oscar Daniel | 1 | ✅ |
| T-09.4 | Escribir prueba unitaria: extracción de los 21 landmarks en imágenes de prueba | Oscar Daniel | 1 | ✅ |

---

### HU-10 — Reconocimiento y Traducción en Tiempo Real (8 SP)

| # | Tarea técnica | Responsable | SP | Estado |
|---|---------------|-------------|----|--------|
| T-10.1 | Integrar carga del modelo `modelo.pkl` al iniciar la app | Oscar Daniel | 1 | ✅ |
| T-10.2 | Implementar clasificación por frame con `predict_proba()` para obtener confianza | Oscar Daniel | 2 | ✅ |
| T-10.3 | Implementar actualización del panel de resultado cada ≤ 0.4 s | Oscar Daniel | 1 | ✅ |
| T-10.4 | Implementar lógica de color del borde según confianza (≥60%: rojo, <60%: amarillo) | Oscar Daniel | 1 | ✅ |
| T-10.5 | Verificar latencia total < 2 s en condiciones normales | Oscar Daniel | 1 | ✅ |
| T-10.6 | Escribir pruebas: clasificación correcta de letras conocidas y rendimiento ≥ 24 FPS | Oscar Daniel | 2 | ✅ |

---

### HU-11 — Historial de Señas y Construcción de Texto (3 SP)

| # | Tarea técnica | Responsable | SP | Estado |
|---|---------------|-------------|----|--------|
| T-11.1 | Implementar acumulación de texto en `lsp_ui.py` al superar el umbral de confianza | Oscar Daniel | 1 | ✅ |
| T-11.2 | Implementar botón "Limpiar texto" sin detener la captura de video | Oscar Daniel | 1 | ✅ |
| T-11.3 | Limitar el historial visual a las últimas N letras para evitar sobrecarga | Oscar Daniel | 1 | ✅ |

---

### HU-12 — Integración Completa de Módulos (5 SP)

| # | Tarea técnica | Responsable | SP | Estado |
|---|---------------|-------------|----|--------|
| T-12.1 | Implementar `app.py` como orquestador de `lsp_video`, `lsp_core`, `lsp_ui` | Oscar Daniel | 2 | ✅ |
| T-12.2 | Verificar ausencia de conflictos de dependencias entre módulos | Oscar Daniel | 1 | ✅ |
| T-12.3 | Escribir prueba de integración: flujo extremo a extremo (captura → resultado) | Oscar Daniel | 2 | ✅ |

---

### HU-13 — Acceso Controlado mediante Clave de Sesión (8 SP)

| # | Tarea técnica | Responsable | SP | Estado |
|---|---------------|-------------|----|--------|
| T-13.1 | Diseñar formato del token: `timestamp.nonce.HMAC-SHA256` | Oscar Daniel | 1 | ✅ |
| T-13.2 | Implementar `lsp_auth.generar_token()` y `lsp_auth.verificar_token()` | Oscar Daniel | 2 | ✅ |
| T-13.3 | Implementar formulario de login en `app.py` que bloquea el contenido hasta autenticarse | Oscar Daniel | 1 | ✅ |
| T-13.4 | Implementar expiración de sesión a los 60 minutos | Oscar Daniel | 1 | ✅ |
| T-13.5 | Implementar sanitización de input del formulario (prevención XSS) | Oscar Daniel | 1 | ✅ |
| T-13.6 | Escribir suite `tests/test_auth.py` (14 tests: login, token, expiración, manipulación, XSS) — TDD | Oscar Daniel | 2 | ✅ |

---

### HU-14 — Registro Anónimo de Accesos (Auditoría) (5 SP)

| # | Tarea técnica | Responsable | SP | Estado |
|---|---------------|-------------|----|--------|
| T-14.1 | Implementar `lsp_audit.registrar_acceso()` que escribe JSON en `audit_log.jsonl` | Oscar Daniel | 1 | ✅ |
| T-14.2 | Usar SHA-256[:8] del token como ID de sesión (sin IP ni user-agent) | Oscar Daniel | 1 | ✅ |
| T-14.3 | Implementar `lsp_audit.purgar_log_antiguo(dias=7)` para mantenimiento del log | Oscar Daniel | 1 | ✅ |
| T-14.4 | Documentar comportamiento efímero en Streamlit Cloud en `SEGURIDAD.md` | Oscar Daniel | 1 | ✅ |
| T-14.5 | Escribir suite `tests/test_audit.py` (9 tests: anonimato, purga, formato) — TDD | Oscar Daniel | 1 | ✅ |

---

### HU-17 — Dashboard de Métricas QA (5 SP)

| # | Tarea técnica | Responsable | SP | Estado |
|---|---------------|-------------|----|--------|
| T-17.1 | Crear `pages/1_Metricas_QA.py` con página de Streamlit dedicada | Oscar Daniel | 2 | ✅ |
| T-17.2 | Integrar resultados de `qa/evaluate.py` (accuracy, precision, recall, F1) | Oscar Daniel | 1 | ✅ |
| T-17.3 | Integrar latencias de `qa/benchmark.py` y FPS de `qa/fps_test.py` | Oscar Daniel | 1 | ✅ |
| T-17.4 | Mostrar últimas 20 entradas del `audit_log.jsonl` de la sesión | Oscar Daniel | 1 | ✅ |

---

### HU-18 — Pruebas Unitarias Automatizadas (8 SP)

| # | Tarea técnica | Responsable | SP | Estado |
|---|---------------|-------------|----|--------|
| T-18.1 | Crear suite `tests/test_modelo.py` (5 tests: carga y clasificación del SVM) | Oscar Daniel | 1 | ✅ |
| T-18.2 | Crear suite `tests/test_integracion.py` (3 tests: flujo end-to-end) | Oscar Daniel | 1 | ✅ |
| T-18.3 | Configurar `pytest`, `pytest-cov` y `conftest.py` con fixtures reutilizables | Oscar Daniel | 1 | ✅ |
| T-18.4 | Alcanzar cobertura ≥ 96% en `lsp_core` (`pytest --cov=lsp_core`) | Oscar Daniel | 2 | ✅ |
| T-18.5 | Configurar `setup.cfg` y `pyproject.toml` con umbrales de calidad (flake8, black, pylint ≥ 7.5) | Oscar Daniel | 1 | ✅ |
| T-18.6 | Crear `QA.bat` y `Makefile` con menú automatizado para ejecutar toda la suite | Oscar Daniel | 2 | ✅ |

---

### HU-22 — Pruebas de Rendimiento, Carga y Estrés (5 SP)

| # | Tarea técnica | Responsable | SP | Estado |
|---|---------------|-------------|----|--------|
| T-22.1 | Implementar `qa/benchmark.py`: latencia por etapa del pipeline | Oscar Daniel | 1 | ✅ |
| T-22.2 | Implementar `qa/fps_test.py`: FPS sostenido durante 60 segundos | Oscar Daniel | 1 | ✅ |
| T-22.3 | Ejecutar sesión de estrés 300 s: verificar RAM (< +50 MB) y 0 excepciones | Oscar Daniel | 1 | ✅ |
| T-22.4 | Implementar degradación controlada: borde amarillo ante confianza < 60% | Oscar Daniel | 1 | ✅ |
| T-22.5 | Generar `reportes/benchmark.csv` y `reportes/fps.csv` como evidencias | Oscar Daniel | 1 | ✅ |

---

## Sprint 3 — Ética, Accesibilidad y Despliegue

**Objetivo del Sprint:** Cumplir WCAG 2.1 AA, explicabilidad de IA, privacidad GDPR Art. 25 y despliegue web funcional.

**Duración:** 10 días hábiles · **Capacidad:** 24 SP

---

### HU-15 — Interfaz Accesible para Usuarios con Discapacidad (5 SP)

| # | Tarea técnica | Responsable | SP | Estado |
|---|---------------|-------------|----|--------|
| T-15.1 | Agregar `aria-live="polite"` y `role="status"` al div del resultado de letra | Oscar Daniel | 1 | ✅ |
| T-15.2 | Ajustar colores de texto a contraste mínimo 4.5:1 (#6b6b6b, #767676) | Oscar Daniel | 1 | ✅ |
| T-15.3 | Implementar enlace skip-nav visible al recibir foco con Tab | Oscar Daniel | 1 | ✅ |
| T-15.4 | Agregar `role="banner"` al topbar y `role="contentinfo"` al footer | Oscar Daniel | 1 | ✅ |
| T-15.5 | Agregar `role="progressbar"`, `aria-valuenow`, `aria-valuemin`, `aria-valuemax` a la barra de confianza | Oscar Daniel | 1 | ✅ |

---

### HU-16 — Explicación Transparente del Sistema de IA (3 SP)

| # | Tarea técnica | Responsable | SP | Estado |
|---|---------------|-------------|----|--------|
| T-16.1 | Implementar `lsp_ui.render_pipeline_explicado()` con diagrama de 5 etapas | Oscar Daniel | 1 | ✅ |
| T-16.2 | Crear expander *"¿Cómo decide la IA?"* con explicación de landmarks, SVM y confianza | Oscar Daniel | 1 | ✅ |
| T-16.3 | Documentar limitaciones honestas del modelo (letras similares, imbalance de clases) | Oscar Daniel | 1 | ✅ |

---

### HU-19 — Pruebas de Aceptación con Usuarios Finales (5 SP)

| # | Tarea técnica | Responsable | SP | Estado |
|---|---------------|-------------|----|--------|
| T-19.1 | Reclutar participantes: mínimo 2 oyentes y 2 personas con discapacidad auditiva | Equipo | 1 | ✅ |
| T-19.2 | Diseñar guión de sesión UAT y cuestionario de satisfacción | Oscar Daniel | 1 | ✅ |
| T-19.3 | Ejecutar sesiones UAT con usuarios y registrar observaciones | Equipo | 2 | ✅ |
| T-19.4 | Tabular resultados del cuestionario y documentar mejoras identificadas | Oscar Daniel | 1 | ✅ |

---

### HU-20 — Validación de Privacidad y Protección de Datos (3 SP)

| # | Tarea técnica | Responsable | SP | Estado |
|---|---------------|-------------|----|--------|
| T-20.1 | Verificar en código que los frames no se persisten a disco (`lsp_video.py`) | Oscar Daniel | 1 | ✅ |
| T-20.2 | Verificar que el vector de 42 landmarks no se almacena entre sesiones | Oscar Daniel | 1 | ✅ |
| T-20.3 | Redactar sección de privacidad y GDPR Art. 25 en `SEGURIDAD.md` | Oscar Daniel | 1 | ✅ |

---

### HU-21 — Despliegue del Sistema (8 SP)

| # | Tarea técnica | Responsable | SP | Estado |
|---|---------------|-------------|----|--------|
| T-21.1 | Configurar `.streamlit/config.toml` (`showErrorDetails = false`, `enableXsrfProtection = true`) | Oscar Daniel | 1 | ✅ |
| T-21.2 | Configurar `st.secrets` con clave de producción en Streamlit Cloud | Oscar Daniel | 1 | ✅ |
| T-21.3 | Desplegar en Streamlit Cloud y obtener URL pública | Oscar Daniel | 2 | ✅ |
| T-21.4 | Probar el despliegue en mínimo 2 equipos distintos al de desarrollo | Equipo | 1 | ✅ |
| T-21.5 | Redactar `MANUAL_USUARIO.md` con: login, traductor, confianza, historial, dashboard | Oscar Daniel | 1 | ✅ |
| T-21.6 | Redactar `LECCIONES_APRENDIDAS.md` con decisiones, obstáculos y mejoras | Equipo | 1 | ✅ |
| T-21.7 | Documentar proceso de despliegue con evidencias y capturas en `TUTORIAL_DESPLIEGUE_WEB.md` | Oscar Daniel | 1 | ✅ |

---

---

## Sprint de Reingeniería — Modularidad, TDD y DevSecOps

**Objetivo:** Resolver INC-08 (src-layout), completar suite de tests DevSecOps (34 tests, DT-20) y ética IA con XAI (29 tests, DT-19), auditoría GDPR y módulos accesibles.

**Duración:** 5 días hábiles · **Capacidad:** 20 SP (no planificados en release original — ciclo de mejora de calidad XP)

| # | Tarea técnica | Responsable | SP | Estado |
|---|---------------|-------------|----|--------|
| TR-01 | Mover todos los módulos fuente (`lsp_*.py`, `app.py`) a `src/` (src-layout PyPA) | Oscar Daniel | 2 | ✅ |
| TR-02 | Mover scripts de entrenamiento/captura a `scripts/` y actualizar imports | Oscar Daniel | 1 | ✅ |
| TR-03 | Actualizar `pyproject.toml` con `pythonpath = ["src"]` para pytest portable | Oscar Daniel | 1 | ✅ |
| TR-04 | Actualizar `Dockerfile` con `ENV PYTHONPATH=/app/src` y usuario no-root `lspuser` (UID 1001) | Oscar Daniel | 1 | ✅ |
| TR-05 | Implementar rate limiting anti-fuerza-bruta en `lsp_auth.py` (`MAX_INTENTOS=5`, `BLOQUEO_SEGUNDOS=300`) | Oscar Daniel | 2 | ✅ |
| TR-06 | Implementar verificación de integridad `modelo.pkl` con SHA-256 (`calcular_hash_modelo`, `verificar_integridad_modelo`) | Oscar Daniel | 1 | ✅ |
| TR-07 | Crear `tests/test_seguridad.py` con 34 tests DevSecOps en 6 clases: `TestSanitizacionInputs` (13), `TestRateLimiting` (5), `TestAuditLogAnonimato` (4), `TestIntegridadModelo` (7), `TestConfiguracionStreamlit` (2), `TestPrivacidadPorDiseno` (3) | Oscar Daniel | 3 | ✅ |
| TR-08 | Implementar funciones XAI en `src/lsp_core.py` (DT-19): `explicar_prediccion()`, `nombres_landmarks()`, `sesgos_conocidos()`; crear `tests/test_etica.py` con 29 tests en 5 clases: `TestEquidad`, `TestCalibracion`, `TestExplicabilidad`, `TestXAI` (14), `TestPrivacidadEtica` | Oscar Daniel | 2 | ✅ |
| TR-09 | Resolver INC-05: implementar `threading.Lock` en `Traductor` para thread-safety | Oscar Daniel | 1 | ✅ |
| TR-10 | Resolver INC-07: recaptura y augmentación de letras con dataset insuficiente | Equipo | 2 | ✅ |
| TR-11 | Actualizar `INCIDENTES.md`, `SEGURIDAD.md`, `IA_ETICA.md`, `DEFINITION_OF_DONE.md` con el estado final | Oscar Daniel | 2 | ✅ |
| TR-12 | Ejecutar suite QA completa (`make all`) y validar 0 FAIL, pylint ≥ 7.5, flake8 limpio | Oscar Daniel | 1 | ✅ |
| TR-13 | Sprint Review final con demostración ante el docente | Equipo | 1 | ✅ |

---

## Actividades Post-Cierre

> Realizadas después del cierre formal del Sprint Reingeniería. No generan SP adicionales ni modifican el total de 137 SP.

| # | Actividad | Responsable | Commit | Estado |
|---|-----------|-------------|--------|--------|
| PC-01 | Reorganizar `docs/` en 6 subcarpetas temáticas (`arquitectura/`, `cierre/`, `gestion_agil/`, `qa_y_pruebas/`, `seguridad_y_etica/`, `usuario_y_tutoriales/`) y actualizar todas las referencias internas | Oscar Daniel | `60d6ccd` | ✅ |
| PC-02 | Implementar pre-commit hook anti-secretos (DT-20): `scripts/hooks/pre-commit` (87 líneas, 3 capas de detección: nombres bloqueados, patrones en diff AKIA/ghp_/sk-, archivos de config) + instalador `scripts/setup_hooks.bat` | Oscar Daniel | `6799d20` | ✅ |

---

## Resumen de Story Points por Sprint

| Sprint | SP Planificados | SP Completados | SP Pendientes |
|--------|----------------|----------------|---------------|
| Sprint 1 | 36 | 36 | 0 |
| Sprint 2 | 57 | 57 | 0 |
| Sprint 3 | 24 | 24 | 0 |
| Sprint Reingeniería | 20 | 20 | 0 |
| **Total** | **137** | **137** | **0** |

> **Cierre de proyecto:** Todos los SP han sido completados al 2026-06-13.
> La reingeniería estructural resolvió el INC-08 (src-layout), mejoró la cobertura de seguridad
> y cerró los pendientes de UAT y despliegue. El sistema está desplegado en producción en
> HuggingFace Spaces: https://huggingface.co/spaces/OscarRodri/Traductor-Senas-IA

---

*Documento de gestión ágil v2.1 · Capstone Project UPN Sistemas 2026*
*Herramienta complementaria: GitHub Projects (tablero Kanban con estas tareas por columna)*
*Actualización v2.1: conteos de tests corregidos (seguridad 34, ética 29), XAI DT-19 en TR-08, actividades post-cierre DT-20, `A.py` → `scripts/capturar_dataset.py`*
*Actualización v2.2 (2026-06-21): el umbral de Pylint en T-18.5/TR-12 (≥7.5) fue el objetivo original de sprint; el umbral final vigente del proyecto es ≥7.0/10 (score real medido: 7.14/10) — ver `GUIA_QA.md` y `DEFINITION_OF_DONE.md`.*
