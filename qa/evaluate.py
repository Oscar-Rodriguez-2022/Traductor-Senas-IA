"""
Fase 10 — Métricas de precisión del modelo sobre el dataset real.
Accuracy, Precision, Recall y F1 (macro y por clase).

Uso:  python qa/evaluate.py
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import lsp_core
from qa._utils import guardar_csv, guardar_json, banner


def main():
    banner("FASE 10 — PRECISIÓN DEL MODELO (Accuracy / Precision / Recall / F1)")
    from sklearn.metrics import (
        accuracy_score, precision_score, recall_score, f1_score, classification_report,
    )

    print("Extrayendo landmarks del dataset (puede tardar)...")
    X, y = lsp_core.cargar_dataset()
    if len(X) == 0:
        print("Dataset vacío. Captura imágenes primero.")
        return

    modelo = lsp_core.cargar_modelo()
    y_pred = modelo.predict(X)

    acc = accuracy_score(y, y_pred)
    prec = precision_score(y, y_pred, average="macro", zero_division=0)
    rec = recall_score(y, y_pred, average="macro", zero_division=0)
    f1 = f1_score(y, y_pred, average="macro", zero_division=0)

    resumen = {
        "muestras": int(len(X)),
        "clases": int(len(set(y))),
        "accuracy": round(acc, 4),
        "precision_macro": round(prec, 4),
        "recall_macro": round(rec, 4),
        "f1_macro": round(f1, 4),
    }
    print(f"\n  Muestras  : {resumen['muestras']}")
    print(f"  Accuracy  : {acc*100:.2f}%")
    print(f"  Precision : {prec*100:.2f}%")
    print(f"  Recall    : {rec*100:.2f}%")
    print(f"  F1-Score  : {f1*100:.2f}%")

    # Tabla por clase
    rep = classification_report(y, y_pred, zero_division=0, output_dict=True)
    filas = []
    for clase, m in rep.items():
        if clase in ("accuracy", "macro avg", "weighted avg"):
            continue
        filas.append({
            "letra": clase.upper(),
            "precision": round(m["precision"], 3),
            "recall": round(m["recall"], 3),
            "f1": round(m["f1-score"], 3),
            "muestras": int(m["support"]),
        })

    guardar_csv("metricas_por_clase.csv", filas)
    guardar_json("metricas.json", resumen)
    guardar_csv("metricas_resumen.csv", [resumen])
    print("\n  NOTA: medido sobre el MISMO dataset de entrenamiento (optimista).")
    print("      Para evaluacion rigurosa, ver qa/cross_validation.py")
    print("[OK] Reportes guardados en reportes/")


if __name__ == "__main__":
    main()
