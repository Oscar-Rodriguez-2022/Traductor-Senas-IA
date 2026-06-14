# Manual de Usuario — LSP Vision AI
## Sistema Interactivo de Visión Artificial para la Comunicación Inclusiva (LSP)
### Universidad Privada del Norte · Capstone Project Sistemas 2026-1
**Versión:** 2.1 · **Fecha:** 2026-06-13
**Autores:** Equipo LSP Vision AI — UPN Ingeniería de Sistemas

---

## Índice

1. [Descripción general del sistema](#1-descripción-general-del-sistema)
2. [Requisitos del sistema](#2-requisitos-del-sistema)
3. [Acceso e inicio de sesión](#3-acceso-e-inicio-de-sesión)
4. [Pantalla principal — Traductor en tiempo real](#4-pantalla-principal--traductor-en-tiempo-real)
5. [Interpretación del indicador de confianza](#5-interpretación-del-indicador-de-confianza)
6. [Historial de señas y construcción de texto](#6-historial-de-señas-y-construcción-de-texto)
7. [Dashboard de Métricas QA](#7-dashboard-de-métricas-qa)
8. [Panel de explicabilidad del sistema de IA](#8-panel-de-explicabilidad-del-sistema-de-ia)
9. [Cierre de sesión](#9-cierre-de-sesión)
10. [Accesibilidad](#10-accesibilidad)
11. [Preguntas frecuentes](#11-preguntas-frecuentes)
12. [Soporte y contacto](#12-soporte-y-contacto)

---

## 1. Descripción General del Sistema

**LSP Vision AI** es una aplicación web que traduce en tiempo real los gestos estáticos del **alfabeto manual de la Lengua de Señas Peruana (LSP)** a texto, usando la cámara web del dispositivo. Fue desarrollada como proyecto Capstone de la Universidad Privada del Norte con fines académicos e inclusivos.

### 1.1 Pipeline de funcionamiento

El sistema opera en cinco etapas que se ejecutan en menos de 20 milisegundos por frame:

```
┌──────────┐    ┌────────────────┐    ┌─────────────────┐    ┌──────────┐    ┌────────────┐
│  Cámara  │ →  │ Captura WebRTC │ →  │ MediaPipe Hands  │ →  │   SVM    │ →  │ Resultado  │
│   web    │    │   (320×240 px) │    │  21 landmarks   │    │  kernel  │    │  en UI     │
└──────────┘    └────────────────┘    └─────────────────┘    │   RBF    │    └────────────┘
                                             ↓                └──────────┘
                                     42 coordenadas (x,y)
                                      normalizadas [0,1]
```

### 1.2 Características principales

| Característica | Detalle |
|---|---|
| **Reconocimiento en tiempo real** | Predicción < 20 ms por frame, ≥ 24 FPS sostenidos |
| **Indicador de confianza** | Muestra el porcentaje de certeza del modelo (0–100%) |
| **Privacidad por diseño** | Ningún frame ni dato personal se almacena en disco |
| **Accesibilidad WCAG 2.1 AA** | Compatible con lectores de pantalla, contraste ≥ 4.5:1 |
| **Sesión segura** | Token HMAC-SHA256 con expiración de 60 minutos |
| **Explicabilidad XAI** | Panel que describe cómo la IA toma sus decisiones |

### 1.3 Letras del alfabeto LSP reconocidas

El sistema reconoce las letras del alfabeto manual LSP que se realizan con gesto estático:

> **A B C D E F G H I K L M N O P Q R S T U V W X Y**

> **Nota:** Las letras **J** y **Z** requieren movimiento de la mano (gesto dinámico) y están fuera del alcance de la versión actual del sistema.

---

## 2. Requisitos del Sistema

### 2.1 Para uso en la web (versión desplegada)

| Requisito | Mínimo recomendado |
|---|---|
| Navegador | Google Chrome 112+ · Firefox 113+ · Microsoft Edge 112+ |
| Cámara web | Resolución mínima 640 × 480 px · 15 FPS o superior |
| Conexión a internet | Banda ancha para carga inicial; el modelo corre en el servidor |
| Permisos | El navegador debe tener permiso para acceder a la cámara |
| Pantalla | 1024 × 768 px mínimo (recomendado 1280 × 720) |

### 2.2 Para instalación local

| Requisito | Versión |
|---|---|
| Python | **3.12** (MediaPipe 0.10.21 no soporta Python 3.13) |
| Sistema operativo | Windows 10+, Ubuntu 20.04+, macOS 12+ |
| RAM | Mínimo 4 GB (recomendado 8 GB) |
| CPU | Con soporte SSE4 (Intel i5 6ª gen+ o equivalente AMD) |

---

## 3. Acceso e Inicio de Sesión

### 3.1 Abrir la aplicación

**Versión web desplegada:**
- Abre la URL del servidor en tu navegador (consulta al equipo docente la URL vigente).

**Versión local:**
```bash
streamlit run src/app.py
# Luego abre: http://localhost:8501
```

### 3.2 Pantalla de inicio de sesión

Al abrir la aplicación verás únicamente el formulario de acceso. El traductor y sus funciones no son visibles hasta autenticarse correctamente.

```
┌──────────────────────────────────────────────┐
│                                              │
│           LSP Vision AI                      │
│     Universidad Privada del Norte            │
│                                              │
│   Clave de acceso:  [____________________]   │
│                                              │
│              [  Ingresar  ]                  │
│                                              │
└──────────────────────────────────────────────┘
```

### 3.3 Ingresar la clave

1. Escribe la clave de acceso en el campo indicado.
   - **Clave de demostración:** `UPN2026`
   - En producción, la clave se configura en los secretos del servidor (`.streamlit/secrets.toml`).
2. Presiona el botón **Ingresar** o la tecla `Enter`.
3. Si la clave es correcta, serás redirigido al traductor y se creará una sesión válida por **60 minutos**.

### 3.4 Tabla de resultados de autenticación

| Situación | Resultado en pantalla |
|---|---|
| Clave correcta | Redirección al traductor. Sesión activa 60 min. |
| Clave incorrecta (intentos 1–4) | "Clave incorrecta. Intentos restantes: N" |
| Quinto intento fallido | Cuenta bloqueada por 5 minutos. |
| Cuenta bloqueada | "Demasiados intentos fallidos. Espera 5 minutos." |
| Sesión expirada (> 60 min) | Formulario de inicio de sesión nuevamente. |

> **Privacidad:** el sistema no registra tu identidad ni dirección IP. Solo guarda un identificador de sesión anónimo de 8 caracteres (SHA-256 truncado) para el log de auditoría.

### 3.5 Protección anti-fuerza-bruta (Rate Limiting)

El módulo `lsp_auth.py` implementa un control de rate limiting thread-safe:

| Parámetro | Valor configurado |
|---|---|
| Intentos permitidos antes del bloqueo | 5 (`MAX_INTENTOS = 5`) |
| Duración del bloqueo | 5 minutos — 300 segundos (`BLOQUEO_SEGUNDOS = 300`) |
| Mecanismo | `threading.Lock` para operaciones atómicas |
| Protección contra timing attacks | `hmac.compare_digest()` en lugar de `==` |
| Reseteo | Automático al expirar el período o al ingresar correctamente |

**Mensaje durante el bloqueo:**
```
  Demasiados intentos fallidos.
  Por seguridad, el acceso está bloqueado.
  Espera 5 minutos e intenta nuevamente.
```

> **Para evaluadores y docentes:** si durante una demostración se alcanza el límite de 5 intentos, espera 5 minutos o reinicia el servidor local ejecutando `streamlit run src/app.py`.

---

## 4. Pantalla Principal — Traductor en Tiempo Real

### 4.1 Vista general de la interfaz

```
┌──────────────────────────────────────────────────────────────────┐
│  LSP Vision AI                 [Métricas QA]      [Cerrar ×]    │
├────────────────────────────┬─────────────────────────────────────┤
│                            │  LETRA DETECTADA                   │
│                            │  ┌──────────────────┐              │
│     [CÁMARA EN VIVO]       │  │        A         │  94%         │
│                            │  └──────────────────┘              │
│  (skeleton de 21 puntos    │  ████████████████░░░  94%          │
│   dibujado sobre la mano)  │                                     │
│                            │  [EN VIVO]  [24.3 FPS]             │
│                            │                                     │
│                            │  Texto acumulado:                  │
│                            │  H O L A                           │
│                            │          [Limpiar texto]           │
├────────────────────────────┴─────────────────────────────────────┤
│  ▼ ¿Cómo decide la IA? (expandir para ver explicación)          │
│  Estado del sistema  |  Estadísticas  |  Información del modelo │
└──────────────────────────────────────────────────────────────────┘
```

### 4.2 Activar la cámara

1. Al cargar la pantalla principal, el navegador pedirá permiso para usar la cámara.
2. Haz clic en **"Permitir"** en el aviso emergente del navegador.
3. El video en vivo aparecerá en el panel izquierdo.
4. Espera a que el indicador cambie de **"Conectando…"** a **"[EN VIVO]"** (2–5 segundos).

> Si usas una red corporativa o universitaria y la cámara no conecta, el sistema tiene configurado un servidor TURN (`openrelay.metered.ca`) como respaldo para redes con NAT simétrico.

### 4.3 Realizar una seña correctamente

**Posición óptima:**
- Coloca tu mano frente a la cámara a **30–60 cm** de distancia.
- Mantén toda la mano **visible** dentro del cuadro de video.
- Asegúrate de tener **buena iluminación** frontal (luz natural o lámpara dirigida).
- Usa un **fondo liso** (pared, mesa de color uniforme).

**Proceso de reconocimiento:**
1. MediaPipe detecta tu mano y dibuja los **21 puntos clave (landmarks)** en tiempo real.
2. El sistema extrae las 42 coordenadas normalizadas de esos puntos.
3. El SVM clasifica el vector en una letra del alfabeto LSP.
4. El resultado aparece en el panel derecho con la letra y su porcentaje de confianza.

**Consejos para mejores resultados:**
- Mantén la seña **estable** al menos 1 segundo antes de leer el resultado.
- Evita movimiento excesivo de la mano mientras haces la seña.
- Si la confianza es baja (borde amarillo), intenta mejorar la iluminación o el ángulo.
- Verifica que toda la mano —incluida la muñeca— sea visible en el cuadro.

### 4.4 Indicadores en el video en vivo

| Elemento | Descripción |
|---|---|
| **Puntos de colores** | 21 landmarks de MediaPipe dibujados sobre la mano (azul = nudillos, rojo = puntas) |
| **Líneas de conexión** | Esqueleto de la mano que muestra la estructura de 5 dedos |
| **Badge [EN VIVO]** | Confirma que el stream de video está activo |
| **Badge [X FPS]** | FPS suavizados con media exponencial (objetivo ≥ 24 FPS) |

---

## 5. Interpretación del Indicador de Confianza

### 5.1 ¿Qué es la confianza?

La confianza es la **probabilidad calibrada** que el modelo SVM asigna a la letra predicha:

```
Confianza (%) = predict_proba(vector_42_coords)[clase_predicha] × 100
```

Es un valor entre 0% y 100% que indica qué tan seguro está el modelo de su predicción. No es un umbral arbitrario: proviene del método de calibración de Platt aplicado al SVM durante el entrenamiento.

### 5.2 Barra de confianza

```
████████████████████░░  92%   → Alta confianza — predicción fiable
████████████░░░░░░░░░░  55%   → Confianza baja — ajustar posición de mano
░░░░░░░░░░░░░░░░░░░░░░   0%   → Sin mano detectada en el cuadro
```

### 5.3 Colores del borde de la tarjeta de resultado

| Color del borde | Confianza | Significado y acción recomendada |
|---|---|---|
| **Rojo** `#E30613` | ≥ 60% | Predicción confiable — la letra mostrada es la detectada. Puedes registrarla. |
| **Amarillo** `#f0a500` | < 60% con mano | Predicción ambigua — ajusta la posición, iluminación o ángulo. |
| **Sin borde** | — | No hay mano visible en el cuadro de video. |

> **Recomendación de uso:** registra la letra solo cuando el borde sea rojo (≥ 60% de confianza).

### 5.4 Letras visualmente similares en LSP

Algunas letras del alfabeto LSP tienen landmarks muy similares. El sistema los indica con borde amarillo:

| Grupo de confusión | Por qué se confunden |
|---|---|
| **A / S** | Dedos doblados, solo difiere la posición del pulgar |
| **B / 4** | Todos los dedos extendidos con variación mínima |
| **G / Q** | Índice extendido horizontal vs. vertical |
| **E / O** | Todos los dedos curvados con diferentes radios |

En estos casos, mantener la seña más estable y con mejor iluminación mejora la discriminación.

---

## 6. Historial de Señas y Construcción de Texto

### 6.1 Cómo funciona el acumulador

La aplicación acumula letras en el **texto de sesión** cuando:
- La confianza de la predicción supera el umbral configurado (≥ 60%).
- La misma letra se mantiene estable durante al menos un ciclo de actualización (0.4 s).

### 6.2 Leer el texto acumulado

El texto acumulado aparece debajo de la tarjeta de letra, en el panel derecho. Muestra todas las letras reconocidas desde el inicio de la sesión o desde el último borrado.

### 6.3 Limpiar el historial

1. Presiona el botón **"Limpiar texto"**.
2. El texto acumulado se borra completamente.
3. El video y la detección de manos **no se detienen**.
4. Puedes comenzar a construir una nueva palabra o frase.

> El historial **no se guarda en disco**. Se pierde al cerrar la pestaña o al que expire la sesión.

---

## 7. Dashboard de Métricas QA

### 7.1 Acceder al dashboard

En la barra de navegación superior (o lateral en pantallas pequeñas), selecciona **"Métricas QA"**.

### 7.2 Secciones del dashboard

| Sección | Qué muestra | Para qué sirve |
|---|---|---|
| **Métricas del modelo** | Accuracy, Precision, Recall, F1-Score del SVM | Verificar calidad del clasificador |
| **Rendimiento por etapa** | Latencia en ms de: carga modelo, detección MediaPipe, clasificación SVM, pipeline total | Diagnosticar cuellos de botella |
| **FPS sostenidos** | Cuadros por segundo durante la sesión de prueba de 60 s | Verificar fluidez del video |
| **Log de auditoría** | Últimas 20 entradas del registro de eventos (IDs anónimos) | Trazabilidad sin datos personales |

### 7.3 Interpretar las métricas

| Métrica | Umbral académico | Qué significa si está por debajo |
|---|---|---|
| **Accuracy** ≥ 85% | Umbral del Capstone | El modelo necesita más datos de entrenamiento |
| **Latencia pipeline** < 200 ms | Tiempo real viable | El servidor puede estar bajo carga alta |
| **FPS** ≥ 24 | Video fluido | Considera reducir resolución de cámara |
| **F1-Score por clase** ≠ 0% | Equidad mínima | Algunas letras necesitan recaptura de dataset |

---

## 8. Panel de Explicabilidad del Sistema de IA

### 8.1 ¿Cómo decide la IA?

En la pantalla principal, debajo del video, hay un panel expandible titulado **"¿Cómo decide la IA?"**. Al expandirlo, el sistema explica en lenguaje accesible el proceso completo de toma de decisión:

```
Etapa 1 — Cámara
  La cámara captura un frame (imagen) por cada ciclo de procesamiento.
  Se redimensiona a 320×240 px para optimizar la velocidad de análisis.

Etapa 2 — Detección de mano (MediaPipe Hands)
  El modelo de detección de manos de Google MediaPipe identifica la
  presencia de una mano y localiza sus 21 puntos anatómicos clave.

Etapa 3 — Extracción de landmarks
  Los 21 puntos (x, y) se normalizan al rango [0,1] relativo a la
  posición de la muñeca, generando un vector de 42 coordenadas.
  Este vector es independiente del tamaño y posición de la mano.

Etapa 4 — Clasificación SVM
  El vector de 42 coordenadas se pasa al clasificador SVM (kernel RBF,
  C=10, gamma="scale") entrenado con el dataset LSP del equipo UPN.
  El SVM produce una letra y la probabilidad de Platt como confianza.

Etapa 5 — Visualización
  La letra y su confianza (0–100%) se muestran en el panel de resultado
  con actualización cada 0.4 segundos vía st.fragment de Streamlit.
```

### 8.2 Panel de alternativas XAI (top-5)

Junto al pipeline, el panel expandible muestra también la **tabla de las 5 letras más probables** con su porcentaje de confianza:

| Posición | Letra | Confianza |
|---|---|---|
| 1ª (predicción principal) | A | 87 % |
| 2ª | S | 6 % |
| 3ª | E | 4 % |
| 4ª | T | 2 % |
| 5ª | M | 1 % |

Esto permite ver **cuánto "dudó" el modelo** entre letras similares. Cuando la primera y la segunda opción están muy cercanas (ej. A 55 %, S 40 %), el borde amarillo ya habrá aparecido en el panel de resultado indicando ambigüedad. Los valores son generados por `explicar_prediccion()` sin coste computacional adicional y verificados en `tests/test_etica.py::TestXAI` (14 tests).

### 8.3 Por qué usamos SVM y no una red neuronal profunda

El SVM con vectores de landmarks es **interpretable por diseño**:

- Las 42 entradas del modelo son coordenadas geométricas comprensibles.
- La confianza es una probabilidad calibrada, no una puntuación opaca.
- El modelo es auditable: se puede inspeccionar con las herramientas estándar de scikit-learn.
- Entrenamiento en < 3 segundos sin GPU, reproducible por cualquier integrante del equipo.

---

## 9. Cierre de Sesión

### 9.1 Cierre automático por expiración

La sesión se cierra automáticamente después de **60 minutos** desde el inicio. Al expirar, la aplicación muestra nuevamente el formulario de inicio de sesión. Ningún dato personal se almacena al cerrar.

### 9.2 Cierre manual

Para cerrar la sesión antes de que expire:
- Cierra la pestaña del navegador, **o**
- Recarga la página (`F5` o `Ctrl+R`).

> **Nota:** Al cerrar o recargar, el texto acumulado de la sesión se perderá. La función de cierre de sesión explícita con botón está prevista para versiones futuras del sistema.

---

## 10. Accesibilidad

LSP Vision AI cumple con el estándar **WCAG 2.1 Nivel AA**, validado en `tests/test_etica.py` y `tests/test_seguridad.py`:

| Criterio WCAG | Nivel | Implementación |
|---|---|---|
| **1.4.3 — Contraste** | AA | Ratio ≥ 4.5:1 en todos los textos visibles (`#6b6b6b`, `#767676`) |
| **1.3.1 — Info y relaciones** | A | `role="banner"`, `role="contentinfo"`, `role="progressbar"` |
| **4.1.3 — Mensajes de estado** | AA | `aria-live="polite"` en el panel de resultado (letra detectada) |
| **2.4.1 — Saltar bloques** | A | Skip-nav funcional (presiona `Tab` al cargar para activarlo) |
| **2.4.7 — Foco visible** | AA | Estilos `focus-visible` en todos los elementos interactivos |
| **3.1.1 — Idioma de la página** | A | `lang="es"` inyectado en el documento HTML |
| **1.1.1 — Contenido no textual** | A | `aria-hidden="true"` en emojis decorativos |
| **Barra de confianza** | AA | `role="progressbar"` con `aria-valuenow` y `aria-valuemax="100"` |

**Para usuarios de lectores de pantalla:**
- La letra detectada se anuncia automáticamente cada vez que cambia (modo `polite`).
- Presiona `Tab` al cargar para acceder al enlace "Saltar al contenido".
- Todos los controles son accesibles por teclado.

---

## 11. Preguntas Frecuentes

**¿El sistema guarda mis imágenes o video?**
No. Los frames de video se procesan en memoria RAM y se descartan inmediatamente. El vector de 42 coordenadas tampoco se guarda en disco. Solo se almacena un log de auditoría con timestamps e IDs de sesión anónimos, sin imágenes ni datos personales.

**¿Por qué la cámara no se activa?**
Verifica que el navegador tiene permiso para acceder a la cámara. Busca el ícono de cámara en la barra de direcciones → haz clic → selecciona "Permitir siempre". Si estás en una red corporativa o universitaria, el sistema usa un servidor TURN como respaldo para superar restricciones de NAT.

**¿Por qué la letra detectada es incorrecta?**
1. Mejora la iluminación — evita contraluz o sombras en la mano.
2. Asegúrate de que toda la mano sea visible en el cuadro.
3. Mantén la seña estática durante 1–2 segundos.
4. Algunas letras LSP (A/S, G/Q, B/E) son visualmente similares. Revisa la tabla de grupos de confusión en la sección 5.4.

**¿Qué letras reconoce el sistema?**
El sistema reconoce los gestos estáticos del alfabeto LSP: A B C D E F G H I K L M N O P Q R S T U V W X Y. Las letras J y Z (que requieren movimiento) no están en el alcance de la versión actual.

**¿Puedo usarlo en el teléfono?**
La interfaz es responsiva, pero el rendimiento puede variar en dispositivos móviles de gama baja. Se recomienda el uso en computadora de escritorio o laptop para una experiencia óptima.

**¿Qué pasa si escribo la clave incorrectamente 5 veces?**
El sistema bloquea el acceso durante 5 minutos como medida de seguridad. Aparecerá el mensaje "Demasiados intentos fallidos." Espera el tiempo indicado o, si ejecutas el servidor localmente, reinícialo con `streamlit run src/app.py`.

**La sesión se cerró sola, ¿qué pasó?**
Las sesiones expiran a los 60 minutos por seguridad. El texto acumulado se pierde al expirar. Ingresa tu clave nuevamente para continuar.

**¿Cómo sé si el modelo está entrenado y listo?**
En la pantalla principal, el panel de **Estado del sistema** muestra el indicador "Modelo cargado" en verde cuando `modelo.pkl` está disponible y ha pasado la verificación de integridad SHA-256.

---

## 12. Soporte y Contacto

Este sistema fue desarrollado como proyecto Capstone para la Universidad Privada del Norte (Ingeniería de Sistemas, 2026-1).

| Integrante | Rol |
|---|---|
| Rodriguez Chacara, Oscar Daniel | Desarrollo Full-Stack, ML, QA, Despliegue |
| Armas Alvarado, José Deyvis | Desarrollo y ML |
| Arias Chauca, Nicolás Enrry | Desarrollo y QA |
| Reátegui Arévalo, Oscar Manuel | Desarrollo y Despliegue |

**Docente:** Edward Jose Flores Masias
**Institución:** Universidad Privada del Norte — Facultad de Ingeniería

Para reportar problemas técnicos o consultas académicas, dirigirse al equipo durante las sesiones de sustentación o a través de los canales oficiales establecidos por la universidad.

**Repositorio del proyecto:** `https://github.com/Oscar-Rodriguez-2022/Traductor-Senas-IA`

---

*Manual de Usuario v2.1 — 2026-06-13 · LSP Vision AI · UPN Sistemas*
*Cambios v2.1: §8.2 añadido — panel de alternativas XAI top-5 (DT-19, `explicar_prediccion()`)*
*Cambios v2.0: nuevo pipeline diagram, sección de explicabilidad XAI, tabla de letras LSP, sección de accesibilidad WCAG expandida, preguntas frecuentes ampliadas, estado del sistema*
