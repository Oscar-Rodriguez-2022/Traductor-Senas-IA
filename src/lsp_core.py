"""
lsp_core.py — Núcleo reutilizable y TESTEABLE del Traductor LSP.

Centraliza la lógica que antes estaba incrustada en A.py / app.py / B.py:
carga del modelo, extracción de landmarks, validación y predicción.
Tanto la app como la suite de pruebas (tests/) y los scripts de QA (qa/)
importan desde aquí, evitando duplicar código y permitiendo medir calidad.

Trazabilidad de Historias de Usuario:
  HU-06 CA-06.1 — Extracción de landmarks  (extraer_landmarks, extraer_landmarks_de_archivo)
  HU-06 CA-06.2 — Normalización de landmarks (coordenadas en [0,1] de MediaPipe)
  HU-06 CA-06.3 — Integridad de datos       (landmarks_validos, cargar_dataset descarta None)
  HU-07 CA-07.1 — División para entrenamiento (cargar_dataset devuelve X, y)
  HU-07 CA-07.3 — Persistencia del modelo    (cargar_modelo desde modelo.pkl)
  HU-09 CA-09.1 — Detección 21 landmarks     (_get_hands, extraer_landmarks)
  HU-10 CA-10.1 — Carga correcta del modelo  (cargar_modelo con FileNotFoundError explícito)
  HU-10 CA-10.2 — Predicción en tiempo real  (predecir → letra + confianza%)
  HU-22 CA-22.3 — Liberación de recursos     (close_hands limpia _hands_cache)
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import warnings
warnings.filterwarnings("ignore")

import glob
import numpy as np

MODELO_PATH = "modelo.pkl"
NUM_LANDMARKS = 21          # puntos que devuelve MediaPipe Hands
NUM_FEATURES = 42           # 21 puntos * (x, y)
LETTERS = "abcdefghijklmnopqrstuvwxyz"
DATA_FOLDER = "data"

_hands_cache = {}


# ───────────────────────── Modelo ─────────────────────────
def cargar_modelo(path=MODELO_PATH):
    """
    Carga el modelo SVM entrenado desde disco.

    Args:
        path (str): Ruta al archivo pickle del modelo. Por defecto 'modelo.pkl'.

    Returns:
        object: Clasificador scikit-learn con métodos predict() y predict_proba().

    Raises:
        FileNotFoundError: Si el archivo no existe en la ruta indicada.
    """
    import joblib
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el modelo en '{path}'.")
    return joblib.load(path)


# ───────────────────────── MediaPipe ─────────────────────────
def _get_hands(static_image_mode=True):
    """
    Devuelve (y cachea) una instancia de MediaPipe Hands.

    Usar static_image_mode=True para imágenes fijas (dataset, QA).
    Usar static_image_mode=False para video en tiempo real (app.py).
    El caché evita reinicializar el modelo de detección en cada llamada.
    """
    import mediapipe as mp
    clave = bool(static_image_mode)
    if clave not in _hands_cache:
        _hands_cache[clave] = mp.solutions.hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=1,
            model_complexity=0,
            min_detection_confidence=0.6,
        )
    return _hands_cache[clave]


def extraer_landmarks(img, static_image_mode=True):
    """
    Extrae los landmarks de la mano detectada en una imagen BGR.

    Usa MediaPipe Hands para detectar 21 puntos anatómicos y devuelve
    sus coordenadas (x, y) normalizadas en el rango [0, 1].

    Args:
        img (numpy.ndarray): Imagen en formato BGR (como la devuelve cv2.imread).
        static_image_mode (bool): True para imágenes fijas, False para video. Por defecto True.

    Returns:
        list[float] | None: Lista de 42 floats [x0,y0,...,x20,y20] normalizados,
            o None si no se detecta ninguna mano en la imagen.
    """
    import cv2
    if img is None or not hasattr(img, "shape") or img.size == 0:
        return None
    hands = _get_hands(static_image_mode)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    resultado = hands.process(rgb)
    if not resultado.multi_hand_landmarks:
        return None
    landmarks = []
    for lm in resultado.multi_hand_landmarks[0].landmark:
        landmarks.append(lm.x)
        landmarks.append(lm.y)
    return landmarks if len(landmarks) == NUM_FEATURES else None


def extraer_landmarks_de_archivo(path):
    """
    Lee una imagen PNG del disco y extrae sus landmarks.

    Args:
        path (str): Ruta al archivo de imagen (PNG, JPG, etc.).

    Returns:
        list[float] | None: Vector de 42 floats, o None si no hay mano o el archivo no existe.
    """
    import cv2
    img = cv2.imread(path)
    return extraer_landmarks(img)


# ───────────────────────── Validación ─────────────────────────
def landmarks_validos(landmarks):
    """
    Valida que un vector de landmarks sea apto para clasificación.

    Verifica que el vector tenga exactamente NUM_FEATURES (42) valores,
    que todos sean números finitos (sin NaN ni Inf), y que estén dentro
    del rango [-0.5, 1.5] (MediaPipe normaliza en [0,1]; el margen
    cubre manos parcialmente fuera del encuadre).

    Args:
        landmarks: Lista, array o cualquier valor a validar.

    Returns:
        bool: True si el vector es válido para predicción, False en caso contrario.
    """
    if landmarks is None:
        return False
    arr = np.asarray(landmarks, dtype=float).ravel()
    if arr.shape[0] != NUM_FEATURES:
        return False
    if not np.all(np.isfinite(arr)):
        return False
    return bool(np.all(arr >= -0.5) and np.all(arr <= 1.5))


# ───────────────────────── Predicción ─────────────────────────
def predecir(modelo, landmarks):
    """
    Clasifica un vector de landmarks con el modelo SVM entrenado.

    Usa predict_proba() si está disponible (SVM con probability=True)
    para devolver la confianza como porcentaje. Si no está disponible,
    usa predict() y devuelve 100.0 como confianza.

    Args:
        modelo: Clasificador scikit-learn cargado con cargar_modelo().
        landmarks: Lista o array de 42 floats (x0,y0,...,x20,y20) normalizados.

    Returns:
        tuple[str, float]: (letra a-z, confianza 0.0–100.0).
            La letra es el carácter predicho en minúscula.
            La confianza es la probabilidad de Platt × 100.

    Raises:
        ValueError: Si landmarks no supera la validación de landmarks_validos().
    """
    if not landmarks_validos(landmarks):
        raise ValueError("Vector de landmarks inválido (se esperaban 42 valores).")
    vector = np.asarray(landmarks, dtype=float).reshape(1, -1)
    if hasattr(modelo, "predict_proba"):
        probas = modelo.predict_proba(vector)[0]
        idx = int(np.argmax(probas))
        return str(modelo.classes_[idx]), float(probas[idx]) * 100.0
    letra = str(modelo.predict(vector)[0])
    return letra, 100.0


# ───────────────────────── Dataset ─────────────────────────
def cargar_dataset(data_folder=DATA_FOLDER, limite_por_letra=None):
    """
    Carga el dataset de imágenes y extrae landmarks para entrenamiento o evaluación.

    Recorre 'data/<letra>/*.png' en orden alfabético, extrae los landmarks
    de cada imagen y descarta las que MediaPipe no detecta correctamente.

    Args:
        data_folder (str): Carpeta raíz del dataset. Por defecto 'data'.
        limite_por_letra (int | None): Si se especifica, toma solo las primeras
            N imágenes de cada letra (útil para pruebas rápidas).

    Returns:
        tuple[numpy.ndarray, numpy.ndarray]:
            - X: Array de forma (n_muestras, 42) con vectores de landmarks.
            - y: Array de forma (n_muestras,) con etiquetas de letra (a-z).
    """
    X, y = [], []
    for letra in LETTERS:
        carpeta = os.path.join(data_folder, letra)
        if not os.path.isdir(carpeta):
            continue
        imagenes = sorted(glob.glob(os.path.join(carpeta, "*.png")))
        if limite_por_letra:
            imagenes = imagenes[:limite_por_letra]
        for ruta in imagenes:
            vec = extraer_landmarks_de_archivo(ruta)
            if vec is not None:
                X.append(vec)
                y.append(letra)
    return np.array(X), np.array(y)


def imagenes_disponibles(data_folder=DATA_FOLDER):
    """
    Lista todas las rutas de imágenes en el dataset.

    Args:
        data_folder (str): Carpeta raíz del dataset. Por defecto 'data'.

    Returns:
        list[str]: Lista de rutas absolutas/relativas de archivos PNG, ordenadas alfabéticamente.
    """
    return sorted(glob.glob(os.path.join(data_folder, "*", "*.png")))


# ───────────────────────── Integridad del modelo ──────────────────────────────

def calcular_hash_modelo(path: str = MODELO_PATH) -> str:
    """
    Calcula el hash SHA-256 del archivo del modelo en bloques de 64 KB.

    Usar para generar un hash de referencia al entrenar el modelo y para
    verificar que el archivo no ha sido modificado antes de cargarlo.

    Args:
        path (str): Ruta al archivo del modelo (PKL). Por defecto 'modelo.pkl'.

    Returns:
        str: Hash SHA-256 hexadecimal de 64 caracteres.

    Raises:
        FileNotFoundError: Si el archivo no existe.
    """
    import hashlib
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el modelo en '{path}'.")
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def verificar_integridad_modelo(path: str = MODELO_PATH, hash_esperado: str = None) -> bool:
    """
    Verifica que el hash SHA-256 del modelo coincida con el hash de referencia.

    Protege contra la carga de modelos PKL manipulados (deserialización maliciosa).
    Si no se provee hash_esperado, intenta leer '<path>.sha256'. Si no existe
    ese archivo, devuelve True con una advertencia (comportamiento permisivo para
    compatibilidad hacia atrás).

    Args:
        path (str): Ruta al archivo del modelo.
        hash_esperado (str | None): Hash SHA-256 de 64 chars. None = leer de <path>.sha256.

    Returns:
        bool: True si el hash coincide o no hay referencia. False si hay discrepancia.
    """
    import hashlib
    import hmac as _hmac
    if not os.path.exists(path):
        return False

    hash_actual = calcular_hash_modelo(path)

    if hash_esperado is None:
        hash_file = path + ".sha256"
        if not os.path.exists(hash_file):
            return True  # sin referencia → permisivo; advertencia en la carga
        with open(hash_file, "r", encoding="utf-8") as f:
            hash_esperado = f.read().strip()

    return _hmac.compare_digest(hash_actual, hash_esperado)


def close_hands() -> None:
    """
    Libera explícitamente los recursos de las instancias de MediaPipe Hands en caché.

    Debe llamarse al final de scripts de entrenamiento o QA que usen
    extraer_landmarks() para evitar que los handles de MediaPipe queden abiertos.
    En la app web (lsp_video.py) las instancias son gestionadas por la clase Traductor.
    """
    for hands_instance in _hands_cache.values():
        try:
            hands_instance.close()
        except Exception:
            pass
    _hands_cache.clear()
