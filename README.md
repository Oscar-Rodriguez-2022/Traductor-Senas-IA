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

---

## Descripción del Proyecto

Este repositorio contiene el desarrollo del software adaptado para la **Lengua de Señas Peruana (LSP)**. El sistema mitiga la brecha de comunicación mediante visión artificial: traduce gestos estáticos del alfabeto LSP en texto en tiempo real usando la cámara web, sin requerir hardware especial.

### Arquitectura del sistema

```
Cámara web → MediaPipe Hands (21 landmarks) → Vector 42 coords → SVM → Letra + Confianza
```

El sistema está desplegado como aplicación web Streamlit con autenticación HMAC, log de auditoría anónimo (GDPR Art. 25) y accesibilidad WCAG 2.1 AA.

### Propuesta técnica diferencial

1. **Reducción dimensional geométrica:** extracción de 21 puntos clave (landmarks) mediante MediaPipe Hands → solo 42 coordenadas por frame (reducción del 99.7% frente a procesar píxeles). Entrenamiento SVM en < 3 segundos con accuracy ≥ 85%.
2. **Dataset augmentation a nivel de landmarks:** el script `augmentar_dataset.py` genera 15 versiones geométricas por muestra original (rotación, escala, ruido), multiplicando el dataset ×16 sin imágenes adicionales.
3. **Escudo de calidad en captura:** `A.py` descarta automáticamente frames con confianza de detección < 0.7, garantizando un dataset limpio desde la captura.
4. **Seguridad sin dependencias externas:** tokens de sesión `timestamp.nonce.HMAC-SHA256` implementados con stdlib Python (sin JWT externo). PBKDF2-HMAC-SHA256 (260 000 iteraciones) para hashing de contraseñas.

---

## Estructura del Repositorio

### Scripts principales

| Archivo | Descripción |
|---|---|
| `app.py` | Orquestador principal de la app Streamlit (WebRTC + UI + Auth) |
| `A.py` | Captura guiada e interactiva del dataset LSP (evita sobrescribir datos de otros) |
| `B.py` | Entrenamiento rápido + demo de traducción en tiempo real (modo local offline) |
| `entrenar_modelo.py` | Entrenamiento del modelo SVM desde la carpeta `data/` (genera `modelo.pkl`) |
| `augmentar_dataset.py` | Data augmentation ×16 sobre landmarks + entrenamiento (recomendado) |
| `entrenar_desde_csv.py` | Entrenamiento combinando CSVs de múltiples colaboradores |
| `extraer_landmarks.py` | Extrae landmarks de las fotos propias y exporta a CSV para compartir |

### Módulos de la aplicación web

| Módulo | Descripción |
|---|---|
| `lsp_core.py` | Núcleo reutilizable: carga de modelo, extracción de landmarks, predicción |
| `lsp_video.py` | Procesador de video WebRTC (`Traductor`) — frame-by-frame con EMA de FPS |
| `lsp_auth.py` | Autenticación de sesión con tokens HMAC-SHA256 (HU-13) |
| `lsp_audit.py` | Log de auditoría anónimo en JSON Lines — GDPR Art. 25 (HU-14) |
| `lsp_ui.py` | Componentes HTML/CSS con correcciones WCAG 2.1 AA (HU-15) |
| `pages/1_Metricas_QA.py` | Dashboard de métricas de calidad y log de auditoría |

### Carpetas relevantes

| Carpeta | Contenido |
|---|---|
| `data/` | Dataset LSP — subcarpetas `a/` a `z/` con capturas `.png` |
| `tests/` | Suite TDD: 31 pruebas unitarias, de integración y seguridad |
| `qa/` | Scripts de calidad: benchmark, FPS, stress, cobertura, reportes |
| `reportes/` | CSVs y PNGs generados por la suite QA (se regeneran con QA.bat) |

---

## Instalación y ejecución local

### Requisitos previos
- Python 3.12 (requerido — MediaPipe 0.10.21 no es compatible con Python 3.13)
- Cámara web funcional

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/Gael2409/Traductor-Senas-IA.git
cd Traductor-Senas-IA

# 2. Crear entorno virtual (recomendado)
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Entrenar el modelo (necesario antes de correr la app)
py -3.12 augmentar_dataset.py   # o: py -3.12 entrenar_modelo.py

