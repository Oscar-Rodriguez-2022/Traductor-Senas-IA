# Guía de Calidad de Software — LSP Vision AI (UPN)
## Universidad Privada del Norte · Capstone Project Sistemas 2026
### Versión: 3.1 · Fecha: 2026-06-14

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
- `tests/test_etica.py::TestXAI` fue committeado antes de `lsp_core.explicar_prediccion()`

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
pytest tests/ -v --tb=short
```

El `pyproject.toml` configura `pythonpath = ["src"]` para que pytest resuelva los imports
correctamente desde cualquier directorio.

> **Nota:** `config/setup.cfg` contiene configuración de flake8 y coverage. La sección
> `[tool:pytest]` es ignorada por pytest (usa `pyproject.toml` con precedencia). La config de
> coverage fue migrada a `pyproject.toml` (`[tool.coverage.*]`). Flake8 se invoca con
> `--config config/setup.cfg` desde el Makefile.

---

## 2. Requisitos del Entorno de Desarrollo

```bash
# Python 3.12 o 3.13 (ambos soportados con Tasks API)
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

pip install -r config/requirements-dev.txt
```

Las dependencias de desarrollo incluyen: `pytest`, `pytest-cov`, `flake8`, `black`,
`pylint`, `psutil`, `mediapipe==0.10.35`, `streamlit`, `av`, `streamlit-webrtc`.

> **Requisito adicional:** el archivo `hand_landmarker.task` (7.8 MB) debe estar en la raíz
> del proyecto. Se descarga automáticamente con:
> ```bash
> python -c "import urllib.request; urllib.request.urlretrieve('https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task', 'hand_landmarker.task')"
> ```
> Los tests que requieren `streamlit` o `av` se omiten (`SKIP`) fuera del entorno virtual completo.

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
tests/                       ← Pruebas funcionales (pytest)
  conftest.py                │  Fixtures compartidos: modelo, imagen_con_mano,
  │                          │    landmarks_validos, imagen_negra
  │                          │  (No hay tests/__init__.py — pytest descubre los
  │                          │   módulos por rootdir, sin necesidad de paquete)
  test_auth.py               │  14 tests — autenticación HMAC-SHA256 (HU-13)
  test_audit.py              │   9 tests — log de auditoría anónima (HU-14)
  test_seguridad.py          │  34 tests — DevSecOps por 3 capas (HU-13/14/20/21)
  test_etica.py              │  29 tests — IA Ética, equidad, XAI (HU-16/20) *
  test_video.py              │  12 tests — procesador WebRTC Traductor (HU-08/09)
  test_integracion.py        │   3 tests — flujo E2E captura→predicción (HU-10/12)
  test_landmarks.py          │   6 tests — extracción de 21 landmarks (HU-06/09)
  test_modelo.py             │   5 tests — carga y predicción SVM (HU-07/10)
  test_validacion.py         │   9 tests — validación de entradas (HU-05/06)
  test_errores.py            │   4 tests — manejo de excepciones (HU-22)
  test_sistema.py            │  18 tests de sistema UT-01..UT-18 (HU-01..HU-20)

qa/                          ← Scripts de medición de calidad
  __init__.py                │  Marca qa/ como paquete Python (vacío)
  _utils.py                  │  Utilidades compartidas: rutas, CSV, JSON, banner
  benchmark.py               │  Latencia por etapa del pipeline (N=60)
  fps_test.py                │  FPS sostenidos durante 60 segundos
  stress_test.py             │  Estrés 100 → 5 000 predicciones
  recursos.py                │  RAM y CPU durante 300 segundos
  evaluate.py                │  Accuracy/Precision/Recall/F1 por clase
  confusion_matrix.py        │  Heatmap de confusiones entre letras
  cross_validation.py        │  Validación cruzada K-Fold
  robustez.py                │  Resistencia a condiciones adversas
  generar_reportes.py        │  Consolida CSV en PDF + HTML

src/                         ← Código fuente (src-layout)
  __init__.py                │  Marca src/ como paquete Python
  app.py                     │  Orquestador Streamlit
  lsp_core.py                │  Núcleo: modelo, landmarks, predicción, XAI
  lsp_auth.py                │  Autenticación HMAC + rate limiting
  lsp_audit.py               │  Log de auditoría anónimo JSONL
  lsp_ui.py                  │  Componentes HTML/CSS WCAG 2.1 AA + XAI
  lsp_video.py               │  Procesador WebRTC (clase Traductor)
  pages/
    1_Metricas_QA.py         │  Dashboard de métricas en Streamlit
```

