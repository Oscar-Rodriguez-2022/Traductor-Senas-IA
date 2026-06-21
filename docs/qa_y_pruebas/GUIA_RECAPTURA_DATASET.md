# Guía de Recaptura del Dataset — LSP Vision AI
## Universidad Privada del Norte · Capstone Project Sistemas 2026
### Autor: Rodriguez Chacara, Oscar Daniel · Versión 3.1 · 2026-06-21

> **Estado al 2026-06-14 (INC-12 abierto):** La migración a la MediaPipe Tasks API reveló
> tasas de detección críticas en las letras O (0%), D (1.8%), J (0.8%), S (5.8%), F (13.7%) e I (18.9%).
> La letra **O no puede ser reconocida** con el dataset actual.
> Esta guía orienta la recaptura necesaria para superar los umbrales de calidad del proyecto.

Esta guía explica **qué letras necesitan recapturarse, por qué, y los pasos exactos** para
hacerlo antes de reentrenar el modelo final.

---

## Por qué es necesaria la recaptura

El script `augmentar_dataset.py` extrae los landmarks de cada imagen usando `MediaPipe HandLandmarker`
(Tasks API). Si el modelo no detecta una mano en la foto — por imagen borrosa, mano fuera de cuadro,
poca iluminación, pose muy plana o dedos solapados —, descarta la imagen y no genera ninguna muestra
para el modelo.

Al escanear el dataset completo (13 689 imágenes) con la nueva API se encontraron los problemas
descritos en la siguiente tabla:

| Letra | Imágenes en disco | Detectadas (Tasks API) | Tasa | Problema principal |
|---|---|---|---|---|
| **O** | 500 | **0** | **0%** | Puño circular completamente cerrado — la API no puede delimitar dedos individuales |
| **D** | 509 | 9 | 1.8% | Índice extendido con puño — la base de la palma queda oculta |
| **J** | 509 | 4 | 0.8% | Seña dinámica capturada en posición estática ambigua |
| **S** | 500 | 29 | 5.8% | Puño cerrado igual que A visto frontalmente |
| **F** | 509 | 70 | 13.7% | Dedos doblados con anular extendido — configuración atípica para el detector |
| **I** | 509 | 96 | 18.9% | Solo meñique extendido — poca masa visible de la mano |
| **A** | 500 | ~211 | ~42% | Puño lateral con pulgar; puede mejorarse con ángulo |
| **C** | 500 | ~213 | ~43% | Curvatura sin dedos separados; puede mejorarse con apertura |

> **Letras ya corregidas (INC-07, 2026-06-08):** N, Q, R, V — recapturadas con éxito, tasa ≥ 98%.

> **Nota técnica:** El modelo SVM solo puede reconocer letras con al menos 5 muestras detectadas.
> J terminó con 3 muestras en el dataset final de entrenamiento (el escaneo inicial detectó 4/509);
> se incluye en el modelo pero su fiabilidad es muy baja y no admite K-Fold (k≥5).
> Con 0 muestras, O queda excluida del modelo por completo.

---

## Letras a recapturar (orden de prioridad)

| Prioridad | Letra | Razón |
|---|---|---|
| 1 | **O** | 0 muestras — completamente excluida del modelo |
| 2 | **D** | 9 muestras — K-Fold y evaluación cruzada imposibles |
| 3 | **J** | 3 muestras finales — K-Fold y evaluación cruzada imposibles |
| 4 | **S** | 29 muestras — recall < 50%, no supera umbral de equidad |
| 5 | **F** | 70 muestras — recall bajo |
| 6 | **I** | 96 muestras — recall bajo |
| 7 | **A** | 211 muestras — funciona, pero la recaptura mejoraría la precisión |
| 8 | **C** | 213 muestras — ídem A |

---

## Guía visual de señas LSP difíciles

Antes de capturar, consulta la posición correcta de cada seña problemática:

| Letra | Descripción de la seña LSP | Truco para detección |
|---|---|---|
| **O** | Todos los dedos doblados formando un círculo con la punta del pulgar | Inclinar la mano 30° hacia la cámara para que el modelo vea el interior del anillo |
| **D** | Índice extendido, demás dedos doblados sobre pulgar | Mostrar el perfil lateral de la mano, no el dorso completo |
| **J** | Igual que I (meñique) con movimiento de gancho — capturar la posición final | Usar el frame final del gancho, mano a 45° |
| **S** | Puño cerrado con pulgar sobre los dedos (diferente de A) | Orientar el dorso completamente hacia la cámara, no el lateral |
| **F** | Pulgar e índice forman un círculo; medio, anular y meñique extendidos | Separar los tres dedos extendidos visiblemente hacia la cámara |
| **I** | Solo el meñique extendido, palma de frente | Colocar la mano más cerca al centro del encuadre; iluminación lateral |
| **A** | Puño cerrado con pulgar apoyado lateralmente en el índice | Inclinar la mano 20°-30° hacia la cámara para mostrar perspectiva |
| **C** | Todos los dedos curvados formando una C abierta | Abrir ligeramente más los dedos; el detector necesita separación |

---

## Pasos para recapturar

### Requisitos previos

- Python 3.12 instalado (versión de referencia del proyecto — ver Dockerfile/pyproject.toml)
- Archivo `hand_landmarker.task` en la raíz del proyecto (requerido por la Tasks API)
- Cámara web funcional
- Buena iluminación frontal (evitar luz de fondo que siluetea la mano)
- Fondo neutro (pared blanca o gris, sin objetos detrás de la mano)

> Si no tienes `hand_landmarker.task`, descárgalo con:
> ```
> python -c "import urllib.request; urllib.request.urlretrieve('https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task', 'hand_landmarker.task')"
> ```

### Paso 1 — Preparar el entorno de captura

```
Condiciones óptimas:
  - Iluminación frontal difusa (≥ 200 lux) o lámpara apuntando a la mano
  - Fondo uniforme, preferiblemente blanco o gris claro
  - Distancia de la mano a la cámara: 30-50 cm
  - La mano debe ocupar al menos el 30 % del encuadre
  - Variar levemente el ángulo entre capturas (+5° a -5°) para mayor variedad
```

### Paso 2 — Ejecutar capturar_dataset.py

Abre una terminal en la carpeta raíz del proyecto y ejecuta:

```
python scripts/capturar_dataset.py
```

O doble clic en `1_CAPTURAR_dataset.bat`.

### Paso 3 — Seleccionar cada letra a recapturar

Para cada letra problemática:

1. El script mostrará: `La letra 'X' ya tiene N fotos guardadas.`
2. Elige la opción **2 — Reemplazar** (borra las fotos antiguas y captura desde cero).
3. Coloca la mano en la posición correcta según la tabla de la sección anterior.
4. Presiona cualquier tecla en la ventana de la cámara para iniciar la captura automática.
5. **Mantén la seña estable** mientras se capturan las 500 fotos.
6. Varía **levemente** el ángulo de la mano cada 50-100 fotos.
7. Al terminar, el script pregunta `G (Guardar) o R (Repetir)`.
   - Si se vieron pocas veces el skeleton verde dibujado: **R** para repetir.
   - Si el skeleton apareció frecuentemente: **G** para guardar y continuar.

> **Nota sobre `capturar_dataset.py` y la API:** En la versión actual (`mediapipe==0.10.21`),
> el script de captura usa íntegramente la API antigua (`mp.solutions.hands`) — no se migró a la
> Tasks API junto con `lsp_core.py`. La captura de imágenes funciona correctamente; solo el núcleo
> de inferencia (`lsp_core.py`) y el dibujo en vivo de la app web usan la Tasks API.

### Paso 4 — Verificar la calidad antes de entrenar

Antes de ejecutar el entrenamiento, comprueba cuántas fotos detecta la Tasks API:

```
python -m scripts.augmentar_dataset
```

Lee el resumen al inicio. La salida deseable para las letras problemáticas:

```
  O:  450 utiles / 500 fotos    <-- antes era 0
  D:  430 utiles / 509 fotos    <-- antes era 9
  J:  400 utiles / 509 fotos    <-- antes era 4
  S:  460 utiles / 500 fotos    <-- antes era 29
  F:  440 utiles / 509 fotos    <-- antes era 70
  I:  430 utiles / 509 fotos    <-- antes era 96
```

Si alguna letra sigue en < 50 muestras, vuelve al Paso 3 y recaptura prestando atención a:
- Girar más la mano hacia la cámara para que el modelo vea los dedos con separación
- Aumentar la iluminación
- Acercar más la mano al centro del encuadre

### Paso 5 — Entrenar con augmentation

Una vez que todas las letras problemáticas tienen ≥ 50 muestras detectadas, ejecuta:

```
python -m scripts.augmentar_dataset
```