# 5. Ejecutar la aplicación web
streamlit run app.py
```

**Clave de acceso demo:** `UPN2026`

### Ejecución con Docker (para despliegue)

```bash
docker build -t lsp-vision-ai .
docker run -p 8501:7860 lsp-vision-ai
# Abrir: http://localhost:8501
```

---

## Artefactos Académicos del Capstone (Scrum / ISO)

### Planificación y gestión Scrum

| Artefacto | Descripción |
|---|---|
| [`HISTORIAS_USUARIO.md`](HISTORIAS_USUARIO.md) | 22 Historias de Usuario (HU-01..HU-22) con criterios Gherkin, prioridad MoSCoW, módulo y estado |
| [`SPRINT_BACKLOG.md`](SPRINT_BACKLOG.md) | Desglose de cada HU en tareas técnicas (Sprint 1, 2 y 3) con responsable y SP |
| [`BURNDOWN_CHART.md`](BURNDOWN_CHART.md) | Burndown Charts: release burndown + gráficos Mermaid por Sprint (117 SP totales) |
| [`DEFINITION_OF_DONE.md`](DEFINITION_OF_DONE.md) | Criterios que todo ítem debe cumplir antes de marcarse Done: TDD, DevSecOps, WCAG 2.1 AA |

### Calidad, seguridad y documentación técnica

| Artefacto | Descripción |
|---|---|
| [`SEGURIDAD.md`](SEGURIDAD.md) | Análisis de superficie de ataque y controles DevSecOps implementados |
| [`GUIA_QA.md`](GUIA_QA.md) | Guía completa de pruebas: unitarias, cobertura, rendimiento, estrés |
| [`TUTORIAL_HUGGINGFACE.md`](TUTORIAL_HUGGINGFACE.md) | Guía de despliegue en Hugging Face Spaces con Docker (recomendada para Capstone) |
| [`TUTORIAL_DESPLIEGUE_WEB.md`](TUTORIAL_DESPLIEGUE_WEB.md) | Guía alternativa para despliegue en Streamlit Community Cloud |
| [`TUTORIAL_EQUIPO.md`](TUTORIAL_EQUIPO.md) | Guía para capturar señas y contribuir al dataset colaborativo |
| [`GUIA_RECAPTURA_DATASET.md`](GUIA_RECAPTURA_DATASET.md) | Guía de recaptura para letras con dataset insuficiente o con 0 muestras válidas |

### Entrega final del Capstone

| Artefacto | Descripción |
|---|---|
| [`MANUAL_USUARIO.md`](MANUAL_USUARIO.md) | Manual de Usuario: login, traductor, confianza, historial y dashboard QA (HU-21 CA-21.4) |
| [`LECCIONES_APRENDIDAS.md`](LECCIONES_APRENDIDAS.md) | Decisiones técnicas, obstáculos y mejoras por Sprint (HU-21 CA-21.4) |

---

## Cumplimiento de estándares académicos

| Punto del Capstone | Artefacto / módulo |
|---|---|
| Historias de Usuario + Sprint Backlog (Scrum) | `HISTORIAS_USUARIO.md`, `SPRINT_BACKLOG.md` |
| Burndown Chart por Sprint | `BURNDOWN_CHART.md` (3 sprints, 117 SP) |
| Definition of Done documentado | `DEFINITION_OF_DONE.md` |
| Refactorización y modularidad (XP/Scrum) | `lsp_core.py`, `lsp_video.py`, `lsp_ui.py`, `lsp_auth.py`, `lsp_audit.py` |
| TDD y pruebas unitarias / integración / sistema | `tests/` (31 tests) + `test_sistema.py` (18 tests) |
| Pruebas de carga y estrés | `qa/benchmark.py`, `qa/fps_test.py`, `qa/stress_test.py` (HU-22) |
| Autenticación y manejo de sesiones seguras | `lsp_auth.py` — HMAC-SHA256, expira 60 min |
| Auditoría y privacidad (GDPR Art. 25) | `lsp_audit.py` — IDs anónimos SHA-256[:8] |
| Accesibilidad WCAG 2.1 AA | `lsp_ui.py` — aria-live, contraste 4.5:1, skip-nav, roles ARIA |
| Explicabilidad del sistema de IA | `lsp_ui.render_pipeline_explicado()` — expander con descripción del SVM |
| Data augmentation (dataset de calidad) | `augmentar_dataset.py` — ×16 muestras por landmark |
| Manual de Usuario Preliminar | `MANUAL_USUARIO.md` |
| Registro de Lecciones Aprendidas | `LECCIONES_APRENDIDAS.md` |
| Despliegue profesional (Docker) | `Dockerfile` + `TUTORIAL_HUGGINGFACE.md` |
