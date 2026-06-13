"""
Fase 11 — Matriz de confusión + heatmap PNG.

Uso:  python qa/confusion_matrix.py
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
import lsp_core
from qa._utils import REPORTES, banner


def main():
    banner("FASE 11 — MATRIZ DE CONFUSIÓN")
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.metrics import confusion_matrix

    print("Extrayendo landmarks del dataset...")
    X, y = lsp_core.cargar_dataset()
    if len(X) == 0:
        print("Dataset vacío.")
        return

    modelo = lsp_core.cargar_modelo()
    y_pred = modelo.predict(X)
    clases = sorted(set(y) | set(y_pred))
    cm = confusion_matrix(y, y_pred, labels=clases)

    fig, ax = plt.subplots(figsize=(max(6, len(clases) * 0.6), max(5, len(clases) * 0.6)))
    im = ax.imshow(cm, cmap="Reds")
    ax.set_xticks(range(len(clases)))
    ax.set_yticks(range(len(clases)))
    ax.set_xticklabels([c.upper() for c in clases])
    ax.set_yticklabels([c.upper() for c in clases])
    ax.set_xlabel("Predicción")
    ax.set_ylabel("Real")
    ax.set_title("Matriz de Confusión — Traductor LSP")
    umbral = cm.max() / 2 if cm.max() else 0
    for i in range(len(clases)):
        for j in range(len(clases)):
            if cm[i, j]:
                ax.text(j, i, cm[i, j], ha="center", va="center",
                        color="white" if cm[i, j] > umbral else "black", fontsize=8)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    ruta_png = os.path.join(REPORTES, "matriz_confusion.png")
    fig.savefig(ruta_png, dpi=140)

    # También CSV
    ruta_csv = os.path.join(REPORTES, "matriz_confusion.csv")
    np.savetxt(ruta_csv, cm, fmt="%d", delimiter=",",
               header=",".join(c.upper() for c in clases), comments="")

    print(f"\n[OK] Heatmap: {ruta_png}")
    print(f"[OK] CSV    : {ruta_csv}")


if __name__ == "__main__":
    main()
