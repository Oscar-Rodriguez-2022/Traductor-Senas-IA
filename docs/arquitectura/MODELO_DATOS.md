# Modelo de Datos — LSP Vision AI
## Diseño Incremental por Sprint
### Universidad Privada del Norte · Capstone Project Sistemas 2026

> Este documento describe las estructuras de datos del sistema, su evolución
> incremental por sprint y su coherencia con el diseño arquitectónico.

---

## 1. Vector de Landmarks (Núcleo del modelo ML)

**Introducido en:** Sprint 1 — HU-06, HU-07

```
Entrada: imagen BGR (numpy.ndarray, forma HxWx3)
         └─ captura desde webcam (640×480) o PNG del dataset

Extracción: MediaPipe Hands → 21 puntos anatómicos
            Cada punto: (x, y) normalizados en [0.0, 1.0]

Salida: vector de 42 floats = [x0, y0, x1, y1, ..., x20, y20]

Restricciones de validación (landmarks_validos()):
  - len(vector) == 42
  - todos los valores son finitos (no NaN, no Inf)
  - todos los valores en [-0.5, 1.5]  ← margen para manos parcialmente fuera de encuadre

Forma numpy: (1, 42)  al predecir con SVM
             (N, 42)  al entrenar (N = total de muestras del dataset)
```

**Evolución incremental:**
- Sprint 1: vector básico de 42 floats para entrenamiento offline
- Sprint 1: augmentación × 16 con transformaciones geométricas sobre el vector
- Sprint 2: validación `landmarks_validos()` antes de predecir (seguridad)
- Sprint 3: confirmado como único dato procesado en tiempo real (ningún frame persistido → GDPR)

---

## 2. Modelo SVM (`modelo.pkl`)

**Introducido en:** Sprint 1 — HU-07

```python
# Estructura lógica del objeto serializado con joblib
{
    "classifier": sklearn.svm.SVC(
        kernel="rbf",
        C=10,
        probability=True,   # habilita predict_proba() para confianza
        gamma="scale"
    ),
    "classes_": ["a", "b", "c", ..., "z"],  # letras presentes en el dataset
    "n_features_in_": 42                     # validación automática de dimensión
}

# Dimensiones típicas del dataset de entrenamiento
# Letras: hasta 26 (a–z, excluyendo j y z que son dinámicas)
# Muestras por letra: ~100–500 imágenes × 16 augmentaciones = ~1600–8000
# Total dataset aumentado: O(50 000) vectores × 42 features
```

**Evolución incremental:**
- Sprint 1: SVM básico, entrenado desde imágenes en `data/`
- Sprint 1: augmentación de landmarks para balanceo de clases
- Sprint 2: carga mediante `@st.cache_resource` para reutilización entre sesiones

---

## 3. Entrada del Log de Auditoría (JSON Lines)

**Introducido en:** Sprint 2 — HU-14

```json
{
  "ts": "2026-06-12T14:32:17",
  "evento": "LOGIN_OK",
  "sesion": "a3f8c2b1",
  "detalle": ""
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `ts` | `str` (ISO 8601) | Timestamp del evento, precisión de segundos |
| `evento` | `str` | Identificador del evento (ver tabla de eventos abajo) |
| `sesion` | `str` (8 hex chars) | SHA-256[:8] del token de sesión — no reversible |
| `detalle` | `str` | Información contextual adicional, sin datos personales |

**Eventos estándar:**

| Evento | Disparado por |
|--------|---------------|
| `LOGIN_OK` | `lsp_auth._render_login()` — login exitoso |
| `LOGIN_FAIL` | `lsp_auth._render_login()` — clave incorrecta |
| `SESION_EXPIRADA` | `lsp_auth.login_requerido()` — token vencido |
| `PAGINA_VISITADA` | `app.py` — primera carga de la página principal |
| `TRADUCCION_INICIADA` | `app.py` — usuario activa la cámara |
| `TRADUCCION_DETENIDA` | `app.py` — usuario detiene la cámara |

**Política de retención:** entradas con más de 7 días se eliminan automáticamente via `purgar_log_antiguo()`.

**Evolución incremental:**
- Sprint 2: schema mínimo (ts, evento, sesion, detalle)
- Sprint 3: confirmado como efímero en Streamlit Cloud (filesystem volátil)

---

## 4. Token de Sesión HMAC

**Introducido en:** Sprint 2 — HU-13

```
Formato: "<timestamp>.<nonce>.<firma>"

