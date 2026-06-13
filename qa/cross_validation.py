"""
Fase 12 — Validación cruzada K-Fold (k=5 y k=10).
Reentrena sobre folds para una estimación honesta (no optimista).
Reporta media y desviación estándar del accuracy.

Uso:  python qa/cross_validation.py
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
import lsp_core
from qa._utils import guardar_csv, banner


def main():
    banner("FASE 12 — VALIDACIÓN CRUZADA K-FOLD")
    import numpy as np
    from collections import Counter
    from sklearn import svm
    from sklearn.model_selection import cross_val_score, StratifiedKFold

    print("Extrayendo landmarks del dataset...")
    X, y = lsp_core.cargar_dataset()
    if len(X) == 0:
        print("Dataset vacío.")
        return

    conteo = Counter(y)
    min_por_clase = min(conteo.values())
    print(f"  Muestras: {len(X)} | Clases: {len(conteo)} | Mínimo por clase: {min_por_clase}")

    filas = []
    for k in (5, 10):
        if min_por_clase < k:
            print(f"\n  k={k}: OMITIDO (alguna clase tiene < {k} muestras). "
                  f"Captura más dataset para habilitarlo.")
            filas.append({"k": k, "accuracy_media": "N/A",
                          "desv_std": "N/A", "nota": f"clase minima={min_por_clase}"})
            continue
        clf = svm.SVC(kernel="rbf", C=10, gamma="scale")
        cv = StratifiedKFold(n_splits=k, shuffle=True, random_state=42)
        scores = cross_val_score(clf, X, y, cv=cv, scoring="accuracy")
        media, std = float(np.mean(scores)), float(np.std(scores))
        print(f"\n  k={k}:  accuracy = {media*100:.2f}%  ±{std*100:.2f}%")
        filas.append({
            "k": k,
            "accuracy_media": round(media, 4),
            "desv_std": round(std, 4),
            "nota": "ok",
        })

    ruta = guardar_csv("cross_validation.csv", filas)
    print(f"\n[OK] Reporte guardado en {ruta}")


if __name__ == "__main__":
    main()
