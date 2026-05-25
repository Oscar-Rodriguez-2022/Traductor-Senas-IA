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