Ejemplo: "1749724337.a3f8c2b19d4e5f67.9e2a1b3c..."

Campos:
  timestamp (int como str) : Unix timestamp del momento de emisión
  nonce     (16 hex chars) : 8 bytes aleatorios, generados con secrets.token_hex(8)
  firma     (64 hex chars) : HMAC-SHA256(key=PEPPER, msg="timestamp.nonce")

Validación:
  1. Exactamente 3 partes separadas por "."
  2. HMAC-SHA256 del par (timestamp, nonce) coincide con la firma recibida
  3. time.time() - timestamp <= SESSION_EXPIRY_MINUTES × 60  (60 min)

Almacenamiento: st.session_state["lsp_token"] (memoria del navegador, no persiste)
```

---

## 5. Imagen del Dataset

**Introducido en:** Sprint 1 — HU-04, HU-05

```
Ruta:     data/<letra>/<letra>_<índice>.png
Ejemplo:  data/a/a_0.png, data/a/a_1.png, ..., data/a/a_N.png

Formato:    PNG, color RGB/BGR
Resolución: variable (la captura es a resolución de webcam)
Contenido:  mano del usuario haciendo la seña de la letra <letra>

Restricciones:
  - Solo letras a–z en minúscula como directorio padre
  - El índice es autoincremental (A.py no sobreescribe índices existentes)
  - MediaPipe debe detectar exactamente 1 mano; imágenes sin mano se descartan

No se almacena en producción: el sistema web procesa frames en memoria (GDPR Art. 25)
```

---

## 6. Exportación CSV de Landmarks (Dataset colaborativo)

**Introducido en:** Sprint 1 — HU-05 (RF-12)

```
Ruta:     landmarks_csv/<usuario>_landmarks.csv
Columnas: letra, x0, y0, x1, y1, ..., x20, y20  (43 columnas en total)

Ejemplo:
  letra,x0,y0,x1,y1,...,x20,y20
  a,0.512,0.743,0.489,0.698,...,0.521,0.612
  b,0.601,0.812,...

Uso: entrenar_desde_csv.py carga todos los CSV de landmarks_csv/,
     los combina y entrena el SVM unificado.
```

---

## 7. Reporte de Métricas QA

**Introducido en:** Sprint 2 — HU-17, HU-22

```
reportes/
├── metricas.json          ← accuracy, precision_macro, recall_macro, f1_macro
├── metricas_por_clase.csv ← letra, precision, recall, f1, support
├── metricas_resumen.csv   ← resumen de métricas globales
├── benchmark.csv          ← etapa, latencia_ms (captura|mediapipe|svm|render)
├── fps.csv                ← t_seg, fps, fps_ema
├── cross_validation.csv   ← fold, accuracy, precision, recall, f1
├── confusion_matrix.csv   ← matriz N×N de letras
├── confusion_matrix.png   ← heatmap PNG (560px)
├── robustez.csv           ← condicion, accuracy, comentario
├── recursos.csv           ← t_seg, ram_mb, cpu_pct
└── stress.csv             ← n_frames, ram_mb, errores
```

---

## Evolución Incremental del Modelo de Datos por Sprint

| Sprint | Artefacto añadido | HU relacionada |
|--------|-------------------|----------------|
| Sprint 1 | Vector de landmarks 42-d, modelo.pkl, imágenes dataset, CSV colaborativo | HU-04 a HU-07 |
| Sprint 2 | Token de sesión HMAC, log de auditoría JSONL, reportes QA | HU-13, HU-14, HU-17, HU-22 |
| Sprint 3 | Confirmación de efemeralidad (GDPR), políticas de retención del log | HU-20 |

---

## Historial de Versiones

| Versión | Fecha | Cambio |
|---------|-------|--------|
| 1.0 | 2026-06-12 | Versión inicial — 7 estructuras de datos documentadas con evolución por sprint |
