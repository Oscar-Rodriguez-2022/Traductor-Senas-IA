# Sistema Interactivo de Visión Artificial para la Comunicación Inclusiva de Personas con Discapacidad Auditiva (LSP)

### 🏫 Universidad Privada del Norte (UPN)
* **Facultad de Ingeniería**
* **Carrera de Ingeniería de Sistemas Computacionales**
* **Curso:** Capstone Project Sistemas (2026-1)
* **Docente:** Edward Jose Flores Masias

---

## 👥 Integrantes del Proyecto (Autores)
* **Armas Alvarado, Jose Deyvis** (Contribución: 100%)
* **Arias Chauca, Nicolas Enrry** (Contribución: 100%)
* **Reategui Arevalo, Oscar Manuel** (Contribución: 100%)

---

## 🎯 Descripción del Proyecto (Contexto LSP)
Este repositorio contiene el desarrollo del software adaptado específicamente para el contexto de la **Lengua de Señas Peruana (LSP)**. El sistema mitiga la brecha de comunicación mediante el uso de visión artificial, utilizando la cámara web para traducir gestos estáticos en tiempo real.

### ⚡ Propuesta de Mejoría e Innovación Técnica
A diferencia de los modelos tradicionales que procesan matrices completas de píxeles en bruto (lo que generaba cuellos de botella de más de 30 minutos de entrenamiento), esta propuesta optimizada implementa:

1. **Reducción Dimensional Geométrica:** Extracción de 21 puntos clave (landmarks) tridimensionales mediante **MediaPipe Hands**, reduciendo los datos de entrada en un **99.7%** (pasando de millones de píxeles a solo 42 coordenadas por frame). El entrenamiento mediante **SVM (Support Vector Machine)** se reduce a menos de 3 segundos con alta precisión.
2. **Escudo de Calidad en Captura (`A.py`):** El módulo de captura restringe el guardado de datos si el nivel de confianza de detección de la morfología de la mano es menor al 70% ($min\_detection\_confidence=0.7$), asegurando un dataset limpio.
3. **Margen de Seguridad Dinámico:** Se incorporó un *padding* de 30 píxeles en el recuadro de recorte automático para evitar pérdidas morfológicas en los extremos de los dedos.

---

## 📂 Estructura del Repositorio
* **`A.py`**: Script interactivo para la captura guiada del dataset LSP, con márgenes de seguridad dinámicos y validación geométrica en tiempo real.
* **`B.py`**: Script de entrenamiento y traducción en tiempo real mediante vectores de soporte optimizados.
* **`data/`**: Carpeta que aloja la estructura y las muestras representativas del dataset de lenguaje de señas peruano desarrollado por el equipo.

---

## 🛠️ Requisitos e Instalación
Para ejecutar y probar el sistema localmente, asegúrese de contar con Python instalado y siga estos pasos:

1. Clonar este repositorio propio del equipo.
2. Instalar las dependencias esenciales ejecutando en la terminal:
   ```bash
   pip install opencv-python mediapipe numpy scikit-learn
   ```
3. Ejecutar la aplicación web:
   ```bash
   streamlit run app.py
   ```

---

## Artefactos Académicos del Capstone (Scrum / ISO)

Los siguientes archivos son **artefactos de planificación y calidad congelados**. Reflejan los requisitos establecidos en el prompt inicial del Capstone y no deben modificarse sin aprobación explícita del equipo:

| Artefacto | Descripción |
|---|---|
| [`HISTORIAS_USUARIO.md`](HISTORIAS_USUARIO.md) | 22 Historias de Usuario (HU-01..HU-22) con criterios Gherkin, prioridad MoSCoW, módulo y estado |
| [`DEFINITION_OF_DONE.md`](DEFINITION_OF_DONE.md) | Criterios de calidad que todo ítem debe cumplir: TDD, DevSecOps, WCAG 2.1 AA, privacidad |
| [`SEGURIDAD.md`](SEGURIDAD.md) | Análisis de superficie de ataque y controles DevSecOps implementados |

### Estándares que cumple el proyecto

| Punto del prompt | Artefacto / módulo |
|---|---|
| Refactorización y modularidad (XP/Scrum) | `lsp_core.py`, `lsp_video.py`, `lsp_ui.py` |
| TDD y pruebas unitarias/integración/sistema | `tests/` (30 tests automatizados) |
| Pruebas de carga y estrés | `qa/benchmark.py`, `qa/fps_test.py` (HU-22) |
| Autenticación y manejo de sesiones | `lsp_auth.py` — HMAC-SHA256, expira 60 min |
| Auditoría y privacidad (GDPR Art. 25) | `lsp_audit.py` — IDs anónimos SHA-256[:8] |
| Accesibilidad WCAG 2.1 AA | `lsp_ui.py` — aria-live, contraste, skip-nav |
| Explicabilidad del sistema de IA | `lsp_ui.render_pipeline_explicado()` |
| Definition of Done documentado | `DEFINITION_OF_DONE.md` |
