# Modelo de Datos — LSP Vision AI
## Diseño Incremental por Sprint
### Universidad Privada del Norte · Capstone Project Sistemas 2026
### Versión: 1.3 · Fecha: 2026-06-21

> Este documento describe las estructuras de datos del sistema, su evolución
> incremental por sprint y su coherencia con el diseño arquitectónico.
> Para el inventario operativo, diccionario unificado y pipelines, ver [`MANUAL_BASE_DE_DATOS.md`](MANUAL_BASE_DE_DATOS.md).

---

## 1. Vector de Landmarks (Núcleo del modelo ML)

**Módulo:** `src/lsp_core.py` · **HU:** HU-06 (CA-06.1, CA-06.2, CA-06.3)

```
Entrada: imagen BGR (numpy.ndarray, forma HxWx3)
         └─ captura desde webcam (640×480) o PNG del dataset

Extracción: MediaPipe HandLandmarker (Tasks API, mp.tasks.vision) → 21 puntos anatómicos (NOMBRES_LANDMARKS, ver §8)
            Cada punto: (x, y) normalizados en [0.0, 1.0]
            Configuración: num_hands=1, min_hand_detection_confidence=0.6

Salida: vector de 42 floats = [x0, y0, x1, y1, ..., x20, y20]

Restricciones (landmarks_validos()):
  - len(vector) == 42          (NUM_FEATURES)
  - todos los valores son finitos (no NaN, no Inf)
  - todos los valores en [-0.5, 1.5]  ← margen para manos parcialmente fuera de encuadre

Forma numpy: (1, 42)  al predecir con SVM
             (N, 42)  al entrenar (N = total de muestras del dataset)
```

**Evolución incremental:**
- Sprint 1: vector básico de 42 floats para entrenamiento offline
- Sprint 1: augmentación × 16 con transformaciones geométricas sobre el vector
- Sprint 2: validación `landmarks_validos()` antes de predecir (seguridad)
- Sprint 3: `explicar_prediccion()` consume este vector y devuelve dict XAI (§8)
- Sprint 3: confirmado como único dato procesado en tiempo real (ningún frame persistido → GDPR)

---

## 2. Modelo SVM (`modelo.pkl`)

**Módulo:** `src/lsp_core.py` · **HU:** HU-07 (CA-07.1, CA-07.3), HU-10 (CA-10.1)

```python
# Estructura lógica del objeto serializado con joblib
{
    "classifier": sklearn.svm.SVC(
        kernel="rbf",
        C=10,
        probability=True,   # habilita predict_proba() para confianza y XAI
        gamma="scale"
    ),
    "classes_": ["a", "b", "c", ..., "z"],  # letras presentes en el dataset
    "n_features_in_": 42                     # validación automática de dimensión
}

# Dimensiones típicas del dataset de entrenamiento
# Letras: 25 de 26 (a–z, excluyendo la o — sin detección válida, ver INC-12)
# Muestras por letra: muy desigual, de 3 (j) y 9 (d, s) hasta ~500–997 (la mayoría)
# Total landmarks extraídos del dataset crudo: 9 585 vectores × 42 features (reportes/metricas.json)
# El entrenamiento del modelo aplica además augmentación ×16 sobre estos vectores
```

**Archivo de integridad asociado:** `modelo.pkl.sha256`

```
modelo.pkl.sha256  ← hash SHA-256 de 64 chars, generado por calcular_hash_modelo()
                      verificado en tests de seguridad con verificar_integridad_modelo()
```

**Evolución incremental:**
- Sprint 1: SVM básico, entrenado desde imágenes en `data/`
- Sprint 1: augmentación de landmarks para balanceo de clases
- Sprint 2: carga mediante `@st.cache_resource` para reutilización entre sesiones
- Sprint 3: verificación de integridad SHA-256 antes de carga (protección contra PKL manipulado)

---

## 3. Imagen del Dataset

**Módulo:** `scripts/capturar_dataset.py` · **HU:** HU-04, HU-05

```
Ruta:     data/<letra>/<letra>_<índice>.png
Ejemplo:  data/a/a_0.png, data/a/a_1.png, ..., data/a/a_N.png

Formato:    PNG, color RGB/BGR
Resolución: variable (la captura es a resolución de webcam)
Contenido:  mano del usuario haciendo la seña de la letra <letra>

Restricciones:
  - Solo letras a–z en minúscula como directorio padre
  - El índice es autoincremental (no sobreescribe índices existentes)
  - MediaPipe debe detectar exactamente 1 mano; imágenes sin mano se descartan

No se almacena en producción: el sistema web procesa frames en memoria (GDPR Art. 25)
```

---

## 4. Exportación CSV de Landmarks (Dataset colaborativo)

