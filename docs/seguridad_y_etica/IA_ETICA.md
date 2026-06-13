# IA Ética — LSP Vision AI
## Transparencia, Explicabilidad (XAI) y Equidad del Sistema de Visión Artificial
### Universidad Privada del Norte · Capstone Project Sistemas 2026
### Autor: Rodriguez Chacara, Oscar Daniel · Versión 2.1 · 2026-06-13

> Este documento forma parte del artefacto de Sprint 3 (HU-16, HU-20) y cumple con los
> principios de IA Ética exigidos por el Capstone: Explicabilidad (XAI), equidad,
> privacidad por diseño y responsabilidad social.
>
> **v2.1:** Actualizado post-reingeniería — INC-07 resuelto (letras con recall 0%), equidad
> mínima por clase ≥ 50% verificada automáticamente por `tests/test_etica.py` (29 tests en 5 clases).
> API de XAI programática documentada en §2.4: `explicar_prediccion()`, `nombres_landmarks()`, `sesgos_conocidos()`
> disponibles en `src/lsp_core.py` y verificadas por `TestXAI` (14 tests).

---

## 1. Principios de IA Ética Adoptados

El sistema **LSP Vision AI** fue diseñado siguiendo cinco principios de IA Ética:

| Principio | Implementación en el sistema |
|-----------|------------------------------|
| **Transparencia** | Pipeline explicado en la UI (`render_pipeline_explicado`). Confianza del modelo visible al usuario en todo momento (0–100%). |
| **Explicabilidad (XAI)** | El expander *"¿Cómo decide la IA?"* explica en lenguaje accesible cómo MediaPipe extrae 42 coordenadas y cómo el SVM usa hiperplanos para clasificar. |
| **Equidad / No-sesgo** | Análisis de recall por clase en `qa/evaluate.py` y `qa/confusion_matrix.py`. Borde amarillo cuando la confianza es < 60% para alertar al usuario sobre ambigüedad. |
| **Privacidad** | Ningún frame de video ni vector de landmarks se persiste. Procesamiento en memoria efímera. Cumple GDPR Art. 25 (documentado en `SEGURIDAD.md`). |
| **Responsabilidad** | Entrenamiento solo con datos del equipo UPN. Modelo PKL verificado con SHA-256 antes de cargar (`lsp_core.verificar_integridad_modelo`). Log de auditoría sin datos personales. |

---

## 2. Explicabilidad del Sistema (XAI)

### 2.1 Arquitectura explicable

El sistema usa un pipeline **interpretable por diseño**:

```
Frame BGR → MediaPipe Hands → 42 coordenadas (x,y) → SVM → letra + confianza%
```

A diferencia de una CNN (caja negra de millones de parámetros), el SVM con vectores de landmarks permite:

- **Inspección directa del vector de entrada:** las 42 coordenadas son coordenadas geométricas de la mano, interpretables por cualquier persona.
- **Probabilidad de Platt como confianza:** la confianza (0–100%) es la probabilidad calibrada P(clase|vector) × 100. No es una métrica arbitraria.
- **Identificación de casos ambiguos:** letras como B/E, A/S, G/Q tienen vectores de landmarks similares — el sistema lo indica con el borde amarillo antes de comprometer una predicción errónea.

### 2.2 Landmarks con mayor poder discriminativo

Los puntos anatómicos más importantes para distinguir letras del LSP son:

| Grupo de landmarks | MediaPipe IDs | Letras diferenciadas |
|---|---|---|
| **Puntas de dedos** | 4, 8, 12, 16, 20 | A (pulgar) vs B (todos extendidos) vs E (doblados) |
| **Nudillos medios** | 6, 10, 14, 18 | F/Y (posición anular/meñique) |
| **Muñeca y palma** | 0, 1, 5, 9, 13 | Orientación general de la mano |

Esta información está disponible en el expander *"¿Cómo decide la IA?"* dentro de la aplicación.

### 2.3 Indicadores visuales de confianza

| Estado | Borde | Significado para el usuario |
|--------|-------|-----------------------------|
| ≥ 60% confianza | Rojo `#E30613` | Predicción con alta seguridad — registrar la letra |
| < 60% con mano | Amarillo `#f0a500` | Ambigüedad — repetir la seña o ajustar posición |
| Sin mano | Sin borde | El sistema espera una mano visible |

### 2.4 API de Explicabilidad Programática (`src/lsp_core.py`)

El módulo `src/lsp_core.py` expone tres funciones XAI verificables por tests automáticos (DT-19):

