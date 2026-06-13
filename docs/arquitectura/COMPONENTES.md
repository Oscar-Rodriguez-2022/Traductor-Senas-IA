# Arquitectura del Sistema — LSP Vision AI
## Diagramas de Componentes y Casos de Uso
### Universidad Privada del Norte · Capstone Project Sistemas 2026

> Este documento cumple con **CA-02.1** (diagrama de componentes con 4 módulos principales),
> **CA-02.2** (≥7 casos de uso UC-01 a UC-07) y **CA-02.3** (tecnologías por módulo).

---

## 1. Diagrama de Componentes

```mermaid
graph TD
    subgraph PRESENTACION["🎨 Capa de Presentación"]
        APP["app.py\nOrquestador Streamlit"]
        UI["lsp_ui.py\nComponentes HTML/CSS/ARIA"]
        DASH["pages/1_Metricas_QA.py\nDashboard de Calidad"]
    end

    subgraph SEGURIDAD["🔐 Capa de Seguridad"]
        AUTH["lsp_auth.py\nTokens HMAC-SHA256\nPBKDF2 Password Hash"]
        AUDIT["lsp_audit.py\nLog Anónimo JSONL\nGDPR Art. 25"]
    end

    subgraph INFERENCIA["🧠 Capa de Inferencia ML/CV"]
        VIDEO["lsp_video.py\nProcesador WebRTC\nOverlay & FPS"]
        CORE["lsp_core.py\nNúcleo: Landmarks\nPredicción SVM"]
        MODEL[("modelo.pkl\nSVM Entrenado")]
    end

    subgraph DATOS["📊 Capa de Datos / Entrenamiento"]
        DATASET[("data/<letra>/*.png\nDataset de Imágenes")]
        CSV[("landmarks_csv/\nExportación Colaborativa")]
        REPORTES[("reportes/\nResultados QA")]
    end

    subgraph QA["🧪 Capa de Calidad"]
        TESTS["tests/\nSuite TDD: 49 tests"]
        QA_SCRIPTS["qa/\nBenchmark · FPS · Estrés\nEvaluación · Robustez"]
    end

    %% Flujo principal
    APP -->|"auth guard"| AUTH
    APP -->|"log event"| AUDIT
    APP -->|"render components"| UI
    APP -->|"WebRTC factory"| VIDEO
    VIDEO -->|"extraer_landmarks\npredecir"| CORE
    CORE -->|"joblib.load"| MODEL
    DASH -->|"auth guard"| AUTH
    DASH -->|"read log"| AUDIT
    DASH -->|"load CSVs"| REPORTES

    %% Entrenamiento
    DATASET -->|"cargar_dataset"| CORE
    CSV -->|"entrenar_desde_csv"| CORE
    CORE -->|"sklearn SVM fit"| MODEL

    %% QA
    QA_SCRIPTS -->|"import"| CORE
    TESTS -->|"import & mock"| CORE
    TESTS -->|"import & mock"| AUTH
    TESTS -->|"import & mock"| AUDIT
    QA_SCRIPTS -->|"write results"| REPORTES
```

---

## 2. Diagrama de Casos de Uso

```mermaid
graph LR
    USUARIO["👤 Usuario\n(persona sorda)"]
    ADMIN["🛡️ Administrador\n(docente/evaluador)"]
    SISTEMA["⚙️ Sistema\n(proceso interno)"]

    UC01["UC-01\nIniciar sesión"]
    UC02["UC-02\nTraducir seña en tiempo real"]
    UC03["UC-03\nVisualizar historial de señas"]
    UC04["UC-04\nConsultar métricas de calidad"]
    UC05["UC-05\nCapturar dataset"]
    UC06["UC-06\nEntrenar modelo SVM"]
    UC07["UC-07\nRegistrar evento de auditoría"]
    UC08["UC-08\nVisualizar pipeline explicado"]
    UC09["UC-09\nDesplegar en la nube"]

    USUARIO --> UC01
    USUARIO --> UC02
    USUARIO --> UC03
    USUARIO --> UC08
    ADMIN --> UC04
    ADMIN --> UC05
    ADMIN --> UC06
    ADMIN --> UC09
    SISTEMA --> UC07

    UC01 -.->|"include"| UC07
    UC02 -.->|"include"| UC07
    UC04 -.->|"extend (requiere auth)"| UC01
```

---

## 3. Tecnologías por Módulo (CA-02.3)

