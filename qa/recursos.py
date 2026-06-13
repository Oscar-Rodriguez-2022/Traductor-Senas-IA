"""
Fases 8 y 9 — Consumo de RAM y CPU durante detección continua.
Detecta posibles fugas de memoria (memory leaks).

Uso:  python qa/recursos.py [segundos]
"""
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
import lsp_core
from qa._utils import guardar_csv, banner

DURACION = 20


def main(duracion=DURACION):
    banner(f"FASES 8-9 — CONSUMO DE RAM Y CPU ({duracion}s)")
    try:
        import psutil
    except ImportError:
        print("Falta psutil. Instala con: pip install psutil")
        return
    import cv2

    proc = psutil.Process(os.getpid())
    rutas = lsp_core.imagenes_disponibles()
    frames = [cv2.imread(r) for r in rutas[:60]]
    frames = [f for f in frames if f is not None]
    modelo = lsp_core.cargar_modelo()

    # Calentamiento: MediaPipe carga su modelo en los primeros frames.
    # Lo ejecutamos ANTES de medir para no confundir esa carga única con un leak.
    for f in frames[:10]:
        lsp_core.extraer_landmarks(f, static_image_mode=False)

    proc.cpu_percent(None)  # primera lectura (se descarta)
    ram_inicial = proc.memory_info().rss / (1024 * 1024)
    rams, cpus = [], []

    fin = time.perf_counter() + duracion
    i = 0
    print("Midiendo recursos...")
    while time.perf_counter() < fin:
        frame = frames[i % len(frames)]
        lm = lsp_core.extraer_landmarks(frame, static_image_mode=False)
        if lm:
            lsp_core.predecir(modelo, lm)
        i += 1
        if i % 15 == 0:
            rams.append(proc.memory_info().rss / (1024 * 1024))
            cpus.append(proc.cpu_percent(None))

    ram_final = proc.memory_info().rss / (1024 * 1024)
    fuga = ram_final - ram_inicial

    fila = {
        "ram_inicial_mb": round(ram_inicial, 1),
        "ram_promedio_mb": round(sum(rams) / len(rams), 1) if rams else round(ram_final, 1),
        "ram_maxima_mb": round(max(rams), 1) if rams else round(ram_final, 1),
        "ram_final_mb": round(ram_final, 1),
        "posible_leak_mb": round(fuga, 1),
        "cpu_promedio_pct": round(sum(cpus) / len(cpus), 1) if cpus else 0.0,
        "cpu_pico_pct": round(max(cpus), 1) if cpus else 0.0,
    }
    print(f"\n  RAM inicial   : {fila['ram_inicial_mb']} MB")
    print(f"  RAM promedio  : {fila['ram_promedio_mb']} MB")
    print(f"  RAM máxima    : {fila['ram_maxima_mb']} MB")
    print(f"  Posible leak  : {fila['posible_leak_mb']:+} MB  ({'OK' if fuga < 50 else 'REVISAR'})")
    print(f"  CPU promedio  : {fila['cpu_promedio_pct']} %")
    print(f"  CPU pico      : {fila['cpu_pico_pct']} %")
    ruta = guardar_csv("recursos.csv", [fila])
    print(f"\n[OK] Reporte guardado en {ruta}")


if __name__ == "__main__":
    seg = int(sys.argv[1]) if len(sys.argv) > 1 else DURACION
    main(seg)
