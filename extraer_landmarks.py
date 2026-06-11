"""
=== PARA LOS COMPAÑEROS DEL EQUIPO ===

Después de capturar tus señas con A.py (1_CAPTURAR_dataset.bat), ejecuta este
script. Lee tus fotos de la carpeta 'data', extrae los 42 puntos de cada mano y
genera un archivo CSV pequeñito (unos KB) con todo.

Luego envías SOLO ese archivo CSV al encargado del dataset (por WhatsApp, Drive,
correo...). No hace falta mandar las fotos: el modelo solo necesita los números.

Uso:  python extraer_landmarks.py
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import warnings
warnings.filterwarnings("ignore")

import glob
import csv
import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1, model_complexity=0)

data_folder = "data"
letters = "abcdefghijklmnopqrstuvwxyz"

nombre = input("Escribe tu nombre o apodo SIN espacios (para identificar tu archivo): ").strip()
if not nombre:
    nombre = "anonimo"
nombre = "".join(c for c in nombre if c.isalnum() or c in "-_")
salida = f"landmarks_{nombre}.csv"

filas = []
print("\nExtrayendo puntos clave de tus fotos...")
for letter in letters:
    folder = os.path.join(data_folder, letter)
    if not os.path.isdir(folder):
        continue
    imagenes = glob.glob(os.path.join(folder, "*.png"))
    usadas = 0
    for ruta in imagenes:
        img = cv2.imread(ruta)
        if img is None:
            continue
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                fila = []
                for lm in hand_landmarks.landmark:
                    fila.append(lm.x)
                    fila.append(lm.y)
                if len(fila) == 42:
                    fila.append(letter)
                    filas.append(fila)
                    usadas += 1
    if usadas:
        print(f"  Letra {letter.upper()}: {usadas} muestras")

hands.close()

if not filas:
    print("\n¡No se extrajo nada! ¿Seguro capturaste fotos con A.py primero?")
    raise SystemExit(1)

encabezado = [f"p{i}_{eje}" for i in range(21) for eje in ("x", "y")] + ["letra"]
with open(salida, "w", newline="") as f:
    escritor = csv.writer(f)
    escritor.writerow(encabezado)
    escritor.writerows(filas)
print(f"\n[OK] Listo: {len(filas)} muestras guardadas en '{salida}'.")
print("-->  Envia SOLO ese archivo CSV al encargado del dataset.")
