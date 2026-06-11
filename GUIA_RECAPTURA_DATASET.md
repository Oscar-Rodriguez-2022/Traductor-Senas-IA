# Guía de Recaptura del Dataset — LSP Vision AI
## Universidad Privada del Norte · Capstone Project Sistemas 2026
### Autor: Rodriguez Chacara, Oscar Daniel

Esta guía explica **cuáles letras necesitan recapturarse, por qué, y los pasos exactos** para hacerlo antes de entrenar el modelo final.

---

## Por qué es necesaria la recaptura

El script `augmentar_dataset.py` extrae los landmarks de cada imagen usando MediaPipe. Si MediaPipe no detecta una mano en la foto (imagen borrosa, mano fuera de cuadro, poca iluminación, seña demasiado plana), descarta la imagen. Una foto descartada no genera ninguna muestra para el modelo.

Al evaluar el dataset actual se encontraron los siguientes problemas:

| Letra | Imágenes en disco | Muestras válidas (MediaPipe) | Problema |
|---|---|---|---|
| **A** | 500 | ~22 (4 %) | Fotos con mano cerrada plana — MediaPipe no detecta puño cerrado sin contexto de profundidad |
| **N** | 500 | 0 | Sin muestras utilizables — seña con dedos cruzados de difícil detección frontal |
| **Q** | 500 | 0 | Sin muestras utilizables — seña muy similar a G vista frontalmente |
| **R** | 500 | 0 | Sin muestras utilizables — dedos cruzados pierden separación con cámara 2D |
| **S** | 500 | 0 | Sin muestras utilizables — puño cerrado igual que A en 2D |
| **V** | 500 | 0 | Sin muestras utilizables — variación de ángulo no detectada en capturas actuales |

> **Nota:** El modelo SVM solo puede reconocer letras para las que tiene al menos 5 muestras. Las letras N, Q, R, S y V no serán reconocibles hasta ser recapturadas.

---

## Letras a recapturar (prioridad alta)

Recaptura en este orden de prioridad:

1. **N** — 0 muestras
2. **Q** — 0 muestras
3. **R** — 0 muestras
4. **S** — 0 muestras
5. **V** — 0 muestras
6. **A** — 22 muestras (insuficiente, necesita recaptura completa)

Las demás letras tienen muestras suficientes y el augmentation ×16 las mejorará.

---

## Guía visual de señas LSP difíciles

Antes de capturar, revisa la posición correcta de cada seña problemática:

| Letra | Descripción de la seña LSP |
|---|---|
| **A** | Puño cerrado con el pulgar apoyado lateralmente en el índice (no encima). Orientar el dorso de la mano hacia la cámara. |
| **N** | Índice, medio y anular doblados sobre el pulgar; meñique extendido. La mano debe estar ligeramente girada para que MediaPipe vea la separación de los dedos. |
| **Q** | Índice apuntando hacia abajo con pulgar extendido formando una "q". Girar la muñeca 90° para que sea distinguible de G. |
| **R** | Índice y medio cruzados. Separar los dedos visiblemente y mostrar la mano a 45° de ángulo para mejorar la detección. |
| **S** | Puño cerrado con el pulgar entre el índice y el medio. Para diferenciarlo de A: mostrar el dorso completamente, no el lateral. |
| **V** | Índice y medio en V abierta con los otros dedos cerrados. Inclinar la mano hacia la cámara para que los dos dedos queden claramente separados. |

---

## Pasos para recapturar

### Requisitos previos
- Python 3.12 instalado
- Cámara web funcional
- Buena iluminación frontal (evitar luz de fondo que siluetea la mano)
- Fondo neutro (pared blanca o gris, sin objetos detrás de la mano)

### Paso 1 — Preparar el entorno de captura

```
Condiciones óptimas de captura:
  - Iluminación: luz natural frontal o lámpara apuntando a la mano (no al rostro)
  - Fondo: uniforme, de preferencia blanco o gris claro
  - Distancia de la mano a la cámara: 30-50 cm
  - La mano debe ocupar al menos el 30 % del encuadre
  - Variar ligeramente el ángulo entre capturas (+5° a -5°) para mayor variedad
```

### Paso 2 — Ejecutar A.py

Abre una terminal en la carpeta del proyecto y ejecuta:

```
py -3.12 A.py
```

O doble clic en `1_CAPTURAR_dataset.bat`.

