"""
Fase 13 — Test de robustez por aumentación de imágenes.
No requiere capturar nuevas fotos: transforma las del dataset para simular
condiciones adversas y mide cuántas mantienen detección de mano.

Condiciones: poca luz, luz intensa, fondo con ruido, mano inclinada,
mano parcial, distancia corta (zoom), distancia larga (reducción).

Uso:  python qa/robustez.py
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import lsp_core
from qa._utils import guardar_csv, banner

MAX_IMG = 40  # imágenes a probar por condición


def poca_luz(img, cv2):
    return cv2.convertScaleAbs(img, alpha=0.35, beta=0)


def luz_intensa(img, cv2):
    return cv2.convertScaleAbs(img, alpha=1.6, beta=70)


def fondo_complejo(img, cv2, np):
    ruido = np.random.randint(0, 80, img.shape, dtype=np.uint8)
    return cv2.add(img, ruido)


def mano_inclinada(img, cv2):
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), 35, 1.0)
    return cv2.warpAffine(img, M, (w, h))


def mano_parcial(img, cv2):
    h, w = img.shape[:2]
    recorte = img.copy()
    recorte[:, : w // 3] = 0  # tapa un tercio
    return recorte


def distancia_corta(img, cv2):
    h, w = img.shape[:2]
    zoom = img[h // 6: h - h // 6, w // 6: w - w // 6]
    return cv2.resize(zoom, (w, h))


def distancia_larga(img, cv2):
    h, w = img.shape[:2]
    pequena = cv2.resize(img, (w // 2, h // 2))
    return cv2.copyMakeBorder(pequena, h // 4, h // 4, w // 4, w // 4,
                              cv2.BORDER_CONSTANT, value=(0, 0, 0))


def main():
    banner("FASE 13 — ROBUSTEZ ANTE CONDICIONES ADVERSAS")
    import cv2
    import numpy as np

    rutas = lsp_core.imagenes_disponibles()
    base = []
    for r in rutas:
        img = cv2.imread(r)
        if img is not None and lsp_core.extraer_landmarks(img) is not None:
            base.append(img)
        if len(base) >= MAX_IMG:
            break
    if not base:
        print("No hay imágenes con mano detectable.")
        return

    print(f"Probando {len(base)} imágenes (todas con mano detectable en condición normal)...\n")

    condiciones = {
        "Normal (referencia)": lambda im: im,
        "Poca luz": lambda im: poca_luz(im, cv2),
        "Luz intensa": lambda im: luz_intensa(im, cv2),
        "Fondo complejo (ruido)": lambda im: fondo_complejo(im, cv2, np),
        "Mano inclinada (35 grados)": lambda im: mano_inclinada(im, cv2),
        "Mano parcial": lambda im: mano_parcial(im, cv2),
        "Distancia corta (zoom)": lambda im: distancia_corta(im, cv2),
        "Distancia larga (lejos)": lambda im: distancia_larga(im, cv2),
    }

    filas = []
    print(f"{'Condición':<30}{'Detección':>12}{'Tasa':>8}")
    print("-" * 50)
    for nombre, transformar in condiciones.items():
        detectadas = 0
        for img in base:
            try:
                if lsp_core.extraer_landmarks(transformar(img)) is not None:
                    detectadas += 1
            except Exception:
                pass
        tasa = detectadas / len(base) * 100
        filas.append({
            "condicion": nombre,
            "detectadas": detectadas,
            "total": len(base),
            "tasa_deteccion_pct": round(tasa, 1),
        })
        print(f"{nombre:<30}{detectadas:>5}/{len(base):<5}{tasa:>7.1f}%")

    ruta = guardar_csv("robustez.csv", filas)
    print(f"\n✅ Reporte guardado en {ruta}")


if __name__ == "__main__":
    main()
