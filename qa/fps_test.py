"""
Fase 6 — Medición de FPS sostenidos durante 30 s.
Procesa imágenes del dataset en bucle simulando el flujo de cámara
(sin hardware) y reporta FPS promedio/máximo/mínimo.

Uso:  python qa/fps_test.py [segundos]
"""
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import lsp_core
from qa._utils import guardar_csv, banner

DURACION = 30


def main(duracion=DURACION):
    banner(f"FASE 6 — MEDICIÓN DE FPS ({duracion}s continuos)")
    import cv2

    rutas = lsp_core.imagenes_disponibles()
    if not rutas:
        print("No hay imágenes en data/.")
        return
    frames = [cv2.imread(r) for r in rutas[:120]]
    frames = [f for f in frames if f is not None]
    modelo = lsp_core.cargar_modelo()

    fps_por_segundo = []
    fin = time.perf_counter() + duracion
    i = 0
    cuenta = 0
    t_ventana = time.perf_counter()
    print("Procesando... (espera ~%ds)" % duracion)
    while time.perf_counter() < fin:
        frame = frames[i % len(frames)]
        lm = lsp_core.extraer_landmarks(frame, static_image_mode=False)
        if lm:
            lsp_core.predecir(modelo, lm)
        i += 1
        cuenta += 1
        if time.perf_counter() - t_ventana >= 1.0:
            fps_por_segundo.append(cuenta)
            cuenta = 0
            t_ventana = time.perf_counter()

    if not fps_por_segundo:
        fps_por_segundo = [i / duracion]

    prom = sum(fps_por_segundo) / len(fps_por_segundo)
    fila = {
        "frames_totales": i,
        "fps_promedio": round(prom, 1),
        "fps_maximo": max(fps_por_segundo),
        "fps_minimo": min(fps_por_segundo),
    }
    print(f"\n  Frames procesados : {fila['frames_totales']}")
    print(f"  FPS promedio      : {fila['fps_promedio']}")
    print(f"  FPS máximo        : {fila['fps_maximo']}")
    print(f"  FPS mínimo        : {fila['fps_minimo']}")
    ruta = guardar_csv("fps.csv", [fila])
    print(f"\n✅ Reporte guardado en {ruta}")


if __name__ == "__main__":
    seg = int(sys.argv[1]) if len(sys.argv) > 1 else DURACION
    main(seg)
