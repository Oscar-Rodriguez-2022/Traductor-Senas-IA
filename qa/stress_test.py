"""
Fase 7 — Test de estrés: 100/500/1000/5000 predicciones consecutivas.
Mide errores, degradación del tiempo de respuesta y crecimiento de memoria (HU-22 CA-22.3).

Criterio de aceptación CA-22.3: la memoria RAM no debe crecer más de 50 MB
respecto al estado inicial durante una sesión sostenida de predicciones.

Uso:  python qa/stress_test.py
"""
import os
import sys
import time
import tracemalloc

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
import lsp_core
from qa._utils import guardar_csv, banner

NIVELES = [100, 500, 1000, 5000]
LIMITE_MEMORIA_MB = 50.0   # umbral CA-22.3


def main():
    banner("FASE 7 — TEST DE ESTRÉS")

    rutas = lsp_core.imagenes_disponibles()
    modelo = lsp_core.cargar_modelo()
    vector = None
    for r in rutas:
        vector = lsp_core.extraer_landmarks_de_archivo(r)
        if vector is not None:
            break
    if vector is None:
        print("No se pudo obtener un vector de landmarks del dataset.")
        return

    filas = []
    print(f"\n{'Predicciones':>12}{'Errores':>10}{'Prom(ms)':>12}{'Total(s)':>12}{'ΔMem(MB)':>12}")
    print("-" * 60)

    tracemalloc.start()
    mem_base_kb, _ = tracemalloc.get_traced_memory()

    for n in NIVELES:
        errores = 0
        tracemalloc.clear_traces()
        mem_inicio_kb, _ = tracemalloc.get_traced_memory()

        t0 = time.perf_counter()
        for _ in range(n):
            try:
                lsp_core.predecir(modelo, vector)
            except Exception:
                errores += 1
        total = time.perf_counter() - t0

        _, mem_pico_kb = tracemalloc.get_traced_memory()
        delta_mb = (mem_pico_kb - mem_inicio_kb) / 1024.0
        prom_ms = (total / n) * 1000.0

        estado = "OK" if errores == 0 else "FALLOS"
        mem_estado = "OK" if delta_mb <= LIMITE_MEMORIA_MB else f"ALERTA >{LIMITE_MEMORIA_MB}MB"

        fila = {
            "predicciones": n,
            "errores": errores,
            "promedio_ms": round(prom_ms, 3),
            "total_s": round(total, 2),
            "delta_memoria_mb": round(delta_mb, 2),
            "estado": estado,
            "memoria_estado": mem_estado,
        }
        filas.append(fila)
        print(f"{n:>12}{errores:>10}{fila['promedio_ms']:>12}{fila['total_s']:>12}{delta_mb:>11.2f}MB")

    tracemalloc.stop()

    ruta = guardar_csv("stress.csv", filas)
    degradacion = filas[-1]["promedio_ms"] - filas[0]["promedio_ms"]
    mem_max = max(f["delta_memoria_mb"] for f in filas)
    mem_ok = mem_max <= LIMITE_MEMORIA_MB

    print(f"\n  Degradación (5000 vs 100): {degradacion:+.3f} ms/predicción")
    print(f"  Pico de memoria (DeltaMB): {mem_max:.2f} MB  -->  {'PASA CA-22.3' if mem_ok else 'SUPERA limite 50 MB'}")
    print(f"[OK] Reporte guardado en {ruta}")


if __name__ == "__main__":
    main()