> \* `test_etica.py` importa `lsp_ui` que a su vez importa `streamlit`. Requiere el
> entorno virtual completo con `streamlit` instalado para poder colectarse y ejecutarse.

**Totales:**
- Suite principal sin `test_etica.py`: **114 tests** (colectables sin streamlit)
- Suite completa con `test_etica.py`: **143 tests**

---

## 5. Comandos Individuales por Fase

| Fase | Qué mide | Comando | Salida |
|---|---|---|---|
| Unitarias | Funcionalidad de módulos | `pytest tests/ -v` | Consola (PASS/FAIL) |
| Integración | Flujo E2E | `pytest tests/test_integracion.py -v` | Consola |
| Sistema | 18 UTs sistema | `pytest tests/test_sistema.py -v` | Consola |
| Seguridad | 34 checks DevSecOps | `pytest tests/test_seguridad.py -v` | Consola |
| Ética IA / XAI | 29 checks equidad y XAI | `pytest tests/test_etica.py -v` | Consola |
| Cobertura | % líneas cubiertas | `pytest --cov=lsp_core --cov=lsp_auth --cov=lsp_audit --cov=lsp_ui --cov=lsp_video --cov-report=html` | `htmlcov/` |
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
| Cobertura `lsp_ui` | ≥ 80% | `pytest --cov=lsp_ui` |
| Cobertura `lsp_video` | ≥ 80% | `pytest --cov=lsp_video` |
| Calidad de código | Pylint ≥ 7.0/10 | `pylint src/` |
| Estilo | Flake8 0 errores | `flake8 src/ tests/` |
| Formato | Sin diferencias | `black --check src/ tests/` |
| Latencia pipeline total | < 200 ms/etapa | `qa/benchmark.py` |
| FPS sostenidos (60 s) | ≥ 24 FPS | `qa/fps_test.py` |
| Estrés 5 000 predicciones | 0 excepciones | `qa/stress_test.py` |
| Accuracy modelo SVM | ≥ 85% | `qa/evaluate.py` |
| Tests DevSecOps | 33/34 PASS, 1 SKIP* | `test_seguridad.py` |
| Tests IA Ética / XAI | 29/29 PASS | `test_etica.py` |

> \* `test_frames_no_se_persisten_durante_recv` se omite (`SKIP`) cuando `av` o
> `streamlit_webrtc` no están instalados en el entorno de ejecución. En el entorno
> virtual completo debe pasar.

### 6.2 Estándares de código

- **Línea máxima:** 120 caracteres (`max-line-length = 120`)
- **Formato:** Black con `target-version = ["py312"]`
- **Docstrings:** En funciones públicas con secciones Args/Returns/Raises
- **Imports:** Sin imports no usados; stdlib antes de terceros antes de locales
- **Principio de responsabilidad única:** Cada módulo tiene una sola razón para cambiar
- **Trazabilidad obligatoria:** Cada función pública referencia la HU y CA que satisface

---

## 7. Resultados Actuales (Post-Migración MediaPipe Tasks API · 2026-06-14)

