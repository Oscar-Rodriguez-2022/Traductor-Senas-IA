# Manual de Usuario Preliminar — LSP Vision AI
## Sistema Interactivo de Visión Artificial para la Comunicación Inclusiva (LSP)
### Universidad Privada del Norte · Capstone Project Sistemas 2026
**Autor:** Rodriguez Chacara, Oscar Daniel

---

## Índice

1. [Descripción general del sistema](#1-descripción-general-del-sistema)
2. [Requisitos del sistema](#2-requisitos-del-sistema)
3. [Acceso e inicio de sesión](#3-acceso-e-inicio-de-sesión)
4. [Pantalla principal — Traductor en tiempo real](#4-pantalla-principal--traductor-en-tiempo-real)
5. [Interpretación del indicador de confianza](#5-interpretación-del-indicador-de-confianza)
6. [Historial de señas y construcción de texto](#6-historial-de-señas-y-construcción-de-texto)
7. [Dashboard de Métricas QA](#7-dashboard-de-métricas-qa)
8. [Cierre de sesión](#8-cierre-de-sesión)
9. [Accesibilidad](#9-accesibilidad)
10. [Preguntas frecuentes](#10-preguntas-frecuentes)
11. [Soporte y contacto](#11-soporte-y-contacto)

---

## 1. Descripción general del sistema

**LSP Vision AI** es una aplicación web que traduce en tiempo real gestos estáticos del alfabeto de la **Lengua de Señas Peruana (LSP)** usando la cámara web del dispositivo.

El sistema está compuesto por cuatro etapas:

```
Cámara web  →  MediaPipe (detección de mano)  →  SVM (clasificación)  →  Resultado en pantalla
```

No almacena imágenes ni datos personales. Todo el procesamiento ocurre en memoria local.

---

## 2. Requisitos del sistema

### Para uso en la web (recomendado)
| Requisito | Mínimo |
|-----------|--------|
| Navegador | Google Chrome 112+ · Firefox 113+ · Edge 112+ |
| Cámara web | Resolución mínima 640 × 480 px |
| Conexión a internet | Solo para cargar la página; el modelo corre en el servidor |
| Permisos | El navegador debe tener permiso para acceder a la cámara |

### Para uso local
| Requisito | Versión |
|-----------|---------|
| Python | 3.10 o superior (recomendado 3.12) |
| Dependencias | Ver `requirements.txt` |
| Sistema operativo | Windows 10+, Ubuntu 20.04+, macOS 12+ |

---

## 3. Acceso e inicio de sesión

### 3.1 Abrir la aplicación

**Versión web:** abre la URL del despliegue en Streamlit Cloud (consulta al equipo o al docente la URL vigente).

**Versión local:**
```bash
streamlit run app.py
```
Luego abre el navegador en `http://localhost:8501`.

### 3.2 Pantalla de inicio de sesión

Al abrir la aplicación verás únicamente el formulario de acceso. El contenido del traductor no es visible hasta autenticarse correctamente.

```
┌─────────────────────────────────────┐
│        🤟 LSP Vision AI             │
│   Universidad Privada del Norte     │
│                                     │
│   Clave de acceso: [__________]     │
│                                     │
│          [  Ingresar  ]             │
└─────────────────────────────────────┘
```

### 3.3 Ingresar la clave

1. Escribe la clave de sesión académica en el campo indicado.
   - Clave de demostración: `UPN2026`
   - En producción, la clave está configurada en los secretos del servidor.
2. Presiona **Ingresar** o la tecla `Enter`.

### 3.4 Resultado de la autenticación

| Situación | Resultado |
|-----------|-----------|
| Clave correcta | Se redirige al traductor y se genera una sesión válida por 60 minutos. |
| Clave incorrecta | Aparece el mensaje *"Clave incorrecta. Intenta nuevamente."* Sin bloqueo. |
| Sesión expirada (> 60 min) | Se muestra nuevamente el formulario de acceso. |

> **Privacidad:** el sistema no registra tu identidad ni dirección IP. Solo guarda un identificador de sesión anónimo de 8 caracteres para la auditoría de accesos.

---

## 4. Pantalla principal — Traductor en tiempo real

### 4.1 Vista general

```
┌──────────────────────────────────────────────────────────┐
│  🤟 LSP Vision AI          [Métricas QA]   [Cerrar ×]   │
├─────────────────────────┬────────────────────────────────┤
│                         │  LETRA DETECTADA               │
│   [VIDEO EN VIVO]       │  ┌──────────────┐              │
│                         │  │      A       │ 94%          │
│   (cámara activa)       │  └──────────────┘              │
│                         │  ▓▓▓▓▓▓▓▓▓▓░░  94%            │
│                         │                                │
│                         │  Texto acumulado:              │
│                         │  HOLA                          │
│                         │         [Limpiar texto]        │
├─────────────────────────┴────────────────────────────────┤
│  ▼ ¿Cómo decide la IA? (expandir para ver explicación)  │
│  ──────────────────────────────────────────────────────  │
│  Cámara → MediaPipe → Landmarks → SVM → Predicción       │
└──────────────────────────────────────────────────────────┘
```

### 4.2 Activar la cámara

1. Al cargar la pantalla principal, el sistema pedirá permiso para usar la cámara.
2. Haz clic en **"Permitir"** en el aviso del navegador.
3. El video en vivo aparecerá en el panel izquierdo.
4. Si la cámara no está disponible, el sistema mostrará el mensaje *"Cámara no disponible"* sin interrumpir la aplicación.

### 4.3 Realizar una seña

1. Coloca tu mano frente a la cámara, a **30–60 cm** de distancia.
2. Asegúrate de tener **buena iluminación** (preferible luz natural o lámpara frontal).
3. El sistema detectará tu mano automáticamente y dibujará los **21 puntos clave** (landmarks) sobre ella.
4. En el panel derecho aparecerá la letra reconocida y su nivel de confianza.

**Consejos para mejores resultados:**
- Fondo liso (pared o escritorio de color uniforme).
- Mano visible en su totalidad dentro del cuadro.
- Mantén la seña estable al menos 1 segundo antes de leer el resultado.
- Evita movimiento excesivo mientras mantienes la seña.

---

## 5. Interpretación del indicador de confianza

El indicador de confianza muestra qué tan seguro está el modelo de la seña detectada.

### 5.1 Barra de confianza

```
▓▓▓▓▓▓▓▓▓▓░░░  78%   → El modelo está bastante seguro
▓▓▓▓▓░░░░░░░░  42%   → El modelo tiene dudas (borde amarillo)
░░░░░░░░░░░░░   0%   → No hay mano detectada
```

### 5.2 Colores del borde de la tarjeta

| Color | Confianza | Significado |
|-------|-----------|-------------|
| 🔴 Rojo (`#E30613`) | ≥ 60% | Predicción confiable — la letra mostrada es la detectada. |
| 🟡 Amarillo (`#f0a500`) | < 60% | Predicción ambigua — puede no ser correcta; ajusta la posición. |
| ⬜ Sin borde | — | No hay mano visible en el cuadro. |

> **Recomendación:** espera el borde rojo para considerar la letra como válida.

---

## 6. Historial de señas y construcción de texto

### 6.1 Cómo funciona

El sistema agrega automáticamente cada letra al **texto acumulado** cuando:
- La confianza supera el umbral configurado (por defecto 60%).
- La misma letra se mantiene estable durante al menos un intervalo de procesamiento.

### 6.2 Leer el texto acumulado

El texto acumulado aparece en el panel derecho, debajo de la tarjeta de letra. Muestra todas las letras reconocidas desde el inicio de la sesión o desde el último borrado.

### 6.3 Limpiar el historial

Presiona el botón **"Limpiar texto"** para reiniciar el texto acumulado.
- El video y la detección de manos **no se detienen**.
- El historial comienza de cero.

### 6.4 Límite del historial

Para evitar sobrecarga visual, el historial muestra las últimas letras acumuladas en pantalla. El registro completo de la sesión no se guarda a disco.

---

## 7. Dashboard de Métricas QA

### 7.1 Acceder al dashboard

En la barra lateral (o menú superior en pantallas pequeñas), haz clic en **"Métricas QA"**.

### 7.2 Contenido del dashboard

| Sección | Qué muestra |
|---------|-------------|
| **Métricas del modelo** | Accuracy, Precision, Recall y F1-Score del clasificador SVM sobre el dataset de evaluación. |
| **Rendimiento por etapa** | Latencia en milisegundos de cada paso del pipeline (captura, MediaPipe, clasificación, render). |
| **FPS sostenidos** | Cuadros por segundo medidos durante la sesión de prueba de 60 segundos. |
| **Log de auditoría** | Últimas 20 entradas del registro de eventos de la sesión (IDs anónimos, sin datos personales). |

### 7.3 Interpretar las métricas

- **Accuracy ≥ 85%:** el modelo cumple el umbral académico del proyecto.
- **Latencia total < 200 ms:** el pipeline es apto para uso en tiempo real.
- **FPS ≥ 24:** la captura es fluida para reconocimiento continuo.

---

## 8. Cierre de sesión

La sesión se cierra automáticamente a los **60 minutos** de haberse iniciado. Al expirar, la aplicación muestra nuevamente el formulario de inicio de sesión.

Para cerrar la sesión antes:
- Cierra la pestaña del navegador, o
- Recarga la página (se perderá el texto acumulado de la sesión).

> No hay botón de cierre de sesión explícito en la versión actual (funcionalidad prevista para versiones futuras).

---

## 9. Accesibilidad

LSP Vision AI cumple con el estándar **WCAG 2.1 Nivel AA**:

| Característica | Detalle |
|----------------|---------|
| Lector de pantalla | La letra detectada se anuncia automáticamente con `aria-live="polite"`. |
| Barra de confianza | Accesible como `role="progressbar"` con `aria-valuenow`. |
| Contraste de texto | Ratio mínimo de 4.5:1 en todo el texto visible. |
| Saltar navegación | Presiona `Tab` al cargar la página para acceder al enlace *"Saltar al contenido"*. |
| Regiones semánticas | Topbar con `role="banner"` y footer con `role="contentinfo"`. |

---

## 10. Preguntas frecuentes

**¿El sistema guarda mis imágenes o video?**
No. Los frames se procesan en memoria y se descartan inmediatamente. No se almacena ningún video ni imagen de las señas realizadas.

**¿Por qué la cámara no se activa?**
Verifica que el navegador tiene permiso para acceder a la cámara (ícono de cámara en la barra de direcciones → "Permitir siempre").

**¿Por qué la letra detectada es incorrecta?**
- Mejora la iluminación del entorno.
- Asegúrate de que toda la mano sea visible dentro del cuadro.
- Mantén la seña estática durante 1–2 segundos.
- Algunas letras LSP son visualmente similares; el modelo tiene mayor dificultad con ellas.

**¿Qué letras reconoce el sistema?**
El sistema reconoce las letras estáticas del alfabeto LSP implementadas en el dataset del equipo. Las letras que requieren movimiento (como la J o la Z) no están en el alcance de esta versión.

**¿Puedo usarlo en el teléfono?**
La aplicación es responsiva, pero el rendimiento del modelo puede variar en dispositivos móviles. Se recomienda el uso en computadora de escritorio o laptop.

**La sesión se cerró sola, ¿qué pasó?**
Las sesiones expiran a los 60 minutos por seguridad. Ingresa tu clave nuevamente para continuar.

---

## 11. Soporte y contacto

Este sistema fue desarrollado como proyecto Capstone para la Universidad Privada del Norte.

| Integrante | Rol |
|------------|-----|
| Rodriguez Chacara, Oscar Daniel | Desarrollo Full-Stack, ML, QA y Despliegue |
| Armas Alvarado, José Deyvis | Desarrollo y ML |
| Arias Chauca, Nicolás Enrry | Desarrollo y QA |
| Reátegui Arévalo, Oscar Manuel | Desarrollo y Despliegue |

**Docente:** Edward Jose Flores Masias

Para reportar problemas técnicos o consultas académicas, dirigirse al equipo durante las sesiones de sustentación o a través de los canales establecidos por la universidad.

---

*Versión 1.0 — Junio 2026 · LSP Vision AI · UPN Sistemas*
