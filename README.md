# Sistema Interactivo de Visión Artificial para la Comunicación Inclusiva de Personas con Discapacidad Auditiva (LSP)

### Universidad Privada del Norte (UPN)
* **Facultad de Ingeniería**
* **Carrera de Ingeniería de Sistemas Computacionales**
* **Curso:** Capstone Project Sistemas (2026-1)
* **Docente:** Edward Jose Flores Masias

---

## Integrantes del Proyecto

| Integrante | Rol | Contribución |
|---|---|---|
| **Rodriguez Chacara, Oscar Daniel** | Desarrollo Full-Stack, ML, QA, Despliegue | 100% |
| **Armas Alvarado, José Deyvis** | Desarrollo y ML | 100% |
| **Arias Chauca, Nicolás Enrry** | Desarrollo y QA | 100% |
| **Reátegui Arévalo, Oscar Manuel** | Desarrollo y Despliegue | 100% |

---

## Descripción del Proyecto

**LSP Vision AI** es un sistema de visión artificial que traduce en tiempo real los gestos del alfabeto manual de la **Lengua de Señas Peruana (LSP)** a texto, reduciendo la brecha de comunicación entre personas con discapacidad auditiva y oyentes. Opera directamente desde la cámara web del dispositivo, sin requerir hardware especializado.

El sistema fue desarrollado aplicando metodología **Scrum** (3 sprints, 22 historias de usuario, 117 story points) con prácticas de ingeniería **XP** (TDD, refactorización, propiedad compartida de código) y controles **DevSecOps** (autenticación HMAC, auditoría anónima, escaneo de vulnerabilidades).

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
├── src/                          ← Código fuente de la aplicación web
│   ├── app.py                    │  Orquestador principal Streamlit + WebRTC
│   ├── lsp_core.py               │  Núcleo ML: carga modelo, landmarks, predicción
│   ├── lsp_auth.py               │  Autenticación HMAC-SHA256 + rate limiting
│   ├── lsp_audit.py              │  Log de auditoría anónimo JSON Lines (GDPR)
│   ├── lsp_video.py              │  Procesador de video WebRTC (clase Traductor)
│   ├── lsp_ui.py                 │  Componentes HTML/CSS accesibles (WCAG 2.1 AA)
│   └── pages/
│       └── 1_Metricas_QA.py      │  Dashboard de métricas de calidad
│
├── tests/                        ← Suite TDD (49+ pruebas automatizadas)
│   ├── conftest.py               │  Fixtures compartidos
│   ├── test_auth.py              │  14 tests — autenticación (HU-13)
│   ├── test_audit.py             │  9 tests — auditoría (HU-14)
│   ├── test_seguridad.py         │  20 tests — DevSecOps (3 capas)
│   ├── test_etica.py             │  15 tests — IA ética y equidad (HU-20)
│   ├── test_video.py             │  11 tests — procesamiento de video (HU-08)
│   ├── test_integracion.py       │  3 tests — flujo E2E
│   ├── test_landmarks.py         │  Tests de extracción de landmarks (HU-06)
│   ├── test_modelo.py            │  Tests de carga y predicción (HU-10)
│   ├── test_validacion.py        │  Tests de validación de datos
│   └── test_errores.py           │  Tests de manejo de excepciones
│
├── test_sistema.py               ← 18 tests de sistema UT-01..UT-18
│
├── qa/                           ← Scripts de medición de calidad
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
├── scripts/                      ← Scripts de captura y entrenamiento
│   ├── capturar_dataset.py       │  Captura interactiva guiada del dataset LSP
│   ├── entrenar_modelo.py        │  Entrena SVM desde data/ → modelo.pkl
│   ├── augmentar_dataset.py      │  Data augmentation ×16 + entrenamiento
│   ├── entrenar_desde_csv.py     │  Entrena combinando CSVs colaborativos
│   ├── extraer_landmarks.py      │  Extrae landmarks a CSV para compartir
│   └── traducir_en_vivo.py       │  Demo offline sin Streamlit
│
├── data/                         ← Dataset LSP (subcarpetas a/ … z/ con .png)
├── reportes/                     ← Reportes QA generados (CSV, PNG, PDF)
├── docs/                         ← Documentación técnica y diagramas
│   ├── requerimientos.md         │  15 RF + 15 RNF
│   ├── arquitectura/
│   │   ├── COMPONENTES.md        │  Diagramas Mermaid de componentes
│   │   └── MODELO_DATOS.md       │  Modelo de datos incremental
│   └── plantilla_UAT.md          │  Plantilla de User Acceptance Testing
│
├── modelo.pkl                    ← Modelo SVM entrenado (generado localmente)
├── Dockerfile                    ← Imagen Docker con usuario no-root (UID 1001)
├── Makefile                      ← Automatización de tareas QA
├── QA.bat                        ← Menú interactivo de QA para Windows
├── requirements.txt              ← Dependencias de producción
├── requirements-dev.txt          ← Dependencias de desarrollo + testing
├── pyproject.toml                ← Configuración Black, Pylint, pytest
├── setup.cfg                     ← Configuración Flake8 + cobertura
└── trivy.yaml                    ← Escaneo de vulnerabilidades (CRITICAL+HIGH)
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
# Todas las pruebas unitarias, de integración y sistema
pytest tests/ test_sistema.py -v

