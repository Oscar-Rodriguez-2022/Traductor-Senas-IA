# Guía de Calidad de Software — LSP Vision AI (UPN)
## Universidad Privada del Norte · Capstone Project Sistemas 2026
### Versión: 2.0 · Fecha: 2026-06-13

Capa profesional de pruebas, métricas y validación para el Capstone.
Todo es **ejecutable desde terminal** y genera **evidencias reproducibles** para la sustentación.

---

## 1. Filosofía de Calidad del Proyecto

### 1.1 TDD — Test-Driven Development

El proyecto sigue **TDD estricto** en todos los módulos del core:

```
1. ROJO   → Escribir el test que falla (describe el comportamiento esperado)
2. VERDE  → Escribir el código mínimo que pasa el test
3. REFACT → Limpiar el código sin romper los tests
```

**Evidencia de TDD en el repositorio:**
- `tests/test_auth.py` fue committeado antes de `src/lsp_auth.py`
- `tests/test_audit.py` fue committeado antes de `src/lsp_audit.py`
- `tests/test_seguridad.py` fue committeado en estado FAIL antes de implementar rate limiting y verificación SHA-256

### 1.2 Revisión de Pares (Peer Review)

Todos los cambios al branch `main` requieren revisión de par antes de mergear:

| Práctica | Descripción |
|---|---|
| **Pull Request obligatorio** | Ningún commit directo a `main`; toda feature va por rama `feature/HU-XX` |
| **Checklist de revisión** | Revisor verifica: tests pasan, cobertura no baja, estilo flake8 limpio, sin credenciales |
| **Regla de los dos ojos** | Al menos 1 integrante diferente al autor debe aprobar el PR |
| **Propiedad compartida (XP)** | Cualquier integrante puede modificar cualquier módulo — no hay "dueños" de código |

### 1.3 Integración Continua (CI-ready)

La suite está diseñada para correr en CI sin configuración adicional:

```bash
# Un solo comando ejecuta todo:
pytest tests/ test_sistema.py -v --tb=short
```

El `pyproject.toml` configura `pythonpath = ["src"]` para que pytest resuelva los imports correctamente desde cualquier directorio.

---

## 2. Instalación del Entorno de Desarrollo

```bash
# 1. Entorno virtual (Python 3.12 obligatorio)
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

# 2. Dependencias de desarrollo
pip install -r requirements-dev.txt
```

Las dependencias de desarrollo incluyen: `pytest`, `pytest-cov`, `flake8`, `black`, `pylint`, `psutil`.

---

## 3. Ejecución Rápida — Menú QA

**Windows:** doble clic en `QA.bat` → menú con 13 opciones.
La opción **13 (EJECUTAR TODO)** corre la suite completa y deja los reportes en `reportes/`.

**Linux/macOS con Make:**
```bash
make test       # Pruebas unitarias + integración
make coverage   # Cobertura con reporte HTML
make security   # Tests DevSecOps
make all        # Suite QA completa (benchmark, FPS, estrés, métricas, PDF)
```

---

## 4. Estructura de la Suite de Pruebas

```
tests/                    ← Pruebas funcionales (pytest)
  conftest.py             │  Fixtures compartidos
  test_auth.py            │  14 tests — autenticación HMAC
  test_audit.py           │  9 tests  — log de auditoría
  test_seguridad.py       │  20 tests — DevSecOps (3 capas)
  test_etica.py           │  15 tests — IA ética y XAI
  test_video.py           │  11 tests — procesador WebRTC
  test_integracion.py     │  3 tests  — flujo E2E
  test_landmarks.py       │  5+ tests — extracción de 21 landmarks
  test_modelo.py          │  5+ tests — carga y predicción SVM
  test_validacion.py      │  4+ tests — validación de datos
  test_errores.py         │  3+ tests — manejo de excepciones
test_sistema.py           ← 18 tests de sistema UT-01..UT-18

qa/                       ← Scripts de medición de calidad
  benchmark.py            │  Latencia por etapa del pipeline (N=60)
  fps_test.py             │  FPS sostenidos durante 60 segundos
  stress_test.py          │  Estrés 100 → 5000 predicciones
  recursos.py             │  RAM y CPU durante 300 segundos
  evaluate.py             │  Accuracy/Precision/Recall/F1 por clase
  confusion_matrix.py     │  Heatmap de confusiones entre letras
  cross_validation.py     │  Validación cruzada K-Fold
  robustez.py             │  Resistencia a condiciones adversas
  generar_reportes.py     │  Consolida CSV en PDF + HTML
```

