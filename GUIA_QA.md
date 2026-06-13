# 🧪 Guía de Calidad de Software — Traductor LSP (UPN)

Capa profesional de pruebas, métricas y validación para el Capstone.
Todo es **ejecutable desde terminal** y genera **evidencias** para la sustentación.

---

## 1. Instalación (una sola vez)

```bash
pip install -r requirements-dev.txt
```

> En esta laptop ya está instalado. Para otra PC, instala Python 3.12 y ese comando.

---

## 2. Forma más fácil de usar todo: `QA.bat`

**Doble clic en `QA.bat`** → menú con todas las opciones (1 a 13).
La opción **13 (EJECUTAR TODO)** corre la suite completa y deja los reportes en `reportes/`.

---

## 3. Comandos individuales (terminal)

Con `make` (Git Bash) o con el menú `QA.bat`:

| Fase | Qué mide | Comando | Salida |
|---|---|---|---|
| 2,4,14 | Pruebas unitarias + integración | `pytest tests/` | consola |
| 3 | Cobertura de código | `pytest --cov=lsp_core --cov-report=html` | `htmlcov/` |
| 5 | Rendimiento por etapa | `python qa/benchmark.py` | `reportes/benchmark.csv` |
| 6 | FPS sostenidos (30s) | `python qa/fps_test.py` | `reportes/fps.csv` |
| 7 | Estrés (100..5000) | `python qa/stress_test.py` | `reportes/stress.csv` |
| 8,9 | RAM y CPU | `python qa/recursos.py` | `reportes/recursos.csv` |
| 10 | Accuracy/Precision/Recall/F1 | `python qa/evaluate.py` | `reportes/metricas*.csv` |
| 11 | Matriz de confusión | `python qa/confusion_matrix.py` | `reportes/matriz_confusion.png` |
| 12 | Validación cruzada K-Fold | `python qa/cross_validation.py` | `reportes/cross_validation.csv` |
| 13 | Robustez (luz, ruido, rotación...) | `python qa/robustez.py` | `reportes/robustez.csv` |
| 18 | Reporte consolidado | `python qa/generar_reportes.py` | `reportes/REPORTE_QA.pdf` y `.html` |
| 16 | Calidad de código | `flake8 ...` / `black ...` / `pylint ...` | consola |
| 19 | Dashboard web de métricas | `streamlit run src/app.py` → menú *Metricas QA* | navegador |

---

## 4. Estructura creada

```
lsp_core.py            ← núcleo testeable (carga, landmarks, validación, predicción)
tests/                 ← pruebas pytest (27, reales)
  conftest.py
  test_modelo.py
  test_landmarks.py
  test_validacion.py
  test_integracion.py
  test_errores.py
qa/                    ← scripts de medición
  benchmark.py  fps_test.py  stress_test.py  recursos.py
  evaluate.py  confusion_matrix.py  cross_validation.py  robustez.py
  generar_reportes.py
reportes/              ← evidencias generadas (CSV, PNG, PDF, HTML)
pages/1_Metricas_QA.py ← dashboard de métricas en la web
Makefile  QA.bat       ← automatización
setup.cfg  pyproject.toml  requirements-dev.txt
SEGURIDAD.md           ← análisis de seguridad (Fase 15)
```

---

## 5. Resultados actuales (con el dataset de ahora)

| Métrica | Valor |
|---|---|
| Pruebas unitarias | **27/27 PASS** |
| Cobertura de `lsp_core` | **96%** |
| Pylint | **7.14/10** |
| Flake8 | **Limpio** |
| Latencia SVM | **~0.1 ms** |
| Pipeline completo | **~18 ms/predicción** |
| Estrés 5000 pred. | **0 errores, sin degradación** |
| Accuracy (entrenamiento) | **92.9%** |

> ⚠️ La **validación cruzada** y el F1 mejorarán cuando el dataset esté balanceado.
> Hoy varias letras tienen 1-9 muestras (k-fold se omite si una clase tiene < k).
> Captura más con A.py / sistema de CSV y reentrena para métricas robustas.

---

## 6. Evidencias para la sustentación

1. `reportes/REPORTE_QA.pdf` — documento consolidado con todas las tablas.
2. `reportes/matriz_confusion.png` — para la diapositiva.
3. `htmlcov/index.html` — cobertura navegable.
4. Captura del **dashboard de Métricas** en la web.
5. Salida de `pytest tests/ -v` (27 pruebas en verde).

---

## 7. Honestidad de ingeniería (qué SÍ y qué NO está automatizado)

- ✅ **Automatizado de verdad:** unitarias, integración, rendimiento, FPS, estrés,
  RAM/CPU, accuracy, matriz, k-fold, robustez (por aumentación de imagen).
- ⚠️ **No 100% automatizable sin hardware:** las condiciones reales de luz/fondo se
  **simulan** transformando imágenes (no es una cámara real bajo el sol). La cámara
  física y la web en vivo se validan con el checklist manual de abajo.
- ⚠️ **Seguridad web:** no hay backend Flask/SQL, por lo que XSS/CSRF/SQLi no aplican
  de forma clásica; ver `SEGURIDAD.md`.

### Checklist manual (cámara real)
- [ ] Cámara desconectada → la app no crashea, muestra "Esperando…".
- [ ] Webcam ocupada por otra app → mensaje controlado.
- [ ] Poca luz real → baja detección (coincide con `robustez.csv`).
- [ ] Mano lejos/cerca → comportamiento esperado.
- [ ] Recargar página → reinicia limpio.
```
