"""
Fase 5 — Benchmark de rendimiento por etapa del pipeline.
Mide carga de modelo, detección MediaPipe, extracción, clasificación y total.

Uso:  python qa/benchmark.py
"""
import os
import sys
import time
import statistics

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
import lsp_core
from qa._utils import guardar_csv, banner

N = 60  # número de mediciones


def cronometrar(func, repeticiones=N):
    tiempos = []
    for _ in range(repeticiones):
        t0 = time.perf_counter()
        func()
        tiempos.append((time.perf_counter() - t0) * 1000.0)  # ms
    return tiempos


def resumen(nombre, tiempos):
    return {
        "etapa": nombre,
        "promedio_ms": round(statistics.mean(tiempos), 2),
        "minimo_ms": round(min(tiempos), 2),
        "maximo_ms": round(max(tiempos), 2),
        "desv_std_ms": round(statistics.pstdev(tiempos), 2),
    }


def main():
    banner("FASE 5 — BENCHMARK DE RENDIMIENTO")

    # Carga del modelo (medida varias veces)
    t_carga = cronometrar(lambda: lsp_core.cargar_modelo(), repeticiones=10)
    modelo = lsp_core.cargar_modelo()

    imagenes = [r for r in lsp_core.imagenes_disponibles()]
    if not imagenes:
        print("No hay imágenes en data/. Captura dataset primero.")
        return
    import cv2
    img = cv2.imread(imagenes[0])
    # Asegurar imagen con mano
    for r in imagenes:
        if lsp_core.extraer_landmarks_de_archivo(r) is not None:
            img = cv2.imread(r)
            break

    landmarks = lsp_core.extraer_landmarks(img)

    t_deteccion = cronometrar(lambda: lsp_core.extraer_landmarks(img))
    t_clasif = cronometrar(lambda: lsp_core.predecir(modelo, landmarks))

    def pipeline_total():
        lm = lsp_core.extraer_landmarks(img)
        if lm:
            lsp_core.predecir(modelo, lm)

    t_total = cronometrar(pipeline_total)

    filas = [
        resumen("Carga de modelo", t_carga),
        resumen("Deteccion + extraccion (MediaPipe)", t_deteccion),
        resumen("Clasificacion SVM", t_clasif),
        resumen("Pipeline total por prediccion", t_total),
    ]

    print(f"\n{'Etapa':<42}{'Prom(ms)':>10}{'Min':>8}{'Max':>8}{'Std':>8}")
    print("-" * 76)
    for f in filas:
        print(f"{f['etapa']:<42}{f['promedio_ms']:>10}{f['minimo_ms']:>8}{f['maximo_ms']:>8}{f['desv_std_ms']:>8}")

    ruta = guardar_csv("benchmark.csv", filas)
    print(f"\n[OK] Reporte guardado en {ruta}")


if __name__ == "__main__":
    main()