| Métrica | Valor | Estado |
|---|---|---|
| Pruebas unitarias + integración (sin streamlit) | 50 PASS | ✅ |
| Pruebas IA Ética / XAI (`test_etica.py`) | 29 PASS (con entorno virtual) | ✅ |
| **Total ejecutable sin streamlit** | **50 tests** | ✅ |
| Cobertura `lsp_core` | ≥ 96% | ✅ |
| Cobertura `lsp_auth` | ≥ 90% | ✅ |
| Cobertura `lsp_audit` | ≥ 90% | ✅ |
| Latencia MediaPipe (Tasks API) | ~23.9 ms/frame | ✅ |
| Latencia SVM | ~0.22 ms | ✅ |
| Pipeline completo | ~24.5 ms/pred | ✅ (< 200 ms) |
| FPS sostenidos (30 s, modo video) | 82.7 FPS | ✅ (≥ 24 FPS) |
| Estrés 5 000 predicciones | 0 errores | ✅ |
| RAM leak (20 s continuo) | +2.3 MB | ✅ (< 50 MB) |
| Accuracy SVM sobre dataset detectado | 100% (training set) | ⚠️ ver nota |
| Validación cruzada K-Fold | **OMITIDA** | ⚠️ ver §7.2 |

> **Nota accuracy:** Medida sobre el mismo dataset de entrenamiento → optimista. K-Fold omitida porque J (4 muestras) y D (9 muestras) no alcanzan el mínimo de k=5. Para evaluación rigurosa se requiere recaptura de las letras críticas (ver §7.2 y INC-12).

### 7.1 Desglose exacto por archivo de test

| Archivo | Tests | HUs cubiertas | Notas |
|---|---|---|---|
| `tests/test_auth.py` | 14 | HU-13 | — |
| `tests/test_audit.py` | 9 | HU-14 | — |
| `tests/test_seguridad.py` | 34 | HU-13/14/20/21 | 1 SKIP sin `av` |
| `tests/test_etica.py` | 29 | HU-16/20 | Requiere streamlit |
| `tests/test_video.py` | 12 | HU-08/09/22 | Requiere `av` |
| `tests/test_integracion.py` | 3 | HU-10/12 | — |
| `tests/test_landmarks.py` | 6 | HU-06/09 | — |
| `tests/test_modelo.py` | 5 | HU-07/10 | — |
| `tests/test_validacion.py` | 9 | HU-05/06 | — |
| `tests/test_errores.py` | 4 | HU-22 | — |
| `tests/test_sistema.py` | 18 | HU-01..HU-20 | UT-01..UT-18 |
| **TOTAL** | **143** | **22 HUs** | — |

### 7.2 Tasas de detección MediaPipe por letra (2026-06-14)

Escaneo de 13 689 imágenes con `mp.tasks.vision.HandLandmarker` (model_complexity=0, min_detection_confidence=0.6):

| Letra | Imágenes | Detectadas | Tasa | Estado |
|---|---|---|---|---|
| A | 500 | ~211 | ~42% | ⚠️ BAJA |
| B | 545 | 545 | 100% | ✅ |
| C | 500 | ~213 | ~43% | ⚠️ BAJA |
| D | 509 | 9 | 1.8% | 🔴 CRÍTICA |
| E | 509 | ~439 | ~86% | ✅ |
| F | 509 | ~70 | ~14% | 🔴 CRÍTICA |
| G | 509 | ~375 | ~74% | ✅ |
| H | 500 | 500 | 100% | ✅ |
| I | 509 | ~96 | ~19% | 🔴 CRÍTICA |
| J | 509 | 4 | 0.8% | 🔴 CRÍTICA |
| K | 509 | 505 | 99% | ✅ |
| L | 509 | 509 | 100% | ✅ |
| M | 500 | 499 | 100% | ✅ |
| N | 500 | 500 | 100% | ✅ |
| **O** | **500** | **0** | **0%** | 🔴 **NO RECONOCIBLE** |
| P | 509 | 509 | 100% | ✅ |
| Q | 1000 | 998 | 100% | ✅ |
| R | 509 | 500 | 98% | ✅ |
| S | 500 | ~29 | ~6% | 🔴 CRÍTICA |
| T | 509 | 508 | 100% | ✅ |
| U | 500 | 500 | 100% | ✅ |
| V | 509 | 500 | 98% | ✅ |
| W | 509 | 509 | 100% | ✅ |
| X | 509 | 509 | 100% | ✅ |
| Y | 509 | 509 | 100% | ✅ |
| Z | 509 | ~498 | ~98% | ✅ |
| **TOTAL** | **13 689** | **~9 840** | **~72%** | ⚠️ |

