# landmarks_csv/ — Dataset Colaborativo LSP

Esta carpeta recibe los archivos CSV de landmarks exportados por cada integrante del equipo.
Los CSV **no se suben al repositorio** (están en `.gitignore`) porque son archivos pesados
que se comparten entre compañeros fuera de git.

---

## Archivos esperados

```
landmarks_csv/
├── landmarks_oscar.csv       ← exportado por Oscar Rodriguez
├── landmarks_deyvis.csv      ← exportado por José Armas
├── landmarks_nicolas.csv     ← exportado por Nicolás Arias
├── landmarks_oscar_m.csv     ← exportado por Oscar Reátegui
└── landmarks_santiago.csv    ← exportado por Santiago Timana
```

Convención de nombre: `landmarks_<tu_nombre>.csv` (sin espacios, sin tildes).

---

## Formato del CSV

43 columnas por fila:

```
letra, x0, y0, x1, y1, ..., x20, y20
a, 0.512, 0.743, 0.489, 0.698, ..., 0.521, 0.612
b, 0.601, 0.812, ...
```

- `letra` — carácter del alfabeto LSP (`a`–`z`)
- `x0..x20`, `y0..y20` — coordenadas normalizadas [0, 1] de los 21 landmarks de MediaPipe Hands

---

## Cómo generar tu CSV

```bash
# Opción 1 — script Python
py -3.12 scripts/extraer_landmarks.py

# Opción 2 — acceso rápido Windows
scripts/COMPANEROS_extraer_landmarks.bat
```

El script captura tus señas desde la cámara y guarda el CSV en esta misma carpeta
con el nombre que ingreses.

---

## Cómo combinar y reentrenar el modelo

Una vez que todos los CSV estén aquí:

```bash
# Combina los CSV y entrena el SVM unificado
py -3.12 scripts/entrenar_desde_csv.py

# Acceso rápido Windows
scripts/4_ENTRENAR_desde_CSV.bat
```

El resultado es un nuevo `modelo.pkl` entrenado con los datos de todo el equipo.
Ese archivo sí se sube al repositorio (`git add modelo.pkl`).

---

> Ver: `TUTORIAL_EQUIPO.md` para el flujo completo de colaboracion Git.
> Ver: `TUTORIAL_DESPLIEGUE_WEB.md` para reentrenar antes de cada despliegue.
