"""
augmentar_dataset.py — Entrena el modelo SVM con data augmentation a nivel de landmarks.

Problema que resuelve:
  El dataset suele estar desbalanceado (pocas fotos por letra) y MediaPipe descarta
  muchas imágenes de baja calidad. Este script extrae los landmarks válidos que hay,
  los multiplica ~14x con transformaciones geométricas realistas, y entrena el SVM
  con el dataset resultante.

Por qué augmentar landmarks y no imágenes:
  El SVM aprende de vectores de 42 coordenadas (x,y de los 21 puntos de la mano),
  no de píxeles. Augmentar directamente el vector garantiza que cada muestra
  aumentada es válida (MediaPipe no puede fallar en ella) y es instantáneo.

Transformaciones aplicadas (todas preservan la forma de la mano):
  - Rotación: ±5°, ±10°, ±15°  (6 versiones)
  - Escala:   ×0.88, ×0.94, ×1.06, ×1.12  (4 versiones)
  - Ruido gaussiano: σ=0.006, 3 seeds distintas  (3 versiones)
  - Combinadas rotación+ruido: ±8° + σ=0.004  (2 versiones)
  Total por muestra original: 15 versiones → dataset ×16

Uso:
  py -3.12 augmentar_dataset.py
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import warnings
warnings.filterwarnings("ignore")

import glob
import math
import numpy as np
import cv2
import joblib
import mediapipe as mp
from collections import Counter
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report


# ─────────────────────────── Funciones de augmentation ────────────────────────

def _reshape(landmarks):
    return np.array(landmarks, dtype=np.float64).reshape(21, 2)


def rotar(landmarks, grados):
    """Rota los 21 puntos alrededor del centroide de la mano."""
    lm = _reshape(landmarks)
    cx, cy = lm.mean(axis=0)
    rad = math.radians(grados)
    cos_t, sin_t = math.cos(rad), math.sin(rad)
    d = lm - [cx, cy]
    rot = np.column_stack([
        d[:, 0] * cos_t - d[:, 1] * sin_t,
        d[:, 0] * sin_t + d[:, 1] * cos_t,
    ])
    return (rot + [cx, cy]).flatten().tolist()


def escalar(landmarks, factor):
    """Escala los 21 puntos alrededor del centroide."""
    lm = _reshape(landmarks)
    cx, cy = lm.mean(axis=0)
    return ((lm - [cx, cy]) * factor + [cx, cy]).flatten().tolist()


def ruido(landmarks, sigma, seed=None):
    """Agrega ruido gaussiano pequeño a cada coordenada."""
    rng = np.random.default_rng(seed)
    lm = np.array(landmarks, dtype=np.float64)
    return (lm + rng.normal(0, sigma, lm.shape)).tolist()


def augmentar(landmarks):
    """Genera las 15 versiones aumentadas de un vector de landmarks."""
    versiones = []
    for g in (-15, -10, -5, 5, 10, 15):
        versiones.append(rotar(landmarks, g))
    for f in (0.88, 0.94, 1.06, 1.12):
        versiones.append(escalar(landmarks, f))
    for seed in (0, 1, 2):
        versiones.append(ruido(landmarks, sigma=0.006, seed=seed))
    versiones.append(rotar(ruido(landmarks, 0.004, seed=7),  8))
    versiones.append(rotar(ruido(landmarks, 0.004, seed=13), -8))
    return versiones   # 15 versiones


# ─────────────────────────── Extracción de landmarks ──────────────────────────

def extraer_landmarks(data_folder="data"):
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=True,
        max_num_hands=1,
        model_complexity=0,
        min_detection_confidence=0.5,
    )

    X, y = [], []
    letras_ok = []

    for letter in "abcdefghijklmnopqrstuvwxyz":
        folder = os.path.join(data_folder, letter)
        if not os.path.isdir(folder):
            continue
        imagenes = glob.glob(os.path.join(folder, "*.png"))
        if not imagenes:
            continue

        utiles = 0
        for img_path in imagenes:
            img = cv2.imread(img_path)
            if img is None:
                continue
            results = hands.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            if results.multi_hand_landmarks:
                for hl in results.multi_hand_landmarks:
                    lm = []
                    for pt in hl.landmark:
                        lm.append(pt.x)
                        lm.append(pt.y)
                    X.append(lm)
                    y.append(letter)
                    utiles += 1

        estado = f"{utiles:>3} utiles / {len(imagenes):>3} fotos"
        advertencia = " <-- SIN MUESTRAS, captura con A.py" if utiles == 0 else ""
        print(f"  {letter.upper()}: {estado}{advertencia}")
        if utiles > 0:
            letras_ok.append(letter)

    hands.close()
    return X, y, letras_ok


# ─────────────────────────── Main ─────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  augmentar_dataset.py — Data Augmentation + Entrenamiento")
    print("=" * 60)
    print()

    # 1. Extracción
    print("[1/4] Extrayendo landmarks del dataset...")
    X_orig, y_orig, letras = extraer_landmarks()

    if not X_orig:
        print("\nERROR: No se extrajeron landmarks.")
        print("Captura datos con A.py (1_CAPTURAR_dataset.bat) antes de continuar.")
        raise SystemExit(1)

    conteo_orig = Counter(y_orig)
    print(f"\nDataset original: {len(X_orig)} muestras validas de {len(letras)} letras")

    letras_sin_datos = [
        c.upper() for c in "abcdefghijklmnopqrstuvwxyz"
        if os.path.isdir(os.path.join("data", c)) and conteo_orig.get(c, 0) == 0
    ]
    if letras_sin_datos:
        print(f"AVISO: sin muestras utiles: {', '.join(letras_sin_datos)}")
        print("       Estas letras no podran reconocerse. Captura mas fotos con A.py.")

    # 2. Augmentation
    print(f"\n[2/4] Aplicando data augmentation (x16 por muestra)...")
    X_all = list(X_orig)
    y_all = list(y_orig)

    for lm, label in zip(X_orig, y_orig):
        aumentados = augmentar(lm)
        X_all.extend(aumentados)
        y_all.extend([label] * len(aumentados))

    X_all = np.array(X_all)
    y_all = np.array(y_all)
    conteo_final = Counter(y_all)

    print(f"Dataset aumentado: {len(X_all)} muestras ({len(X_orig)} originales + {len(X_all)-len(X_orig)} sinteticas)")
    print("\nMuestras por letra (orig -> aumentado):")
    for c in sorted(set(y_all)):
        orig = conteo_orig.get(c, 0)
        total = conteo_final[c]
        print(f"  {c.upper():>2}: {orig:>4} -> {total:>5}")

    # 3. Entrenamiento
    print("\n[3/4] Entrenando SVM (kernel RBF, C=10)...")
    clases = sorted(set(y_all))
    puede_dividir = all(conteo_final[c] >= 5 for c in clases)

    if puede_dividir:
        X_train, X_test, y_train, y_test = train_test_split(
            X_all, y_all, test_size=0.2, random_state=42, stratify=y_all
        )
        clf = svm.SVC(kernel="rbf", C=10, gamma="scale", probability=True)
        clf.fit(X_train, y_train)

        y_pred = clf.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        print(f"\nAccuracy en validacion: {acc * 100:.1f}%")
        print("\nReporte por letra:")
        print(classification_report(
            y_test, y_pred,
            labels=clases,
            target_names=[c.upper() for c in clases],
            zero_division=0,
        ))
    else:
        clf = svm.SVC(kernel="rbf", C=10, gamma="scale", probability=True)
        clf.fit(X_all, y_all)
        print("Dataset pequeño: entrenado con todas las muestras (sin split de prueba).")

    # 4. Guardar
    print("[4/4] Guardando modelo.pkl...")
    joblib.dump(clf, "modelo.pkl")

    n_clases = len(clf.classes_)
    print(f"\n[OK] modelo.pkl guardado.")
    print(f"     Letras reconocibles: {n_clases} ({', '.join(c.upper() for c in clf.classes_)})")
    if letras_sin_datos:
        print(f"     Letras NO reconocibles (sin datos): {', '.join(letras_sin_datos)}")
    print()
    print("Siguiente paso: sube modelo.pkl a GitHub y despliega en HuggingFace.")
    print("  git add modelo.pkl && git commit -m 'Modelo con augmentation' && git push")


if __name__ == "__main__":
    main()
