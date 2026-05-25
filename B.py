import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  
import warnings
warnings.filterwarnings("ignore", category=UserWarning)  

import cv2
import mediapipe as mp
import numpy as np
from sklearn import svm
from sklearn.model_selection import train_test_split

# Inicializar MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1)

# Cargar imágenes de entrenamiento
data_folder = "data"  
letters = "abcdefghijklmnopqrstuvwxyz"
X, y_labels = [], []

print("--- [MEJORÍA] Iniciando extracción de puntos clave de MediaPipe ---")

for letter in letters:
    folder_path = f"{data_folder}/{letter}"
    if os.path.exists(folder_path):
        print(f"Procesando esqueleto de la letra: '{letter.upper()}'...")
        for i in range(500):
            img_path = f"{folder_path}/{letter}_{i}.png"
            img = cv2.imread(img_path)
            if img is not None:
                # Convertir a RGB para MediaPipe
                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_img)
                
                # Extraer solo las coordenadas si detecta la mano en la foto
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        landmarks = []
                        for lm in hand_landmarks.landmark:
                            landmarks.append(lm.x)
                            landmarks.append(lm.y)
                        X.append(landmarks)
                        y_labels.append(letter)

if len(X) == 0:
    print("¡Error! No se pudieron extraer puntos de las imágenes. Asegúrate de que la carpeta 'data' tenga fotos claras.")
    exit()

X = np.array(X)
y_labels = np.array(y_labels)

print(f"\n✅ Extracción lista. Datos útiles: {len(X)} muestras.")
print("⚡ Entrenando el modelo SVM ultra-optimizado...")

# Entrenar el modelo con los 42 puntos clave (¡Esto será instantáneo!)
X_train, X_test, y_train, y_test = train_test_split(X, y_labels, test_size=0.2, random_state=42)
clf = svm.SVC(kernel='linear', C=1)
clf.fit(X_train, y_train)

print("¡Modelo entrenado en TIEMPO RÉCORD! Abriendo cámara en vivo...")

# Cambiar a modo video para tiempo real
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  
cv2.namedWindow("Traductor de Lengua de Senas Optimizado", cv2.WINDOW_AUTOSIZE)
mp_drawing = mp.solutions.drawing_utils

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Extraer puntos clave de la cámara
            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.append(lm.x)
                landmarks.append(lm.y)
            
            if len(landmarks) == 42:
                try:
                    # Predicción instantánea basada en geometría, no en píxeles
                    predicted_letter = clf.predict([landmarks])[0]
                    cv2.putText(frame, f'Letra: {predicted_letter.upper()}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3, cv2.LINE_AA)
                except:
                    pass

    cv2.imshow("Traductor de Lengua de Senas Optimizado", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()