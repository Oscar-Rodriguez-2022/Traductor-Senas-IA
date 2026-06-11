import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import platform
import cv2
import joblib
import mediapipe as mp
import numpy as np
from sklearn import svm
from sklearn.model_selection import train_test_split

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

data_folder = "data"
letters = "abcdefghijklmnopqrstuvwxyz"
X, y_labels = [], []

print("--- [B.py] Extracción de landmarks y entrenamiento SVM ---")

hands_static = mp_hands.Hands(static_image_mode=True, max_num_hands=1, min_detection_confidence=0.5)

for letter in letters:
    folder_path = f"{data_folder}/{letter}"
    if not os.path.exists(folder_path):
        continue

    img_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".png")]
    if not img_files:
        continue

    print(f"Procesando letra '{letter.upper()}' — {len(img_files)} imágenes...")
    for fname in img_files:
        img = cv2.imread(os.path.join(folder_path, fname))
        if img is None:
            continue
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands_static.process(rgb_img)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                landmarks = []
                for lm in hand_landmarks.landmark:
                    landmarks.append(lm.x)
                    landmarks.append(lm.y)
                X.append(landmarks)
                y_labels.append(letter)

hands_static.close()

if len(X) == 0:
    print("¡Error! No se pudieron extraer puntos de las imágenes.")
    print("Asegúrate de que la carpeta 'data' tenga fotos capturadas con A.py.")
    raise SystemExit(1)

X = np.array(X)
y_labels = np.array(y_labels)

print(f"\n[OK] Extraccion lista: {len(X)} muestras de {len(set(y_labels))} letras.")
print("Entrenando modelo SVM con probabilidad de confianza...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y_labels, test_size=0.2, random_state=42, stratify=y_labels
)

clf = svm.SVC(kernel="rbf", C=10, gamma="scale", probability=True)
clf.fit(X_train, y_train)

accuracy = clf.score(X_test, y_test)
print(f"[OK] Accuracy en validacion: {accuracy * 100:.1f}%")

joblib.dump(clf, "modelo.pkl")
print("[OK] Modelo guardado en modelo.pkl")

print("\nAbriendo cámara para traducción en vivo (presiona Q para salir)...")

hands_video = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    model_complexity=0,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5,
)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) if platform.system() == "Windows" else cv2.VideoCapture(0)
cv2.namedWindow("Traductor LSP", cv2.WINDOW_AUTOSIZE)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands_video.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.append(lm.x)
                landmarks.append(lm.y)

            if len(landmarks) == 42:
                try:
                    proba = clf.predict_proba([landmarks])[0]
                    idx = int(np.argmax(proba))
                    letra = clf.classes_[idx]
                    confianza = proba[idx]
                    color = (0, 255, 0) if confianza >= 0.6 else (0, 165, 255)
                    cv2.putText(frame, f"{letra.upper()}  {confianza * 100:.0f}%",
                                (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, color, 3, cv2.LINE_AA)
                except Exception:
                    pass

    cv2.imshow("Traductor LSP", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
hands_video.close()
cv2.destroyAllWindows()