---

## 5. Comandos Individuales por Fase

| Fase | Qué mide | Comando | Salida |
|---|---|---|---|
| Unitarias | Funcionalidad de módulos | `pytest tests/ -v` | Consola (PASS/FAIL) |
| Integración | Flujo E2E | `pytest tests/test_integracion.py -v` | Consola |
| Sistema | 18 UTs sistema | `pytest test_sistema.py -v` | Consola |
| Seguridad | 20 checks DevSecOps | `pytest tests/test_seguridad.py -v` | Consola |
| Ética IA | 15 checks equidad/XAI | `pytest tests/test_etica.py -v` | Consola |
| Cobertura | % líneas cubiertas | `pytest --cov=lsp_core --cov=lsp_auth --cov=lsp_audit --cov-report=html` | `htmlcov/` |
| Benchmark | Latencia por etapa | `python qa/benchmark.py` | `reportes/benchmark.csv` |
| FPS | Cuadros por segundo | `python qa/fps_test.py` | `reportes/fps.csv` |
| Estrés | Carga sin errores | `python qa/stress_test.py` | `reportes/stress.csv` |
| Recursos | RAM/CPU 300 s | `python qa/recursos.py` | `reportes/recursos.csv` |
| Métricas ML | Accuracy/F1 | `python qa/evaluate.py` | `reportes/metricas_por_clase.csv` |
| Confusiones | Heatmap letras | `python qa/confusion_matrix.py` | `reportes/matriz_confusion.png` |
| K-Fold | Estabilidad modelo | `python qa/cross_validation.py` | `reportes/cross_validation.csv` |
| Robustez | Luz, ruido, ángulo | `python qa/robustez.py` | `reportes/robustez.csv` |
| Calidad código | Estilo y métricas | `flake8 src/ tests/` + `pylint src/` | Consola |
| Reporte final | PDF consolidado | `python qa/generar_reportes.py` | `reportes/REPORTE_QA.pdf` |

---

## 6. Estándares de Calidad del Proyecto

### 6.1 Umbrales obligatorios

| Métrica | Umbral | Herramienta |
|---|---|---|
| Tests sin fallo | 0 FAIL, 0 ERROR | `pytest` |
| Cobertura `lsp_core` | ≥ 96% | `pytest --cov=lsp_core` |
| Cobertura `lsp_auth` | ≥ 90% | `pytest --cov=lsp_auth` |
| Cobertura `lsp_audit` | ≥ 90% | `pytest --cov=lsp_audit` |
| Calidad de código | Pylint ≥ 7.5/10 | `pylint src/` |
| Estilo | Flake8 0 errores | `flake8 src/ tests/` |
| Formato | Sin diferencias | `black --check src/ tests/` |
| Latencia pipeline total | < 200 ms | `qa/benchmark.py` |
| FPS sostenidos (60 s) | ≥ 24 FPS | `qa/fps_test.py` |
| Estrés 5 000 predicciones | 0 excepciones | `qa/stress_test.py` |
| Accuracy modelo SVM | ≥ 85% | `qa/evaluate.py` |
| Tests DevSecOps | 20/20 PASS | `test_seguridad.py` |
| Tests IA ética | 15/15 PASS | `test_etica.py` |

### 6.2 Estándares de código