El script mostrará:
- Tabla de muestras originales y aumentadas por letra (×16)
- Accuracy del modelo en validación
- Reporte por letra (precision, recall, F1)
- Mensaje `[OK] modelo.pkl guardado`

---

## Criterio de calidad mínima

Antes de dar el modelo como listo para despliegue:

| Métrica | Mínimo requerido |
|---|---|
| Accuracy global (validación del script) | ≥ 85% |
| F1-score por letra | ≥ 0.70 en cada letra recapturada |
| Letras sin muestras detectadas | 0 (las 26 letras deben tener datos) |
| Recall mínimo por clase (test_etica.py) | > 0.50 para todas las letras |
| K-Fold k=5 ejecutable | Sí (todas las clases deben tener ≥ 5 muestras) |

---

## Consejos para señas con puño cerrado (O, A, S)

Las señas O, A y S son las más difíciles porque los dedos están curvados y la cámara 2D
pierde profundidad. Estrategias probadas:

- **O:** Inclinar la mano 30° lateralmente — el modelo necesita ver el hueco interior del anillo.
- **A/S:** Inclinar la mano 20°-30° hacia la cámara — MediaPipe necesita perspectiva para inferir profundidad.
- **Iluminación lateral suave** que cree sombras entre los dedos, ayudando a distinguir su separación.
- **No usar guante ni ropa oscura** — el contraste piel/fondo es lo que el modelo usa para delimitar la mano.
- Hacer la seña con la **mano en reposo** (no tensa) — los tendones marcados dificultan la detección.

---

## Después de entrenar: subir el modelo al repositorio

```bash
git add modelo.pkl
git commit -m "Actualizar modelo.pkl con dataset recapturado y augmentation x16"
git push
```

El nuevo `modelo.pkl` será descargado automáticamente por HuggingFace Spaces al actualizar el Space.

> **Importante:** `hand_landmarker.task` también debe estar en el repositorio o descargarse
> en el entorno de despliegue (Dockerfile o setup script).

---

## Privacidad y Protección de Datos durante la Recaptura

| Principio | Implementación |
|-----------|---------------|
| **Consentimiento informado** | Cada integrante captura sus propias señas voluntariamente. No se capturan imágenes de terceros sin consentimiento explícito. |
| **Minimización de datos** | Solo se capturan imágenes de la mano. No se capturan rostros, datos biométricos adicionales ni información personal. |
| **Privacidad por diseño** | `scripts/extraer_landmarks.py` convierte las imágenes a vectores de 42 coordenadas numéricas antes de compartirlas. Los compañeros comparten el CSV de coordenadas, **no las fotos**. |
| **Derecho de supresión** | Cualquier integrante puede solicitar eliminar sus muestras ejecutando `scripts/capturar_dataset.py` opción "Reemplazar" (opción 2) para su letra. |
| **No vinculación** | Los archivos CSV no contienen nombre, correo ni ningún dato personal — solo vectores numéricos y etiqueta de letra. |

**Referencia normativa:** GDPR Art. 25 (Privacidad por diseño por defecto) — documentado en `SEGURIDAD.md`.

---

## Referencia Rápida (rutas v3.0)

```
Captura:              python scripts/capturar_dataset.py    (o 1_CAPTURAR_dataset.bat)
Verificación:         python -m scripts.augmentar_dataset   (ver columna "utiles")
Entrenamiento:        python -m scripts.augmentar_dataset   (o 5_AUGMENTAR_y_ENTRENAR.bat)
Extraer landmarks:    python scripts/extraer_landmarks.py   (o COMPANEROS_extraer_landmarks.bat)
Subir modelo:         git add modelo.pkl && git commit -m "Dataset actualizado" && git push
Modelo Tasks API:     hand_landmarker.task (raíz del proyecto, 7.8 MB)
```

---

*Guía de Recaptura v3.1 · LSP Vision AI · UPN Sistemas 2026*
*Cambios v3.0 (2026-06-14): INC-12 documentado; tabla actualizada con letras críticas actuales
(O/D/J/S/F/I); requisito `hand_landmarker.task` añadido;
sección consejos O/A/S actualizada; criterios K-Fold añadidos; v2.0 conservaba INC-07/N/Q/R/S/V.*
*Cambios v3.1 (2026-06-21): Python corregido a 3.12 (versión real soportada, no 3.12/3.13);
mediapipe corregido a 0.10.21 (no 0.10.35); J corregido a 3 muestras finales (no 4) para
coincidir con `reportes/`; aclarado que `scripts/capturar_dataset.py` no migró a la Tasks API.*