# Con cobertura de código
pytest tests/ --cov=lsp_core --cov=lsp_auth --cov=lsp_audit --cov-report=html

# Suite QA completa (benchmark, FPS, estrés, métricas, PDF)
make all      # Linux/macOS
QA.bat        # Windows — doble clic → opción 13
```

### Resultados actuales

| Métrica | Valor | Umbral |
|---|---|---|
| Tests unitarios + sistema | **49+ PASS** | 0 FAIL |
| Cobertura `lsp_core` | **96%** | ≥ 96% |
| Cobertura `lsp_auth` | **≥ 90%** | ≥ 90% |
| Cobertura `lsp_audit` | **≥ 90%** | ≥ 90% |
| Pylint | **7.14/10** | ≥ 7.5/10 |
| Flake8 | **0 errores** | 0 |
| Latencia pipeline completo | **~18 ms** | < 200 ms |
| FPS sostenidos | **≥ 24 FPS** | ≥ 24 FPS (60 s) |
| Estrés 5 000 predicciones | **0 errores** | 0 excepciones |
| Accuracy del modelo SVM | **≥ 85%** | ≥ 85% |
| Tests DevSecOps | **20/20 PASS** | 100% |

---

## Artefactos Académicos del Capstone (Scrum / ISO)

### Planificación y gestión Scrum

| Artefacto | Descripción |
|---|---|
| [`HISTORIAS_USUARIO.md`](HISTORIAS_USUARIO.md) | 22 Historias de Usuario (HU-01..HU-22) con criterios Gherkin, prioridad MoSCoW y estado final |
| [`SPRINT_BACKLOG.md`](SPRINT_BACKLOG.md) | Desglose de cada HU en tareas técnicas (3 sprints, 117 SP) — todas completadas |
| [`BURNDOWN_CHART.md`](BURNDOWN_CHART.md) | Burndown Charts release + por sprint; línea real llega a 0 en Sprint 3 |
| [`DEFINITION_OF_DONE.md`](DEFINITION_OF_DONE.md) | Criterios obligatorios DoD v2.0: TDD, DevSecOps, WCAG 2.1 AA, 100% HU completadas |
| [`MATRIZ_TRAZABILIDAD.md`](MATRIZ_TRAZABILIDAD.md) | Mapeo completo HU ↔ módulo código ↔ archivo de test ↔ estado |

### Calidad, seguridad y ética

| Artefacto | Descripción |
|---|---|
| [`SEGURIDAD.md`](SEGURIDAD.md) | Plan de Seguridad Integral v2.0: autenticación JWT-like HMAC, rate limiting, GDPR, Dockerfile no-root |
| [`IA_ETICA.md`](IA_ETICA.md) | Transparencia y Explicabilidad (XAI): pipeline interpretable, análisis de sesgos, equidad por clase |
| [`GUIA_QA.md`](GUIA_QA.md) | Estándares TDD, revisión de pares y suite automatizada de 13 fases de medición |
| [`reporte_pruebas.txt`](reporte_pruebas.txt) | Resultados de pruebas unitarias, integración, sistema y seguridad |
| [`INCIDENTES.md`](INCIDENTES.md) | 8 bugs registrados durante la reingeniería con causa raíz, hotfix y verificación |

### Documentación de usuario y despliegue

| Artefacto | Descripción |
|---|---|
| [`MANUAL_USUARIO.md`](MANUAL_USUARIO.md) | Manual preliminar: login, traductor en tiempo real, confianza, QA dashboard (HU-21 CA-21.4) |
| [`TUTORIAL_HUGGINGFACE.md`](TUTORIAL_HUGGINGFACE.md) | Despliegue en Hugging Face Spaces con Docker (recomendado para Capstone) |
| [`TUTORIAL_DESPLIEGUE_WEB.md`](TUTORIAL_DESPLIEGUE_WEB.md) | Despliegue alternativo en Streamlit Community Cloud |
| [`TUTORIAL_EQUIPO.md`](TUTORIAL_EQUIPO.md) | Normas de propiedad compartida, flujo Git y entorno para nuevos integrantes |
| [`GUIA_RECAPTURA_DATASET.md`](GUIA_RECAPTURA_DATASET.md) | Recaptura de letras con dataset insuficiente, respetando privacidad de datos |
| [`LECCIONES_APRENDIDAS.md`](LECCIONES_APRENDIDAS.md) | Retrospectiva técnica de los 3 sprints: retos de visión artificial y mejoras de ingeniería |

---

## Cumplimiento de Estándares Académicos

| Punto del Capstone | Artefacto / módulo | Estado |
|---|---|---|
| Historias de Usuario + Sprint Backlog (Scrum) | `HISTORIAS_USUARIO.md`, `SPRINT_BACKLOG.md` | ✅ |
| Burndown Chart por Sprint | `BURNDOWN_CHART.md` (3 sprints, 117 SP) | ✅ |
| Definition of Done documentado | `DEFINITION_OF_DONE.md` v2.0 | ✅ |
| Matriz de Trazabilidad | `MATRIZ_TRAZABILIDAD.md` | ✅ |
| Refactorización y modularidad (XP) | `src/lsp_*.py` — 6 módulos de responsabilidad única | ✅ |
| TDD — pruebas unitarias / integración / sistema | `tests/` (31+) + `test_sistema.py` (18) = 49+ tests | ✅ |
| Pruebas de carga, estrés y rendimiento | `qa/benchmark.py`, `qa/fps_test.py`, `qa/stress_test.py` | ✅ |
| DevSecOps — autenticación y sesiones seguras | `src/lsp_auth.py` — HMAC-SHA256, expira 60 min | ✅ |
| DevSecOps — auditoría y privacidad (GDPR Art. 25) | `src/lsp_audit.py` — IDs anónimos SHA-256[:8] | ✅ |
| DevSecOps — escaneo de vulnerabilidades | `trivy.yaml` — CRITICAL+HIGH+MEDIUM | ✅ |
| Accesibilidad WCAG 2.1 AA | `src/lsp_ui.py` — aria-live, contraste 4.5:1, skip-nav | ✅ |
| Explicabilidad del sistema de IA (XAI) | `render_pipeline_explicado()` + `IA_ETICA.md` | ✅ |
| Análisis de sesgos e IA ética | `tests/test_etica.py` (15 tests) + `IA_ETICA.md` | ✅ |
| Data augmentation (calidad del dataset) | `scripts/augmentar_dataset.py` — ×16 muestras | ✅ |
| Manual de Usuario Preliminar | `MANUAL_USUARIO.md` | ✅ |
| Registro de Lecciones Aprendidas | `LECCIONES_APRENDIDAS.md` | ✅ |
| Despliegue profesional con Docker | `Dockerfile` (no-root) + `TUTORIAL_HUGGINGFACE.md` | ✅ |

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

*Versión 2.0 — Junio 2026 · LSP Vision AI · UPN Ingeniería de Sistemas*
*Cambios v2.0: arquitectura src-layout, módulos lsp_* refactorizados, 49+ tests TDD, DevSecOps completo, WCAG 2.1 AA, Docker no-root, tabla de cumplimiento académico*