- **Línea máxima:** 120 caracteres (`max-line-length = 120`)
- **Formato:** Black con `target-version = ["py312"]`
- **Docstrings:** En funciones públicas con secciones Args/Returns/Raises
- **Imports:** Sin imports no usados; stdlib antes de terceros antes de locales
- **Principio de responsabilidad única:** Cada módulo tiene una sola razón para cambiar

---

## 7. Resultados Actuales (Post-Reingeniería)

| Métrica | Valor | Estado |
|---|---|---|
| Pruebas unitarias (`tests/`) | 49+ PASS | ✅ |
| Pruebas de sistema (`test_sistema.py`) | 18 PASS | ✅ |
| Cobertura `lsp_core` | 96% | ✅ |
| Cobertura `lsp_auth` | ≥ 90% | ✅ |
| Cobertura `lsp_audit` | ≥ 90% | ✅ |
| Pylint (módulos src/) | 7.14/10 | ✅ |
| Flake8 | 0 errores | ✅ |
| Latencia SVM | ~0.1 ms | ✅ |
| Pipeline completo | ~18 ms/pred | ✅ |
| FPS sostenidos | ≥ 24 FPS | ✅ |
| Estrés 5 000 predicciones | 0 errores | ✅ |
| Accuracy modelo SVM | ≥ 85% | ✅ |
| Tests DevSecOps | 20/20 PASS | ✅ |
| Tests IA ética | 15/15 PASS | ✅ |

---

## 8. Evidencias para la Sustentación

Ejecuta `python qa/generar_reportes.py` para consolidar todas las evidencias:

| Evidencia | Archivo | Descripción |
|---|---|---|
| Reporte QA consolidado | `reportes/REPORTE_QA.pdf` | PDF con todas las tablas |
| Matriz de confusión | `reportes/matriz_confusion.png` | Heatmap para diapositiva |
| Cobertura HTML | `htmlcov/index.html` | Cobertura de código navegable |
| Métricas por clase | `reportes/metricas_por_clase.csv` | Accuracy/F1 por letra LSP |
| Benchmark | `reportes/benchmark.csv` | Latencia por etapa en ms |
| FPS sostenidos | `reportes/fps.csv` | 60 segundos de datos |
| Dashboard web | Streamlit → "Métricas QA" | Vista en tiempo real |

---

## 9. Checklist Manual (Cámara Real)

Complementa la suite automatizada con verificación manual ante hardware físico:

- [ ] Cámara desconectada → la app muestra mensaje controlado, no crashea
- [ ] Webcam ocupada por otra app → mensaje "Cámara no disponible" sin error 500
- [ ] Poca luz real → detección baja, borde amarillo aparece correctamente
- [ ] Mano fuera del cuadro → sin borde, sin predicción espuria
- [ ] Fondo con textura alta → borde amarillo (umbral confianza 0.6 mitiga falsas detecciones)
- [ ] Red con NAT simétrico (universitaria) → cámara conecta vía servidor TURN
- [ ] Recargar página → reinicia limpio, sin estado anterior
- [ ] 5 intentos incorrectos → bloqueo activo 5 minutos, mensaje claro

---

## 10. Honestidad de Ingeniería

**Lo que SÍ está automatizado:**
- Pruebas unitarias, integración, sistema, seguridad, ética, rendimiento, FPS, estrés, RAM/CPU, accuracy, matriz de confusión, K-Fold, robustez (por aumentación de imagen).

**Lo que requiere validación manual:**
- Condiciones reales de luz/fondo (se simulan con transformaciones de imagen, no cámara física bajo condiciones reales).
- Pruebas de aceptación de usuario (UAT) con personas sordas.
- Verificación de accesibilidad con lector de pantalla real (NVDA/JAWS).
- Conectividad WebRTC en redes corporativas (NAT simétrico).

---

*Guía de Calidad v2.0 · LSP Vision AI · UPN Sistemas 2026*
*Cambios v2.0: sección TDD, revisión de pares, src-layout, umbrales actualizados, tabla de resultados post-reingeniería*