| Función | Retorno | Propósito |
|---------|---------|-----------|
| `explicar_prediccion(modelo, landmarks, top_n=5)` | `dict {letra, confianza, alternativas, n_clases}` | Devuelve la letra predicha con su confianza y los top-N candidatos alternativos ordenados por probabilidad. Permite mostrar al usuario cuánto "dudó" el modelo. |
| `nombres_landmarks()` | `dict[int, str]` | Mapa de los 21 índices MediaPipe (0–20) a sus nombres anatómicos en español (Muñeca, Base pulgar, Punta índice, etc.). Permite etiquetar cada coordenada del vector de 42 floats con su significado real. |
| `sesgos_conocidos()` | `dict[str, str]` | Devuelve los 5 sesgos documentados del modelo: `diversidad_entrenamiento`, `letras_dinamicas`, `iluminacion`, `letras_similares`, `sesgo_de_datos`. Texto visible en la UI y verificable en tests. |

**Estructura del dict XAI devuelto por `explicar_prediccion()`:**

```python
{
    "letra":        "a",                          # letra principal predicha
    "confianza":    87.3,                         # confianza en % (0.0–100.0)
    "alternativas": [                             # top-5 candidatos
        {"letra": "s", "confianza": 6.2},
        {"letra": "e", "confianza": 3.1},
        ...
    ],
    "n_clases":     24,                           # clases que conoce el modelo
}
```

**Verificación automática:** `tests/test_etica.py::TestXAI` — 14 tests que verifican estructura del dict, coherencia de confianzas (suman 100%), existencia de alternativas, claves de `NOMBRES_LANDMARKS` (0–20), y entradas obligatorias de `SESGOS_CONOCIDOS`.

---

## 3. Análisis de Sesgos y Limitaciones

### 3.1 Sesgos identificados

> Los sesgos listados aquí están codificados y verificados en `lsp_core.sesgos_conocidos()` (5 entradas) y documentados en la UI a través de `lsp_ui.render_pipeline_explicado()`. `tests/test_etica.py::TestXAI` verifica que todas las claves obligatorias estén presentes.

| Tipo de sesgo | Descripción | Mitigación implementada |
|---|---|---|
| **Sesgo de representatividad** | El modelo fue entrenado exclusivamente con imágenes del equipo UPN (4 personas). No representa la diversidad de tonos de piel, tamaños de mano ni condiciones de iluminación de la población peruana. | Data augmentation × 16 (rotaciones, escala, ruido). Instrucción al usuario de recapturar con variedad de condiciones. |
| **Sesgo de clase** | Letras capturadas primero (A, B, C) tienen más muestras que las últimas. Esto puede causar menor recall para letras con pocas muestras. | `qa/cross_validation.py` detecta clases desequilibradas. `qa/confusion_matrix.py` identifica confusiones sistemáticas. |
| **Sesgo de letras dinámicas** | Las letras J y Z del alfabeto LSP requieren movimiento. El sistema solo reconoce gestos estáticos. | Documentado en la UI. Recomendación: omitir J/Z en comunicación con el sistema. |
| **Sesgo de iluminación** | El rendimiento del modelo decrece en condiciones de luz muy baja o con luces de fondo directas. | `qa/robustez.py` evalúa el rendimiento en condiciones adversas. El borde amarillo avisa al usuario. |

### 3.2 Métricas de equidad por clase

Ejecutar `make confusion` y `make evaluate` para generar:
- `reportes/metricas_por_clase.csv`: recall, precision y F1 por letra
- `reportes/confusion_matrix.png`: heatmap que muestra confusiones sistemáticas

**Criterio de equidad mínimo:** ninguna clase debe tener recall < 50% con el dataset completo.

**Estado actual (post-reingeniería v2.0):**
- INC-07 resuelto: letras N, Q, R, S, V recapturadas con 120+ muestras válidas + augmentación ×16.
- Accuracy global: 88.3% (umbral: ≥85%).
- Recall mínimo por clase: ≥80% para todas las letras implementadas.
- `tests/test_etica.py::TestEquidad::test_todas_las_clases_tienen_recall_positivo` → PASS.
- `tests/test_etica.py::TestEquidad::test_equidad_minima_por_clase_recall_mayor_50` → PASS.

### 3.3 Limitaciones honestas del sistema

1. **No reemplaza a un intérprete LSP profesional.** El sistema reconoce letras individuales del alfabeto manual, no palabras completas, frases ni expresiones faciales de la LSP.
2. **Dependiente del dataset de entrenamiento.** La precisión varía según la variabilidad del gestuario del usuario frente al del equipo de entrenamiento.
3. **Solo gestos estáticos.** Las letras J y Z (con movimiento) no están soportadas en la versión actual.
4. **Requiere buena iluminación.** Condiciones de luz muy bajas o backlighting reducen la capacidad de MediaPipe para detectar landmarks.
5. **Hardware dependiente.** El sistema usa la CPU del servidor; en entornos con alta carga puede aumentar la latencia.

---

## 4. Responsabilidad Social y Accesibilidad

### 4.1 Propósito de inclusión

LSP Vision AI fue diseñado para **reducir la barrera de comunicación** entre personas sordas o con dificultades auditivas y oyentes. El objetivo es que cualquier persona pueda usar la aplicación como herramienta de apoyo a la comunicación sin necesidad de conocer previamente la LSP.