**Módulo:** `scripts/extraer_landmarks.py` · **HU:** HU-05 (RF-12)

```
Ruta:     landmarks_csv/<usuario>_landmarks.csv  (carpeta local — excluida de git, ver .gitignore)
Columnas: letra, x0, y0, x1, y1, ..., x20, y20  (43 columnas en total)

Ejemplo:
  letra,x0,y0,x1,y1,...,x20,y20
  a,0.512,0.743,0.489,0.698,...,0.521,0.612
  b,0.601,0.812,...

Uso: scripts/entrenar_desde_csv.py carga todos los CSV de landmarks_csv/,
     los combina y entrena el SVM unificado.
```

---

## 5. Token de Sesión HMAC

**Módulo:** `src/lsp_auth.py` · **HU:** HU-13 (CA-13.x)

```
Formato: "<timestamp>.<nonce>.<firma>"

Ejemplo: "1749724337.a3f8c2b19d4e5f67.9e2a1b3c..."

Campos:
  timestamp (int como str) : Unix timestamp del momento de emisión
  nonce     (16 hex chars) : 8 bytes aleatorios, generados con secrets.token_hex(8)
  firma     (64 hex chars) : HMAC-SHA256(key=PEPPER, msg="timestamp.nonce")

Validación (verificar_token()):
  1. Exactamente 3 partes separadas por "."
  2. HMAC-SHA256 del par (timestamp, nonce) coincide con la firma recibida
  3. time.time() - timestamp <= SESSION_EXPIRY_MINUTES × 60  (60 min)

Almacenamiento: st.session_state["lsp_token"] (memoria del navegador, no persiste)
```

**Constantes de seguridad (no modificar sin análisis de impacto):**

| Constante | Valor | Propósito |
|-----------|-------|-----------|
| `PEPPER` | `"LSP_UPN_2026"` | Sal fija de aplicación concatenada antes del hash |
| `_PBKDF2_ITERATIONS` | `260 000` | Mínimo OWASP 2023 para PBKDF2-HMAC-SHA256 |
| `SESSION_EXPIRY_MINUTES` | `60` | Expiración de sesión en minutos |
| `MAX_INTENTOS` | `5` | Intentos fallidos consecutivos antes de bloqueo |
| `BLOQUEO_SEGUNDOS` | `300` | Duración del bloqueo anti-fuerza-bruta (5 min) |

**Estado de rate limiting (en memoria, por proceso):**

```python
_intentos_fallidos: int   # contador de intentos fallidos consecutivos
_ultimo_fallo_ts: float   # Unix timestamp del último fallo registrado
_rate_lock: threading.Lock  # acceso thread-safe al estado de bloqueo
```

---

## 6. Entrada del Log de Auditoría (JSON Lines)

**Módulo:** `src/lsp_audit.py` · **Archivo:** `audit_log.jsonl` · **HU:** HU-14

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

| Evento | Disparado desde |
|--------|-----------------|
| `LOGIN_OK` | `lsp_auth._render_login()` — autenticación exitosa |
| `LOGIN_FAIL` | `lsp_auth._render_login()` — clave incorrecta |
| `SESION_EXPIRADA` | `lsp_auth.login_requerido()` — token vencido |
| `PAGINA_VISITADA` | `src/app.py` — primera carga de la página principal |
| `TRADUCCION_INICIADA` | `src/app.py` — usuario activa la cámara WebRTC |
| `TRADUCCION_DETENIDA` | `src/app.py` — usuario detiene la cámara WebRTC |

**Política de retención:** entradas con más de 7 días se eliminan via `purgar_log_antiguo(dias=7)`.
**En Streamlit Cloud:** el archivo es efímero (filesystem volátil); en entorno local persiste entre reinicios.

---

## 7. Estado en Tiempo Real del Traductor (En Memoria)

**Módulo:** `src/lsp_video.py` · **Clase:** `Traductor` · **HU:** HU-08, HU-10, HU-16, HU-22

Los atributos del `Traductor` se actualizan en el hilo de procesamiento WebRTC y se leen desde el hilo de UI de Streamlit. El acceso está protegido por `threading.Lock`.

```python
class Traductor(VideoProcessorBase):
    letra:       str    # última letra detectada; "-" si no hay mano visible
    confianza:   float  # confianza de la predicción, rango 0.0–100.0
    mano:        bool   # True si MediaPipe detectó una mano en el último frame
    fps:         float  # FPS suavizados con EMA (α=0.2) para visualización estable
    alternativas: list  # top-5 dicts {letra, confianza} del resultado XAI (§8)
```

**Configuración de MediaPipe para video en tiempo real (Tasks API):**