### Paso 3 — Seleccionar cada letra a recapturar

Para cada letra problemática (N, Q, R, S, V, A):

1. A.py mostrará el aviso: `La letra 'X' ya tiene 500 fotos guardadas.`
2. Escoge la opción **2 — Reemplazar** (borra las fotos antiguas y captura desde cero).
3. Coloca la mano en la posición correcta según la tabla de la sección anterior.
4. Presiona cualquier tecla en la ventana de la cámara para iniciar la captura automática.
5. **Mantén la seña estable** mientras se capturan las 500 fotos — el script avanza automáticamente.
6. Varía **levemente** el ángulo de la mano cada 50-100 fotos: inclina, rota o acerca/aleja un poco.
7. Al terminar, el script pregunta `G (Guardar) o R (Repetir)`.
   - Si se vieron pocas muestras con el skeleton verde dibujado: **R** para repetir.
   - Si el skeleton apareció frecuentemente: **G** para guardar y pasar a la siguiente letra.

### Paso 4 — Verificar la calidad antes de entrenar

Antes de ejecutar el entrenamiento, comprueba cuántas fotos detecta MediaPipe:

```
py -3.12 augmentar_dataset.py
```

Lee el resumen al inicio. La salida correcta debe verse así:

```
  A:  480 utiles / 500 fotos
  N:  390 utiles / 500 fotos       <-- antes era 0
  Q:  420 utiles / 500 fotos       <-- antes era 0
  R:  370 utiles / 500 fotos       <-- antes era 0
  S:  460 utiles / 500 fotos       <-- antes era 0
  V:  440 utiles / 500 fotos       <-- antes era 0
```

Si alguna letra sigue en 0 muestras, vuelve al Paso 3 y recaptura esa letra prestando atención a:
- Girar la mano más hacia la cámara para que MediaPipe vea los dedos con más separación
- Aumentar la iluminación
- Acercar más la mano al centro del encuadre

### Paso 5 — Entrenar con augmentation

Una vez que todas las letras problemáticas tienen muestras, ejecuta:

```
5_AUGMENTAR_y_ENTRENAR.bat
```

O desde la terminal:

```
py -3.12 augmentar_dataset.py
```

El script mostrará:
- Tabla de muestras originales y aumentadas por letra
- Accuracy del modelo en validación
- Reporte por letra (precision, recall, F1)
- Mensaje `[OK] modelo.pkl guardado`

---

## Criterio de calidad mínima

Antes de dar el modelo como listo para despliegue, el reporte debe mostrar:

| Métrica | Mínimo requerido |
|---|---|
| Accuracy global | ≥ 85 % |
| F1-score por letra | ≥ 0.70 en cada letra recapturada |
| Letras sin muestras | 0 (todas las letras deben tener datos) |

Si el accuracy es < 85 %, revisa las letras con F1 < 0.50 en el reporte y recaptúralas con mejor iluminación y ángulo.

---

## Consejos para señas con puño cerrado (A y S)

Las señas A y S son las más difíciles para MediaPipe porque los dedos están curvados hacia adentro y la cámara ve muy poca diferencia entre puntos. Estrategias probadas:

- **Inclinar la mano 20°-30°** hacia la cámara (no perpendicular al objetivo) — MediaPipe necesita cierta perspectiva para inferir la profundidad.
- **Iluminación lateral suave** que cree sombras entre los dedos, ayudando a distinguir su separación.
- **No usar guante ni ropa oscura** — el contraste piel/fondo es lo que MediaPipe usa para delimitar la mano.
- Hacer la seña con la **mano en reposo** (no tensa) — los tendones marcados dificultan la detección.

---

## Después de entrenar: subir el modelo al repositorio

```bash
git add modelo.pkl
git commit -m "Actualizar modelo.pkl con dataset recapturado y augmentation x16"
git push
```

El nuevo `modelo.pkl` será descargado automáticamente por HuggingFace Spaces al actualizar el Space.

---

## Referencia rápida

```
Letras a recapturar: A  N  Q  R  S  V
Comando de captura:  py -3.12 A.py          (o 1_CAPTURAR_dataset.bat)
Verificación:        py -3.12 augmentar_dataset.py  (ver columna "utiles")
Entrenamiento:       5_AUGMENTAR_y_ENTRENAR.bat
Subir modelo:        git add modelo.pkl && git commit -m "..." && git push
```
