"""
=== PARA EL ENCARGADO DEL DATASET ===

Junta los CSV de TODOS los compañeros y entrena el modelo final.

Pasos:
1. Crea (si no existe) la carpeta 'landmarks_csv'.
2. Copia ahí TODOS los archivos 'landmarks_*.csv' que te enviaron tus compañeros
   (y el tuyo propio, generado con extraer_landmarks.py).
3. Ejecuta este script. Combina todo y genera 'modelo.pkl'.
4. Sube el modelo:  git add modelo.pkl && git commit -m "modelo actualizado" && git push

Uso:  python entrenar_desde_csv.py
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import warnings
warnings.filterwarnings("ignore")

import glob
import csv
import numpy as np
import joblib
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

carpeta = "landmarks_csv"
if not os.path.isdir(carpeta):
    os.makedirs(carpeta)
    print(f"Se creó la carpeta '{carpeta}'.")
    print("Copia ahí los archivos landmarks_*.csv de tus compañeros y vuelve a ejecutar.")
    raise SystemExit(0)

archivos = glob.glob(os.path.join(carpeta, "*.csv"))
if not archivos:
    print(f"No hay ningún CSV en la carpeta '{carpeta}'.")
    print("Copia ahí los archivos landmarks_*.csv y vuelve a ejecutar.")
    raise SystemExit(1)

X, y = [], []
print("--- Combinando los CSV del equipo ---")
for ruta in archivos:
    n = 0
    with open(ruta, newline="") as f:
        lector = csv.reader(f)
        next(lector, None)  # saltar encabezado
        for fila in lector:
            if len(fila) < 43:
                continue
            try:
                feats = [float(v) for v in fila[:42]]
            except ValueError:
                continue
            X.append(feats)
            y.append(fila[42])
            n += 1
    print(f"  {os.path.basename(ruta)}: {n} muestras")

X = np.array(X)
y = np.array(y)
clases = sorted(set(y))

if len(clases) < 2:
    print("\nSe necesitan al menos 2 letras distintas para entrenar.")
    raise SystemExit(1)

print(f"\nTotal combinado: {len(X)} muestras | Letras: {', '.join(c.upper() for c in clases)}")
print("Entrenando el modelo SVM con los datos de TODOS...")

clf = svm.SVC(kernel="rbf", C=10, gamma="scale", probability=True)
puede_dividir = all(list(y).count(c) >= 5 for c in clases)
if puede_dividir:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    print(f"Accuracy en datos de prueba: {accuracy_score(y_test, y_pred) * 100:.1f}%")
    print("\nReporte por letra:")
    print(classification_report(
        y_test, y_pred,
        labels=clases,
        target_names=[c.upper() for c in clases],
        zero_division=0,
    ))
else:
    clf.fit(X, y)
    print("Dataset pequeño: se entrenó con todas las muestras.")

joblib.dump(clf, "modelo.pkl")
print("\n[OK] 'modelo.pkl' actualizado con los datos de todo el equipo.")
print("-->  Ahora subelo: git add modelo.pkl -> git commit -> git push")