```python
mp.tasks.vision.HandLandmarkerOptions(
    base_options=mp.tasks.BaseOptions(model_asset_path="hand_landmarker.task"),
    running_mode=mp.tasks.vision.RunningMode.VIDEO,  # sincrónico con timestamps
    num_hands=1,
    min_hand_detection_confidence=0.6,
)
```

> `mp.solutions` ya no se usa para la **detección**; sigue usándose únicamente para el
> **dibujo** del overlay (`mp.solutions.drawing_utils.draw_landmarks`) en `lsp_video.py`,
> ya que la Tasks API no incluye utilidades de dibujo propias.

**Pipeline de un frame:**

```
recv(av.VideoFrame)
  → BGR 640×480 → resize RGB 320×240
  → HandLandmarker.detect_for_video()
  → landmarks_validos()
  → explicar_prediccion()  ← obtiene letra + confianza + alternativas XAI sin coste extra
  → draw_landmarks (mp.solutions.drawing_utils) + badges overlay
  → actualiza atributos bajo lock
  → retorna av.VideoFrame anotado
```

---

## 8. Resultado XAI — `explicar_prediccion()`

**Módulo:** `src/lsp_core.py` · **HU:** HU-16 (CA-16.2)

```python
# Retorno de lsp_core.explicar_prediccion(modelo, landmarks, top_n=5)
{
    "letra":        str,          # letra principal predicha (a-z)
    "confianza":    float,        # confianza en % de la letra principal (0.0–100.0)
    "alternativas": [             # top_n candidatos ordenados de mayor a menor confianza
        {"letra": str, "confianza": float},
        ...
    ],
    "n_clases":     int,          # total de clases conocidas por el modelo
}
```

**Estructuras XAI complementarias (constantes en `lsp_core`):**

```python
# NOMBRES_LANDMARKS: dict[int, str]
# Mapa de índice de landmark (0–20) a nombre anatómico en español
{
    0: "Muñeca",
    1: "Base pulgar",  2: "Nudillo pulgar",  3: "Falange pulgar",  4: "Punta pulgar",
    5: "Base índice",  ...
    17: "Base meñique", 18: "Nudillo meñique", 19: "Falange meñique", 20: "Punta meñique",
}

# SESGOS_CONOCIDOS: dict[str, str]
# Limitaciones documentadas del modelo para transparencia con el usuario
{
    "diversidad_entrenamiento": "El modelo fue entrenado con datos de 4 personas ...",
    "letras_dinamicas":         "J y Z requieren movimiento y no están soportadas ...",
    "iluminacion":              "El rendimiento se degrada con iluminación insuficiente ...",
    "letras_similares":         "Confusión conocida entre A/S/E, B/F, G/Q ...",
    "sesgo_de_datos":           "Algunas letras pueden tener menos muestras ...",
}
```

---

## 9. Reporte de Métricas QA

**Módulo:** `qa/` · **HU:** HU-17, HU-22

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
| Sprint 2 | Token HMAC, log de auditoría JSONL (`audit_log.jsonl`), reportes QA | HU-13, HU-14, HU-17, HU-22 |
| Sprint 3 | Estado en tiempo real del Traductor (5 atributos, thread-safe) | HU-08, HU-10, HU-22 |
| Sprint 3 | Dict XAI de `explicar_prediccion()`, NOMBRES_LANDMARKS, SESGOS_CONOCIDOS | HU-16 |
| Sprint 3 | Rate limiting en memoria (_intentos_fallidos, _ultimo_fallo_ts, _rate_lock) | HU-13 |
| Sprint 3 | Integridad del modelo (modelo.pkl.sha256, verificar_integridad_modelo) | HU-10 |
| Sprint 3 | Efemeralidad en Streamlit Cloud confirmada (GDPR Art. 25), política retención 7 días | HU-14, HU-20 |

---

## Historial de Versiones

| Versión | Fecha | Cambio |
|---------|-------|--------|
| 1.0 | 2026-06-12 | Versión inicial — 7 estructuras de datos documentadas con evolución por sprint |
| 1.1 | 2026-06-13 | Añadir §7 estado Traductor, §8 XAI (explicar_prediccion + NOMBRES_LANDMARKS + SESGOS_CONOCIDOS); documentar rate limiting, verificación SHA-256 del modelo, ruta real audit_log.jsonl, constantes de seguridad |
| 1.2 | 2026-06-16 | Nota sobre landmarks_csv/ como carpeta local excluida de git; referencia cruzada a MANUAL_BASE_DE_DATOS.md |
| 1.3 | 2026-06-21 | Corrección §1/§2/§7: configuración real de MediaPipe Tasks API (antes mostraba `mp.solutions.hands.Hands`, ya migrado); 25 letras reales (no "j y z excluidas") |