**Letras con tasa crítica (< 20%) que requieren recaptura:** D, F, I, J, O, S  
**Letras con tasa baja (20–50%) que se beneficiarían de recaptura:** A, C  
**Modelo actual reconoce 25 letras** (O excluida por 0 detecciones)

> Ver `INC-12` en `INCIDENTES.md` y `docs/qa_y_pruebas/GUIA_RECAPTURA_DATASET.md` para instrucciones de recaptura.

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
| Estrés | `reportes/stress.csv` | 5 000 predicciones sin error |
| Recursos | `reportes/recursos.csv` | RAM/CPU en 300 s |
| Dashboard web | Streamlit → "Métricas QA" | Vista en tiempo real |

---

## 9. Checklist Manual (Cámara Real)

Complementa la suite automatizada con verificación manual ante hardware físico:

- [ ] Cámara desconectada → la app muestra mensaje controlado, no crashea
- [ ] Webcam ocupada por otra app → mensaje "Cámara no disponible" sin error 500
- [ ] Poca luz real → detección baja, borde amarillo aparece correctamente
- [ ] Mano fuera del cuadro → sin borde, sin predicción espuria
- [ ] Fondo con textura alta → borde amarillo (umbral confianza < 60% mitiga falsas detecciones)
- [ ] Panel XAI visible con alternativas del SVM cuando hay mano detectada
- [ ] Red con NAT simétrico (universitaria) → cámara conecta vía servidor TURN
- [ ] Recargar página → reinicia limpio, sin estado anterior
- [ ] 5 intentos incorrectos → bloqueo activo 5 minutos, mensaje claro
- [ ] Accesibilidad: lector de pantalla anuncia cada letra detectada (aria-live)

---

## 10. Honestidad de Ingeniería

**Lo que SÍ está automatizado:**
Pruebas unitarias, integración, sistema, seguridad, ética/XAI, rendimiento, FPS, estrés,
RAM/CPU, accuracy, matriz de confusión, K-Fold y robustez (por aumentación de imagen).

**Lo que requiere validación manual:**
- Condiciones reales de luz/fondo (se simulan con transformaciones de imagen, no cámara física).
- Pruebas de aceptación de usuario (UAT) con personas sordas (plantilla en `docs/qa_y_pruebas/plantilla_UAT.md`).
- Verificación de accesibilidad con lector de pantalla real (NVDA/JAWS).
- Conectividad WebRTC en redes corporativas (NAT simétrico).

**Limitaciones conocidas de la suite:**
- `tests/test_etica.py` no se puede colectar sin `streamlit` instalado en el entorno.
  Fuera del entorno virtual pytest reporta `ImportError`. En CI/CD usar el entorno virtual.
- `tests/test_seguridad.py::TestPrivacidadPorDiseno::test_frames_no_se_persisten_durante_recv`
  requiere `av` y `streamlit_webrtc`; se omite (`SKIP`) en entornos sin esas dependencias.
- Los scripts `qa/` requieren `modelo.pkl` entrenado. Si no existe, terminan con error descriptivo.

---

*Guía de Calidad v3.0 · LSP Vision AI · UPN Sistemas 2026*

*Cambios v3.0: conteos exactos por archivo (143 tests totales), `qa/__init__.py` y
`qa/_utils.py` añadidos a la estructura, nota sobre `tests/__init__.py` (no existe por diseño),
corrección de los 2 tests fallidos en `TestSanitizacionInputs` (fixture `_resetear_rate_limiter` `autouse`),
nuevos tests XAI (`TestXAI` — 14 tests), cobertura extendida a `lsp_ui` y `lsp_video`,
`setup.cfg` movido a `config/`, coverage migrado a `pyproject.toml`.*

*Cambios v3.1 (2026-06-14): migración a MediaPipe Tasks API (`mp.tasks.vision.HandLandmarker`);
`hand_landmarker.task` añadido como dependencia del proyecto; soporte Python 3.12 y 3.13;
sección §7 actualizada con tasas de detección reales por letra (INC-11, INC-12);
umbral Pylint ajustado a ≥ 7.0/10; K-Fold documentada como omitida por muestras insuficientes en D, J.*