| Módulo | Responsabilidad | Tecnologías |
|--------|-----------------|-------------|
| **app.py** | Orquestador: configura la página, inicializa WebRTC, guarda el estado | Streamlit 1.x, streamlit-webrtc |
| **lsp_video.py** | Captura de video: procesa frames, dibuja overlay, mide FPS | OpenCV 4.11, MediaPipe 0.10, PyAV, threading |
| **lsp_core.py** | Núcleo ML/CV: carga modelo, extrae landmarks, predice, carga dataset | MediaPipe Hands, scikit-learn SVM, NumPy, joblib |
| **lsp_auth.py** | Autenticación: hashea contraseñas, genera/verifica tokens HMAC | hashlib (PBKDF2-SHA256), hmac, secrets (stdlib) |
| **lsp_audit.py** | Auditoría: escribe/lee/purga log JSON Lines anónimo | json, datetime (stdlib) |
| **lsp_ui.py** | Interfaz: HTML, CSS con correcciones WCAG, ARIA, skip-nav | Streamlit HTML unsafe, CSS3, ARIA 1.1 |
| **pages/1_Metricas_QA.py** | Dashboard: métricas del modelo, recursos en vivo, log de auditoría | Streamlit, psutil, csv, json (stdlib) |
| **qa/** | Suite de calidad: latencia, FPS, estrés, robustez, confusión | scikit-learn, NumPy, matplotlib, psutil |
| **tests/** | Suite TDD: unitarios, integración, sistema | pytest, pytest-cov, unittest.mock |
| **Dockerfile** | Contenedorización para despliegue reproducible | Docker, python:3.12-slim |

---

## 4. Flujo de Datos del Pipeline de Inferencia

```mermaid
sequenceDiagram
    participant CAM as Cámara Web
    participant WEBRTC as streamlit-webrtc
    participant TRADUCTOR as lsp_video.Traductor
    participant MP as MediaPipe Hands
    participant SVM as lsp_core.predecir()
    participant UI as lsp_ui.render_resultado()
    participant PANEL as Panel Resultado

    CAM->>WEBRTC: Frame BGR 640×480
    WEBRTC->>TRADUCTOR: recv(frame)
    TRADUCTOR->>TRADUCTOR: resize → 320×240 (alivio CPU)
    TRADUCTOR->>MP: process(rgb_small)
    MP-->>TRADUCTOR: 21 landmarks (x,y) normalizados
    TRADUCTOR->>TRADUCTOR: landmarks_validos(vector_42)
    TRADUCTOR->>SVM: predecir(modelo, landmarks)
    SVM-->>TRADUCTOR: (letra, confianza%)
    TRADUCTOR->>TRADUCTOR: draw_landmarks + badges overlay
    TRADUCTOR-->>WEBRTC: Frame anotado
    WEBRTC-->>CAM: Stream de vuelta al navegador
    Note over TRADUCTOR,PANEL: Cada 400ms (st.fragment run_every)
    TRADUCTOR-->>UI: letra, confianza, mano (via Lock)
    UI->>PANEL: render_resultado(letra, conf, mano)
```

---

## 5. Estructura de Carpetas

```
c:\Traductor-Senas-IA\
├── app.py                    # Punto de entrada Streamlit
├── lsp_core.py               # Núcleo ML/CV (testeable, sin UI)
├── lsp_video.py              # Procesador WebRTC
├── lsp_auth.py               # Autenticación HMAC
├── lsp_audit.py              # Log de auditoría
├── lsp_ui.py                 # Componentes HTML/CSS/ARIA
├── pages/
│   └── 1_Metricas_QA.py      # Dashboard de métricas
├── tests/                    # Suite TDD (49 tests)
├── qa/                       # Scripts de calidad (10 scripts)
├── data/                     # Dataset: data/<letra>/*.png
├── landmarks_csv/            # Exportaciones CSV colaborativas
├── reportes/                 # Resultados QA (CSV, PNG, JSON)
├── docs/
│   ├── requerimientos.md     # 15 RF + 15 RNF (CA-01.1)
│   └── arquitectura/
│       ├── COMPONENTES.md    # Este archivo (CA-02.1/02.2/02.3)
│       └── MODELO_DATOS.md   # Modelo de datos incremental
├── HISTORIAS_USUARIO.md      # 22 HUs con criterios Gherkin
├── DEFINITION_OF_DONE.md     # Criterios DoD por dimensión
├── MATRIZ_TRAZABILIDAD.md    # Función → HU → CA → Test
└── modelo.pkl                # Clasificador SVM entrenado
```

---

## Historial de Versiones

| Versión | Fecha | Cambio |
|---------|-------|--------|
| 1.0 | 2026-06-12 | Versión inicial — diagramas Mermaid, tecnologías, flujo de datos |