### 4.2 Accesibilidad como criterio de diseño (WCAG 2.1 AA)

El frontend implementa los siguientes controles de accesibilidad (detallados en `DEFINITION_OF_DONE.md`):

| Criterio WCAG | Implementación |
|---|---|
| 1.4.3 — Contraste (AA) | Colores corregidos: `#6b6b6b` / `#767676` (ratio ≥ 4.5:1) |
| 1.3.1 — Información y relaciones | `role="banner"`, `role="contentinfo"`, `role="progressbar"` |
| 4.1.3 — Mensajes de estado | `aria-live="polite"` en el panel de resultado |
| 2.4.1 — Saltar bloques (A) | Skip-nav funcional (link visible al recibir Tab) |
| 2.4.7 — Foco visible | Estilos `focus-visible` en todos los elementos interactivos |
| 3.1.1 — Idioma de la página | `lang="es"` inyectado vía `render_estilos()` |

### 4.3 Uso responsable

El sistema:
- **No almacena** imágenes, videos ni vectores de landmarks (privacidad por diseño).
- **No identifica** a las personas; el log de auditoría usa IDs de sesión anónimos.
- **No toma decisiones autónomas** que afecten a las personas; sirve como herramienta de apoyo a la comunicación humana.

---

## 5. Verificación Automatizada de Ética (TDD)

La suite `tests/test_etica.py` verifica automáticamente **29 tests en 5 clases**:

| Clase | Tests | Criterio ético verificado |
|-------|-------|--------------------------|
| `TestEquidad` | ~4 | Equidad: ninguna clase con recall 0% ni recall < 50%; modelo no predice fuera del alfabeto LSP |
| `TestCalibracion` | ~4 | Explicabilidad: `predict_proba()` suma 1.0 (Platt), confianza en rango [0,1], calibración coherente |
| `TestExplicabilidad` | ~7 | Transparencia: umbral 60% documentado en UI, expander de limitaciones presente, pipeline explicado visible |
| `TestXAI` | **14** | API XAI: estructura del dict `explicar_prediccion`, coherencia confianzas (suman ~100%), top-N alternativas, claves de `NOMBRES_LANDMARKS` (0–20), entradas de `SESGOS_CONOCIDOS` (`diversidad_entrenamiento`, `letras_dinamicas`, `iluminacion`, `letras_similares`, `sesgo_de_datos`) |
| `TestPrivacidadEtica` | ~4 | Privacidad: log no almacena landmarks biométricos, no hay PII en audit log |
| **Total** | **29** | **5 dimensiones de ética IA verificadas automáticamente** |

**Tests representativos por criterio:**

| Test | Criterio |
|------|---------|
| `TestEquidad::test_todas_las_clases_tienen_recall_positivo` | Equidad base |
| `TestEquidad::test_equidad_minima_por_clase_recall_mayor_50` | Equidad mínima 50% |
| `TestCalibracion::test_predict_proba_suma_uno` | Calibración de Platt |
| `TestExplicabilidad::test_umbral_confianza_60_documentado_en_ui` | Transparencia del umbral |
| `TestExplicabilidad::test_pipeline_explicado_menciona_limitaciones` | Honestidad en UI |
| `TestXAI::test_explicar_prediccion_retorna_dict_con_claves` | Estructura XAI |
| `TestPrivacidadEtica::test_log_no_almacena_landmarks_biometricos` | Privacidad biométrica |

---

## 6. Plan de Mejora Continua de Ética

| Área | Acción futura | Sprint estimado |
|------|---------------|-----------------|
| Representatividad | Incorporar dataset con diversidad demográfica (LSP Corpus PUCP) | v2.0 |
| Equidad dinámica | Entrenar soporte para letras J y Z con LSTM sobre secuencias de landmarks | v2.0 |
| Auditoría externa | Evaluación por la Comunidad Sorda del Perú para validar precisión percibida | v2.0 |
| Explicabilidad avanzada | Implementar SHAP values para visualizar la importancia de cada landmark en la predicción | v3.0 |
| Reporte de sesgo | Generar automáticamente un reporte de equidad por clase al entrenar | v2.0 |

---

## Historial de Versiones

| Versión | Fecha | Cambio |
|---------|-------|--------|
| 1.0 | 2026-06-12 | Versión inicial — análisis de sesgos, XAI, WCAG, responsabilidad social |
| 2.0 | 2026-06-13 | Actualización post-reingeniería — INC-07 resuelto (equidad verificada), estado de tests actualizado, sección de equidad por clase con resultados reales |
| 2.1 | 2026-06-13 | §2.4 nueva: API XAI de `lsp_core.py` (`explicar_prediccion`, `nombres_landmarks`, `sesgos_conocidos`); §3.1 referencia a `sesgos_conocidos()`; §3.2 nombres de tests con clase; §5 expandida a 29 tests en 5 clases (`TestXAI` 14 destacado) |
