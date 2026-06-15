---
title: Traductor Senas IA
emoji: 🤟
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# Sistema Interactivo de Visión Artificial para la Comunicación Inclusiva de Personas con Discapacidad Auditiva (LSP)

### Universidad Privada del Norte (UPN)
* **Facultad de Ingeniería**
* **Carrera de Ingeniería de Sistemas Computacionales**
* **Curso:** Capstone Project Sistemas (2026-1)
* **Docente:** Edward Jose Flores Masias

[![GitHub](https://img.shields.io/badge/GitHub-Repositorio-181717?logo=github)](https://github.com/Oscar-Rodriguez-2022/Traductor-Senas-IA)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Tests-143%20PASS-brightgreen)](tests/)
[![License](https://img.shields.io/badge/Licencia-MIT-blue)](LICENSE)

---

## Acceso Rápido — Gestión Ágil y Documentación

| Categoría | Documentos clave |
|---|---|
| **Scrum** | [Historias de Usuario](docs/gestion_agil/HISTORIAS_USUARIO.md) · [Sprint Backlog](docs/gestion_agil/SPRINT_BACKLOG.md) · [Burndown Charts](docs/gestion_agil/BURNDOWN_CHART.md) · [DoD v2.1](docs/gestion_agil/DEFINITION_OF_DONE.md) |
| **Calidad / TDD** | [Guía QA](docs/qa_y_pruebas/GUIA_QA.md) · [Incidentes](docs/qa_y_pruebas/INCIDENTES.md) · [Lecciones Aprendidas](docs/cierre/LECCIONES_APRENDIDAS.md) |
| **Seguridad y Ética** | [Plan de Seguridad](docs/seguridad_y_etica/SEGURIDAD.md) · [IA Ética / XAI](docs/seguridad_y_etica/IA_ETICA.md) · [Matriz de Trazabilidad](docs/gestion_agil/MATRIZ_TRAZABILIDAD.md) |
| **Despliegue** | [Hugging Face (Docker)](docs/usuario_y_tutoriales/TUTORIAL_HUGGINGFACE.md) · [Streamlit Cloud](docs/usuario_y_tutoriales/TUTORIAL_DESPLIEGUE_WEB.md) · [Manual de Usuario](docs/usuario_y_tutoriales/MANUAL_USUARIO.md) |
| **Repositorio** | [github.com/Oscar-Rodriguez-2022/Traductor-Senas-IA](https://github.com/Oscar-Rodriguez-2022/Traductor-Senas-IA) |

---

## Integrantes del Proyecto

| Integrante | Rol | Contribución |
|---|---|---|
| **Rodriguez Chacara, Oscar Daniel** | Desarrollo Full-Stack, ML, QA, Despliegue | 100% |
| **Armas Alvarado, José Deyvis** | Desarrollo y ML | 100% |
| **Arias Chauca, Nicolás Enrry** | Desarrollo y QA | 100% |
| **Reátegui Arévalo, Oscar Manuel** | Desarrollo y Despliegue | 100% |
| **Timana Barreda, Santiago Mathias** | Desarrollo y Testing | 100% |

---

## Descripción del Proyecto

**LSP Vision AI** es un sistema de visión artificial que traduce en tiempo real los gestos del alfabeto manual de la **Lengua de Señas Peruana (LSP)** a texto, reduciendo la brecha de comunicación entre personas con discapacidad auditiva y oyentes. Opera directamente desde la cámara web del dispositivo, sin requerir hardware especializado.

El sistema fue desarrollado aplicando metodología **Scrum** (4 sprints, 22 historias de usuario, 137 story points) con prácticas de ingeniería **XP** (TDD, refactorización, propiedad compartida de código) y controles **DevSecOps** (autenticación HMAC, auditoría anónima, escaneo de vulnerabilidades).

### Pipeline de procesamiento

```
Cámara web → MediaPipe Hands → 21 landmarks → 42 coords normalizadas → SVM → Letra + Confianza%
```

### Propuesta técnica diferencial

| Característica | Descripción técnica |
|---|---|
| **Reducción dimensional geométrica** | Extrae 21 puntos clave (landmarks) por frame → solo 42 coordenadas. Reducción del 99.7% frente a procesamiento de píxeles crudos. Entrenamiento SVM en < 3 s con accuracy ≥ 85%. |
| **Data augmentation a nivel de landmarks** | `scripts/augmentar_dataset.py` genera 15 variaciones geométricas por muestra (rotación ±5°/10°/15°, escala ×0.88–1.12, ruido σ=0.006), multiplicando el dataset ×16 sin imágenes adicionales. |
| **Escudo de calidad en captura** | `scripts/capturar_dataset.py` descarta automáticamente frames con confianza de detección MediaPipe < 0.7. |
| **Seguridad sin dependencias externas** | Tokens de sesión `timestamp.nonce.HMAC-SHA256` implementados con stdlib Python estándar. PBKDF2-HMAC-SHA256 (260 000 iteraciones) para hashing. |
| **Modularidad src-layout** | Código fuente en `src/` con 6 módulos de responsabilidad única, testables de forma independiente. `pythonpath = ["src"]` en `pyproject.toml`. |

---

## Arquitectura del Sistema

### Diagrama de módulos

```
┌─────────────────────────────────────────────────────────────────┐
│                        src/app.py                               │
│              (Orquestador Streamlit — HU-12)                    │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  lsp_auth.py │  │ lsp_audit.py │  │     lsp_ui.py        │  │
│  │  Auth HMAC   │  │  Log anónimo │  │   Componentes WCAG   │  │
│  │  (HU-13)     │  │  GDPR Art.25 │  │   2.1 AA (HU-15)     │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────┐  ┌──────────────────────────┐ │
│  │       lsp_video.py           │  │       lsp_core.py        │ │
│  │   Procesador WebRTC          │  │   Núcleo ML testeable    │ │
│  │   Clase Traductor (HU-08)    │  │   Landmarks + SVM        │ │
│  │   threading.Lock (INC-05)    │  │   (HU-06, HU-07, HU-10) │ │
│  └──────────────────────────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Flujo de datos en tiempo real

```
Frame WebRTC (320×240) → cv2.cvtColor BGR→RGB → MediaPipe Hands
→ 21 landmarks [x,y] normalizados → flatten 42 coords
→ SVM.predict_proba() → (letra, confianza%) → aria-live UI
```

---

## Estructura del Repositorio

```
Traductor-Senas-IA/
│
├── .streamlit/
│   └── config.toml               ← Configuración de tema, servidor y XSRF de Streamlit
│
├── src/                          ← Código fuente de la aplicación web
│   ├── __init__.py               │  Marcador de paquete Python
│   ├── app.py                    │  Orquestador principal Streamlit + WebRTC
│   ├── lsp_core.py               │  Núcleo ML: carga modelo, landmarks, predicción
│   ├── lsp_auth.py               │  Autenticación HMAC-SHA256 + rate limiting
│   ├── lsp_audit.py              │  Log de auditoría anónimo JSON Lines (GDPR)
│   ├── lsp_video.py              │  Procesador de video WebRTC (clase Traductor)
│   ├── lsp_ui.py                 │  Componentes HTML/CSS accesibles (WCAG 2.1 AA)
│   └── pages/
│       └── 1_Metricas_QA.py      │  Dashboard de métricas de calidad
│
├── tests/                        ← Suite TDD completa (143 pruebas totales)
│   ├── conftest.py               │  Fixtures compartidos (modelo, landmarks, sesión)
│   ├── test_auth.py              │  14 tests — autenticación HMAC (HU-13)
│   ├── test_audit.py             │  9 tests — auditoría GDPR (HU-14)
│   ├── test_seguridad.py         │  34 tests — DevSecOps (4 clases: sanitización, rate limiting, audit, PKL)
│   ├── test_etica.py             │  29 tests — IA ética, XAI y equidad (HU-16, HU-20)
│   ├── test_video.py             │  12 tests — procesamiento de video (HU-08/09)
│   ├── test_sistema.py           │  18 tests de sistema UT-01..UT-18 (pruebas de integración)
│   ├── test_integracion.py       │  3 tests — flujo E2E
│   ├── test_landmarks.py         │  Tests de extracción de landmarks (HU-06)
│   ├── test_modelo.py            │  Tests de carga y predicción (HU-10)
│   ├── test_validacion.py        │  Tests de validación de datos
│   └── test_errores.py           │  Tests de manejo de excepciones
│
├── qa/                           ← Scripts de medición de calidad
│   ├── __init__.py               │  Marcador de paquete Python
│   ├── _utils.py                 │  Utilidades internas compartidas de QA
│   ├── benchmark.py              │  Latencia por etapa del pipeline
│   ├── fps_test.py               │  FPS sostenidos (objetivo ≥ 24)
│   ├── stress_test.py            │  Estrés 100–5000 predicciones
│   ├── evaluate.py               │  Accuracy/Precision/Recall/F1 por clase
│   ├── confusion_matrix.py       │  Heatmap de confusiones entre letras
│   ├── cross_validation.py       │  Validación cruzada K-Fold
│   ├── robustez.py               │  Resistencia a condiciones adversas (luz, ruido)
│   ├── recursos.py               │  RAM/CPU durante 300 s
│   └── generar_reportes.py       │  Consolida todos los CSV en PDF + HTML
│
├── scripts/                      ← Scripts de captura, entrenamiento y utilidades
│   ├── capturar_dataset.py       │  Captura interactiva guiada del dataset LSP
│   ├── entrenar_modelo.py        │  Entrena SVM desde data/ → modelo.pkl
│   ├── augmentar_dataset.py      │  Data augmentation ×16 + entrenamiento
│   ├── entrenar_desde_csv.py     │  Entrena combinando CSVs colaborativos
│   ├── extraer_landmarks.py      │  Extrae landmarks a CSV para compartir
│   ├── traducir_en_vivo.py       │  Demo offline sin Streamlit
│   ├── 1_CAPTURAR_dataset.bat    │  Acceso rápido Windows → captura de dataset
│   ├── 2_TRADUCIR_en_vivo.bat    │  Acceso rápido Windows → demo offline
│   ├── 3_WEB_probar_local.bat    │  Acceso rápido Windows → servidor local
│   ├── 4_ENTRENAR_desde_CSV.bat  │  Acceso rápido Windows → entrenamiento CSV
│   ├── 5_AUGMENTAR_y_ENTRENAR.bat│  Acceso rápido Windows → augmentación + entreno
│   ├── COMPANEROS_extraer_landmarks.bat │  Extracción para integrantes del equipo
│   └── QA.bat                    │  Menú interactivo de QA para Windows
│
├── data/                         ← Dataset LSP (subcarpetas a/ … z/ con .png)
├── landmarks_csv/                ← CSVs colaborativos de landmarks por integrante
├── reportes/                     ← Reportes QA generados (CSV, PNG, PDF)
├── docs/                         ← Documentación técnica organizada por dominio
│   ├── arquitectura/             │  Modelos de diseño del sistema
│   │   ├── COMPONENTES.md        │  Diagramas Mermaid de componentes
│   │   └── MODELO_DATOS.md       │  Modelo de datos incremental
│   ├── gestion_agil/             │  Seguimiento y trazabilidad Scrum
│   │   ├── HISTORIAS_USUARIO.md  │  22 HUs (HU-01..HU-22) con Gherkin y MoSCoW
│   │   ├── SPRINT_BACKLOG.md     │  Desglose de tareas (4 sprints, 137 SP)
│   │   ├── BURNDOWN_CHART.md     │  Burndown Charts release + 4 sprints
│   │   ├── DEFINITION_OF_DONE.md │  Criterios DoD v2.1: TDD, DevSecOps, WCAG, 22 HUs
│   │   ├── MATRIZ_TRAZABILIDAD.md│  Mapeo HU ↔ módulo ↔ test
│   │   └── requerimientos.md     │  15 RF + 15 RNF
│   ├── qa_y_pruebas/             │  Estándares de calidad y reportes técnicos
│   │   ├── GUIA_QA.md            │  Estándares TDD y suite de 13 fases de medición
│   │   ├── INCIDENTES.md         │  12 incidentes registrados con causa raíz y hotfix
│   │   ├── GUIA_RECAPTURA_DATASET.md │  Recaptura de letras con dataset insuficiente
│   │   ├── plantilla_UAT.md      │  Plantilla de User Acceptance Testing
│   │   └── reporte_pruebas.txt   │  Resultados de la suite de tests automatizados
│   ├── seguridad_y_etica/        │  Plan de Seguridad Integral e IA Ética
│   │   ├── SEGURIDAD.md          │  Plan de Seguridad Integral v2.1
│   │   └── IA_ETICA.md           │  Principios XAI, análisis de sesgos, responsabilidad social
│   ├── usuario_y_tutoriales/     │  Manuales y guías de despliegue
│   │   ├── MANUAL_USUARIO.md     │  Manual de usuario v2.1
│   │   ├── TUTORIAL_HUGGINGFACE.md   │  Despliegue en Hugging Face Spaces con Docker
│   │   ├── TUTORIAL_DESPLIEGUE_WEB.md│  Despliegue en Streamlit Community Cloud
│   │   └── TUTORIAL_EQUIPO.md    │  Normas de propiedad compartida y flujo Git
│   └── cierre/                   │  Retrospectivas y lecciones aprendidas
│       └── LECCIONES_APRENDIDAS.md│  Retrospectiva técnica v3.1 (3 sprints + Reingeniería)
│
├── config/                       ← Configuraciones de herramientas de desarrollo
│   ├── trivy.yaml                │  Escaneo de vulnerabilidades DevSecOps (CRITICAL+HIGH+MEDIUM)
│   ├── setup.cfg                 │  Configuración Flake8 (invocado con --config config/setup.cfg)
│   └── requirements-dev.txt      │  Dependencias de desarrollo y testing
│
├── modelo.pkl                    ← Modelo SVM entrenado (generado localmente)
├── Dockerfile                    ← Imagen Docker con usuario no-root (UID 1001)
├── Makefile                      ← Automatización de tareas QA
├── packages.txt                  ← Dependencias de sistema para Streamlit Cloud (debe estar en raíz)
├── requirements.txt              ← Dependencias de producción (requerido en raíz por Streamlit Cloud)
├── pyproject.toml                ← Configuración Black, Pylint, pytest, coverage (PEP 518)
└── .dockerignore                 ← Archivos excluidos de la imagen Docker
```

---

## Instalación y Ejecución Local

### Requisitos previos

- **Python 3.12** (obligatorio — MediaPipe 0.10.21 no es compatible con Python 3.13)
- Cámara web funcional
- Windows 10+ / Ubuntu 20.04+ / macOS 12+

### Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/Oscar-Rodriguez-2022/Traductor-Senas-IA.git
cd Traductor-Senas-IA

# 2. Crear y activar entorno virtual
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

# 3. Instalar dependencias
pip install -r requirements.txt
```

### Entrenamiento del modelo (una sola vez)

```bash
# Opción recomendada: augmentación ×16 + entrenamiento automático
py -3.12 scripts/augmentar_dataset.py

# Opción rápida: entrenar directo desde imágenes
py -3.12 scripts/entrenar_modelo.py
```

### Ejecutar la aplicación web

```bash
streamlit run src/app.py
# Abrir: http://localhost:8501
# Clave de acceso demo: UPN2026
```

### Ejecución con Docker

```bash
docker build -t lsp-vision-ai .
docker run -p 8501:7860 lsp-vision-ai
# Abrir: http://localhost:8501
```

---

## Suite de Calidad (QA)

### Ejecución rápida

```bash
# Todas las pruebas (unitarias, integración, sistema, seguridad, ética)
pytest tests/ -v

# Solo pruebas de sistema (UT-01..UT-18)
pytest tests/test_sistema.py -v

# Con cobertura de código
pytest tests/ --cov=lsp_core --cov=lsp_auth --cov=lsp_audit --cov-report=html

# Suite QA completa (benchmark, FPS, estrés, métricas, PDF)
make all      # Linux/macOS
QA.bat        # Windows — doble clic → opción 13
```

### Resultados actuales

| Métrica | Valor | Umbral |
|---|---|---|
| Tests `tests/` | **143 tests** (114 base + 29 XAI/ética — 11 archivos de test) | 0 FAIL |
| Cobertura `lsp_core` | **96%** | ≥ 96% |
| Cobertura `lsp_auth` | **≥ 90%** | ≥ 90% |
| Cobertura `lsp_audit` | **≥ 90%** | ≥ 90% |
| Pylint | **7.14/10** | ≥ 7.5/10 |
| Flake8 | **0 errores** | 0 |
| Latencia pipeline completo | **~18 ms** | < 200 ms |
| FPS sostenidos | **24.7 FPS** | ≥ 24 FPS (60 s) |
| Estrés 5 000 predicciones | **0 errores** | 0 excepciones |
| Accuracy del modelo SVM | **88.3%** | ≥ 85% |
| Tests DevSecOps (`test_seguridad.py`) | **33/34 PASS + 1 SKIP** | 0 FAIL |

---

## Artefactos Académicos del Capstone (Scrum / ISO)

### Planificación y gestión Scrum

| Artefacto | Descripción |
|---|---|
| [`HISTORIAS_USUARIO.md`](docs/gestion_agil/HISTORIAS_USUARIO.md) | 22 Historias de Usuario (HU-01..HU-22) con criterios Gherkin, prioridad MoSCoW y estado final |
| [`SPRINT_BACKLOG.md`](docs/gestion_agil/SPRINT_BACKLOG.md) | Desglose de cada HU en tareas técnicas (4 sprints, 137 SP) — todas completadas |
| [`BURNDOWN_CHART.md`](docs/gestion_agil/BURNDOWN_CHART.md) | Burndown Charts release + por sprint; línea real llega a 0 en Sprint de Reingeniería |
| [`DEFINITION_OF_DONE.md`](docs/gestion_agil/DEFINITION_OF_DONE.md) | Criterios obligatorios DoD v2.1: TDD, DevSecOps, WCAG 2.1 AA, 100% HU completadas |
| [`MATRIZ_TRAZABILIDAD.md`](docs/gestion_agil/MATRIZ_TRAZABILIDAD.md) | Mapeo completo HU ↔ módulo código ↔ archivo de test ↔ estado |

### Calidad, seguridad y ética

| Artefacto | Descripción |
|---|---|
| [`SEGURIDAD.md`](docs/seguridad_y_etica/SEGURIDAD.md) | Plan de Seguridad Integral v2.1: autenticación JWT-like HMAC, rate limiting, GDPR, Dockerfile no-root |
| [`IA_ETICA.md`](docs/seguridad_y_etica/IA_ETICA.md) | Transparencia y Explicabilidad (XAI): pipeline interpretable, análisis de sesgos, equidad por clase |
| [`GUIA_QA.md`](docs/qa_y_pruebas/GUIA_QA.md) | Estándares TDD, revisión de pares y suite automatizada de 13 fases de medición |
| [`reporte_pruebas.txt`](docs/qa_y_pruebas/reporte_pruebas.txt) | Resultados de pruebas unitarias, integración, sistema y seguridad |
| [`INCIDENTES.md`](docs/qa_y_pruebas/INCIDENTES.md) | 12 incidentes (11 resueltos, 1 pendiente — INC-12) con causa raíz, hotfix y verificación |

### Documentación de usuario y despliegue

| Artefacto | Descripción |
|---|---|
| [`MANUAL_USUARIO.md`](docs/usuario_y_tutoriales/MANUAL_USUARIO.md) | Manual de usuario v2.1: login, traductor en tiempo real, confianza, historial, QA dashboard (HU-21 CA-21.4) |
| [`TUTORIAL_HUGGINGFACE.md`](docs/usuario_y_tutoriales/TUTORIAL_HUGGINGFACE.md) | Despliegue en Hugging Face Spaces con Docker (recomendado para Capstone) |
| [`TUTORIAL_DESPLIEGUE_WEB.md`](docs/usuario_y_tutoriales/TUTORIAL_DESPLIEGUE_WEB.md) | Despliegue alternativo en Streamlit Community Cloud |
| [`TUTORIAL_EQUIPO.md`](docs/usuario_y_tutoriales/TUTORIAL_EQUIPO.md) | Normas de propiedad compartida, flujo Git y entorno para nuevos integrantes |
| [`GUIA_RECAPTURA_DATASET.md`](docs/qa_y_pruebas/GUIA_RECAPTURA_DATASET.md) | Recaptura de letras con dataset insuficiente, respetando privacidad de datos |
| [`LECCIONES_APRENDIDAS.md`](docs/cierre/LECCIONES_APRENDIDAS.md) | Retrospectiva técnica v3.1: 20 decisiones técnicas, 11 obstáculos — 3 sprints regulares + Sprint Reingeniería |

---

## Cumplimiento de Estándares Académicos

| Punto del Capstone | Artefacto / módulo | Estado |
|---|---|---|
| Historias de Usuario + Sprint Backlog (Scrum) | [`HISTORIAS_USUARIO.md`](docs/gestion_agil/HISTORIAS_USUARIO.md), [`SPRINT_BACKLOG.md`](docs/gestion_agil/SPRINT_BACKLOG.md) | ✅ |
| Burndown Chart por Sprint | [`BURNDOWN_CHART.md`](docs/gestion_agil/BURNDOWN_CHART.md) (4 sprints, 137 SP) | ✅ |
| Definition of Done documentado | [`DEFINITION_OF_DONE.md`](docs/gestion_agil/DEFINITION_OF_DONE.md) v2.1 | ✅ |
| Matriz de Trazabilidad | [`MATRIZ_TRAZABILIDAD.md`](docs/gestion_agil/MATRIZ_TRAZABILIDAD.md) | ✅ |
| Refactorización y modularidad (XP) | `src/lsp_*.py` — 6 módulos de responsabilidad única | ✅ |
| TDD — pruebas unitarias / integración / sistema | `tests/` (143 total en 11 archivos) | ✅ |
| Pruebas de carga, estrés y rendimiento | `qa/benchmark.py`, `qa/fps_test.py`, `qa/stress_test.py` | ✅ |
| DevSecOps — autenticación y sesiones seguras | `src/lsp_auth.py` — HMAC-SHA256, expira 60 min | ✅ |
| DevSecOps — auditoría y privacidad (GDPR Art. 25) | `src/lsp_audit.py` — IDs anónimos SHA-256[:8] | ✅ |
| DevSecOps — escaneo de vulnerabilidades | `config/trivy.yaml` — CRITICAL+HIGH+MEDIUM | ✅ |
| Accesibilidad WCAG 2.1 AA | `src/lsp_ui.py` — aria-live, contraste 4.5:1, skip-nav | ✅ |
| Explicabilidad del sistema de IA (XAI) | `render_pipeline_explicado()` + [`IA_ETICA.md`](docs/seguridad_y_etica/IA_ETICA.md) | ✅ |
| Análisis de sesgos e IA ética | `tests/test_etica.py` (29 tests) + [`IA_ETICA.md`](docs/seguridad_y_etica/IA_ETICA.md) | ✅ |
| Data augmentation (calidad del dataset) | `scripts/augmentar_dataset.py` — ×16 muestras | ✅ |
| Manual de Usuario Preliminar | [`MANUAL_USUARIO.md`](docs/usuario_y_tutoriales/MANUAL_USUARIO.md) | ✅ |
| Registro de Lecciones Aprendidas | [`LECCIONES_APRENDIDAS.md`](docs/cierre/LECCIONES_APRENDIDAS.md) | ✅ |
| Despliegue profesional con Docker | `Dockerfile` (no-root) + [`TUTORIAL_HUGGINGFACE.md`](docs/usuario_y_tutoriales/TUTORIAL_HUGGINGFACE.md) | ✅ |

---

## Stack Tecnológico

| Capa | Tecnología | Versión | Propósito |
|---|---|---|---|
| Lenguaje | Python | 3.12 | Desarrollo principal |
| Framework web | Streamlit | latest | UI reactiva + WebRTC |
| Video en tiempo real | streamlit-webrtc | latest | Captura de cámara web |
| Visión por computador | MediaPipe Hands | 0.10.21 | Detección de 21 landmarks |
| Procesamiento de imagen | OpenCV (headless) | 4.11.0.86 | Conversión y resize de frames |
| ML — clasificación | scikit-learn SVM | 1.9.0 | Clasificador RBF kernel |
| Serialización modelo | joblib | latest | Carga/guarda modelo.pkl |
| Pruebas | pytest + pytest-cov | latest | TDD y cobertura |
| Calidad de código | Flake8 + Black + Pylint | latest | Estilo y calidad |
| Contenedores | Docker | latest | Despliegue reproducible |
| Seguridad | stdlib (hashlib, hmac, secrets) | Python 3.12 | Sin dependencias externas |

---

*Versión 2.1 — Junio 2026 · LSP Vision AI · UPN Ingeniería de Sistemas*
*Cambios v2.0: arquitectura src-layout, módulos lsp_* refactorizados, DevSecOps completo, WCAG 2.1 AA, Docker no-root, Sprint de Reingeniería — 137 SP totales*
*Cambios v2.1: nuevo integrante Timana Barreda, conteos de tests actualizados (143 total, 34 DevSecOps, 29 ética+XAI), DoD v2.1, Lecciones Aprendidas v3.1*
