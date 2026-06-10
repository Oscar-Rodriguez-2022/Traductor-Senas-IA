"""
lsp_core.py — Núcleo reutilizable y TESTEABLE del Traductor LSP.

Centraliza la lógica que antes estaba incrustada en A.py / app.py / B.py:
carga del modelo, extracción de landmarks, validación y predicción.
Tanto la app como la suite de pruebas (tests/) y los scripts de QA (qa/)
importan desde aquí, evitando duplicar código y permitiendo medir calidad.
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
    """Carga el modelo SVM entrenado. Lanza FileNotFoundError si no existe."""
    import joblib
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el modelo en '{path}'.")
    return joblib.load(path)


# ───────────────────────── MediaPipe ─────────────────────────
def _get_hands(static_image_mode=True):
    """Devuelve (y cachea) una instancia de MediaPipe Hands."""
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
    Recibe una imagen BGR (numpy array) y devuelve una lista de 42 floats
    (x0,y0,...,x20,y20) normalizados en [0,1], o None si no detecta mano.
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
    """Lee una imagen del disco y extrae sus landmarks (o None)."""
    import cv2
    img = cv2.imread(path)
    return extraer_landmarks(img)


# ───────────────────────── Validación ─────────────────────────
def landmarks_validos(landmarks):
    """True si 'landmarks' es un vector de 42 números finitos en rango razonable."""
    if landmarks is None:
        return False
    arr = np.asarray(landmarks, dtype=float).ravel()
    if arr.shape[0] != NUM_FEATURES:
        return False
    if not np.all(np.isfinite(arr)):
        return False
    # MediaPipe normaliza en [0,1], pero damos margen por manos en el borde.
    return bool(np.all(arr >= -0.5) and np.all(arr <= 1.5))


# ───────────────────────── Predicción ─────────────────────────
def predecir(modelo, landmarks):
    """
    Devuelve (letra, confianza_0a100). Lanza ValueError si el vector es inválido.
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
    Recorre 'data/<letra>/*.png', extrae landmarks y devuelve (X, y) como arrays.
    'limite_por_letra' permite muestrear para pruebas rápidas.
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
    """Lista de rutas de todas las imágenes del dataset."""
    return sorted(glob.glob(os.path.join(data_folder, "*", "*.png")))
