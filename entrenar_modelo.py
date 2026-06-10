"""
Entrena el modelo SVM UNA SOLA VEZ a partir de las fotos de la carpeta 'data'
y lo guarda en 'modelo.pkl'. La web app (app.py) solo CARGA ese archivo y predice;
nunca vuelve a entrenar. Esto es lo que el profesor llama "integrar el modelo".

Uso:  python entrenar_modelo.py
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import warnings
warnings.filterwarnings("ignore")

import glob
import cv2
import numpy as np
import joblib
import mediapipe as mp
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1)

data_folder = "data"
letters = "abcdefghijklmnopqrstuvwxyz"
X, y_labels = [], []

print("--- Extrayendo puntos clave (landmarks) de las fotos del dataset ---")

for letter in letters:
    folder_path = os.path.join(data_folder, letter)
    if not os.path.isdir(folder_path):
        continue
    # Leer TODAS las fotos de la letra (no solo 500), sin importar la numeración
    imagenes = glob.glob(os.path.join(folder_path, "*.png"))
    if not imagenes:
        continue
    usadas = 0
    for img_path in imagenes:
        img = cv2.imread(img_path)
        if img is None:
            continue
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_img)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                landmarks = []
                for lm in hand_landmarks.landmark:
                    landmarks.append(lm.x)
                    landmarks.append(lm.y)
                X.append(landmarks)
                y_labels.append(letter)
                usadas += 1
    print(f"  Letra '{letter.upper()}': {usadas} muestras útiles de {len(imagenes)} fotos.")

if len(X) == 0:
    print("\n¡ERROR! No se extrajeron puntos de ninguna imagen.")
    print("Captura primero el dataset con A.py (1_CAPTURAR_dataset.bat).")
    raise SystemExit(1)

X = np.array(X)
y_labels = np.array(y_labels)
clases = sorted(set(y_labels))

if len(clases) < 2:
    print(f"\n¡ERROR! Solo hay datos de la letra '{clases[0].upper()}'.")
    print("Se necesitan al menos 2 letras distintas para entrenar. Captura más con A.py.")
    raise SystemExit(1)

print(f"\nTotal de muestras: {len(X)} | Letras disponibles: {', '.join(c.upper() for c in clases)}")
print("Entrenando el modelo SVM...")

clf = svm.SVC(kernel='linear', C=1)

# Si hay datos suficientes, separamos en entrenamiento/prueba para medir precisión.
# Si el dataset es muy pequeño, entrenamos con todo.
puede_dividir = all(list(y_labels).count(c) >= 5 for c in clases)
if puede_dividir:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_labels, test_size=0.2, random_state=42, stratify=y_labels
    )
    clf.fit(X_train, y_train)
    precision = accuracy_score(y_test, clf.predict(X_test))
    print(f"Precisión en datos de prueba: {precision * 100:.1f}%")
else:
    clf.fit(X, y_labels)
    print("Dataset pequeño: se entrenó con todas las muestras (sin prueba aparte).")

joblib.dump(clf, "modelo.pkl")
print("\n✅ Modelo guardado en 'modelo.pkl'. Ya puedes desplegar la web (app.py).")
