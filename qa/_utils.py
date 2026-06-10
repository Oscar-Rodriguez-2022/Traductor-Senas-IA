"""Utilidades compartidas por los scripts de QA: rutas, CSV y formato."""
import os
import sys
import csv
import json
from datetime import datetime

# La consola de Windows (cp1252) crashea con emojis. Forzamos UTF-8 en la salida.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPORTES = os.path.join(RAIZ, "reportes")
os.makedirs(REPORTES, exist_ok=True)


def banner(titulo):
    print("\n" + "=" * 70)
    print(f"  {titulo}")
    print("=" * 70)


def guardar_csv(nombre, filas):
    """filas: lista de dicts. Devuelve la ruta del CSV escrito."""
    ruta = os.path.join(REPORTES, nombre)
    if not filas:
        return ruta
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        escritor.writeheader()
        escritor.writerows(filas)
    return ruta


def guardar_json(nombre, datos):
    ruta = os.path.join(REPORTES, nombre)
    datos = dict(datos)
    datos["_generado"] = datetime.now().isoformat(timespec="seconds")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)
    return ruta
