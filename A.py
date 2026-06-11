import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import platform
import cv2
import mediapipe as mp
import numpy as np
import time
import shutil

# Inicializar MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

data_folder = "data"
letters = "abcdefghijklmnopqrstuvwxyz"
samples_per_letter = 500  # Fotos NUEVAS que se capturan por persona en cada sesión

if not os.path.exists(data_folder):
    os.makedirs(data_folder)


def contar_fotos(folder):
    """Devuelve la lista de archivos .png existentes en la carpeta."""
    if not os.path.exists(folder):
        return []
    return [f for f in os.listdir(folder) if f.lower().endswith(".png")]


def siguiente_indice(folder, letter):
    """
    Calcula el siguiente número de archivo para NO sobrescribir fotos
    de otras personas. Si ya existen 'letra_0' ... 'letra_499',
    la próxima foto será 'letra_500', y así sucesivamente.
    """
    indices = []
    for f in contar_fotos(folder):
        nombre = os.path.splitext(f)[0]  # quita ".png"
        partes = nombre.split("_")
        if len(partes) == 2 and partes[0] == letter and partes[1].isdigit():
            indices.append(int(partes[1]))
    return max(indices) + 1 if indices else 0


cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) if platform.system() == "Windows" else cv2.VideoCapture(0)

print("--- [MEJORÍA] Capturador Interactivo Colaborativo de Dataset ---")
print("Varias personas pueden AUMENTAR el dataset sin borrar el trabajo de los demás.\n")

for letter in letters:
    letter_folder = f"{data_folder}/{letter}"

    if not os.path.exists(letter_folder):
        os.makedirs(letter_folder)

    fotos_existentes = contar_fotos(letter_folder)
    start_index = 0  # por defecto, empieza en 0

    # Si la carpeta ya tiene fotos, dar 3 opciones
    if len(fotos_existentes) > 0:
        print(f"\n[!] La letra '{letter.upper()}' ya tiene {len(fotos_existentes)} fotos guardadas.")
        print("  1. Pasar a la siguiente letra (no tocar nada)")
        print("  2. Reemplazar (borrar TODAS las fotos y volver a capturar desde cero)")
        print("  3. Aumentar (agregar 500 fotos nuevas SUMANDO a las actuales)")
        opcion = input("Elige una opción (1, 2 o 3): ").strip()

        if opcion == "1":
            print(f"Pasando a la siguiente letra...")
            continue
        elif opcion == "2":
            print(f"Limpiando datos viejos de la letra {letter.upper()}...")
            shutil.rmtree(letter_folder)
            os.makedirs(letter_folder)
            start_index = 0
        elif opcion == "3":
            start_index = siguiente_indice(letter_folder, letter)
            print(f"Modo AUMENTAR: las fotos nuevas empezarán en el número {start_index}.")
        else:
            print("Opción inválida. Pasando a la siguiente letra por seguridad...")
            continue

    # ---- Sesión de captura ----
    # Se permite repetir la sesión completa de esta letra si el usuario no quedó conforme
    while True:
        print(f"\nAcomoda tu mano para la letra: {letter.upper()}")
        print("Presiona cualquier tecla en el TECLADO (sobre la ventana de la cámara) para iniciar...")

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.putText(frame, f"Listo para la '{letter.upper()}'. Presiona una tecla.", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            cv2.imshow("Captura de Dataset", frame)
            if cv2.waitKey(1) != -1:
                break

        target = start_index + samples_per_letter  # número final al que queremos llegar
        count = start_index                          # empezamos donde corresponde
        nuevos_guardados = []                        # rutas de las fotos de ESTA sesión

        while count < target:
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
                            nuevos_guardados.append(img_path)
                            count += 1
                            time.sleep(0.005)

                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

            capturadas = count - start_index
            total_letra = len(contar_fotos(letter_folder))
            cv2.putText(frame, f"{letter.upper()}: {capturadas}/{samples_per_letter} nuevas (total: {total_letra})", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.imshow("Captura de Dataset", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Proceso cancelado por el usuario.")
                cap.release()
                cv2.destroyAllWindows()
                exit()

        # ---- Fin de la sesión: ¿guardar o repetir? ----
        total_actual = len(contar_fotos(letter_folder))
        print(f"\n¡Captura de la letra {letter.upper()} terminada! Se guardaron {len(nuevos_guardados)} fotos nuevas (total ahora: {total_actual}).")
        print("  G. Guardar y pasar a la siguiente letra")
        print("  R. Repetir (borrar SOLO las fotos de esta sesión y volver a capturarlas)")
        decision = input("Elige una opción (G o R): ").strip().upper()

        if decision == "R":
            print("Borrando las fotos de esta sesión y repitiendo...")
            for ruta in nuevos_guardados:
                if os.path.exists(ruta):
                    os.remove(ruta)
            # 'start_index' se mantiene, así repetimos exactamente este tramo
            continue
        else:
            print(f"Fotos de la letra {letter.upper()} guardadas correctamente.")
            break

cap.release()
cv2.destroyAllWindows()
print("\n¡Proceso de recolección finalizado!")
