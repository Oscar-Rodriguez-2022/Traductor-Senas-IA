"""
Fase 7 — Test de estrés: 100/500/1000/5000 predicciones consecutivas.
Mide errores, excepciones y degradación del tiempo de respuesta.

Uso:  python qa/stress_test.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import lsp_core
from qa._utils import guardar_csv, banner

NIVELES = [100, 500, 1000, 5000]


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
    print(f"\n{'Predicciones':>12}{'Errores':>10}{'Prom(ms)':>12}{'Total(s)':>12}")
    print("-" * 46)
    for n in NIVELES:
        errores = 0
        t0 = time.perf_counter()
        for _ in range(n):
            try:
                lsp_core.predecir(modelo, vector)
            except Exception:
                errores += 1
        total = time.perf_counter() - t0
        prom_ms = (total / n) * 1000.0
        fila = {
            "predicciones": n,
            "errores": errores,
            "excepciones": errores,
            "promedio_ms": round(prom_ms, 3),
            "total_s": round(total, 2),
            "estado": "OK" if errores == 0 else "FALLOS",
        }
        filas.append(fila)
        print(f"{n:>12}{errores:>10}{fila['promedio_ms']:>12}{fila['total_s']:>12}")

    ruta = guardar_csv("stress.csv", filas)
    degradacion = filas[-1]["promedio_ms"] - filas[0]["promedio_ms"]
    print(f"\n  Degradación (5000 vs 100): {degradacion:+.3f} ms/predicción")
    print(f"✅ Reporte guardado en {ruta}")


if __name__ == "__main__":
    main()
