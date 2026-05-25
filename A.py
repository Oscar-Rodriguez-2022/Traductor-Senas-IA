import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  
import warnings
warnings.filterwarnings("ignore", category=UserWarning)  

import cv2
import mediapipe as mp
import numpy as np
import time
import shutil  # Librería para borrar carpetas específicas

# Inicializar MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

data_folder = "data"
letters = "abcdefghijklmnopqrstuvwxyz"
samples_per_letter = 500

if not os.path.exists(data_folder):
    os.makedirs(data_folder)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

print("--- [MEJORÍA] Capturador Interactivo con Control de Dataset ---")

for letter in letters:
    letter_folder = f"{data_folder}/{letter}"
    
    # Si la carpeta ya existe con fotos, preguntar al usuario
    if os.path.exists(letter_folder) and len(os.listdir(letter_folder)) > 0:
        print(f"\n[!] La letra '{letter.upper()}' ya tiene fotos guardadas.")
        print("1. Omitir (Pasar a la siguiente letra)")
        print("2. Repetir/Actualizar (Borrar fotos anteriores y volver a capturar)")
        opcion = input("Elige una opción (1 o 2): ").strip()
        
        if opcion == "1":
            print(f"Omitiendo letra {letter.upper()}...")
            continue
        elif opcion == "2":
            print(f"Limpiando datos viejos de la letra {letter.upper()}...")
            shutil.rmtree(letter_folder)  # Borra la carpeta completa
            os.makedirs(letter_folder)    # La recrea vacía
        else:
            print("Opción inválida. Omitiendo por seguridad...")
            continue
    else:
        if not os.path.exists(letter_folder):
            os.makedirs(letter_folder)

    # Proceso de captura normal
    print(f"\nAcomoda tu mano para la letra: {letter.upper()}")
    print("Presiona cualquier tecla en el TECLADO para iniciar la captura...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.putText(frame, f"Listo para la '{letter.upper()}'. Presiona una tecla.", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.imshow("Captura de Dataset", frame)
        if cv2.waitKey(1) != -1:
            break

    count = 0
    while count < samples_per_letter:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_limpio = frame.copy()
        h_frame, w_frame, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                landmarks_array = [[int(lm.x * w_frame), int(lm.y * h_frame)] for lm in hand_landmarks.landmark]
                x, y, w, h = cv2.boundingRect(np.array(landmarks_array))
                
                padding = 30  
                x_min = max(0, x - padding)
                y_min = max(0, y - padding)
                x_max = min(w_frame, x + w + padding)
                y_max = min(h_frame, y + h + padding)
                
                if (x_max - x_min) > 0 and (y_max - y_min) > 0:
                    hand_roi = frame_limpio[y_min:y_max, x_min:x_max]
                    if hand_roi is not None and hand_roi.size > 0:
                        img_path = f"{letter_folder}/{letter}_{count}.png"
                        cv2.imwrite(img_path, hand_roi)
                        count += 1
                        time.sleep(0.005) 
                
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                        
        cv2.putText(frame, f"Capturando {letter.upper()}: {count}/{samples_per_letter}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Captura de Dataset", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Proceso cancelado por el usuario.")
            cap.release()
            cv2.destroyAllWindows()
            exit()

cap.release()
cv2.destroyAllWindows()
print("\n¡Proceso de recolección finalizado!")