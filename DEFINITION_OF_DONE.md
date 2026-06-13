# Definition of Done — LSP Vision AI
## Universidad Privada del Norte · Capstone Project Sistemas 2026
### Autor: Rodriguez Chacara, Oscar Daniel
### Versión: 2.0 · Última actualización: 2026-06-13
### Estado: **PROYECTO CERRADO — 22/22 HUs completadas, 100% criterios DoD satisfechos**

Todo trabajo se considera **"Done"** cuando cumple la totalidad de los criterios de la Sección I antes de marcarse como completado en el tablero Scrum. La Sección II registra el estado de cumplimiento al cierre del Capstone (v2.0).

> **v2.0:** Actualizado tras la reingeniería estructural (src-layout, DevSecOps completo, 49+ tests).
> Todos los criterios han sido verificados y el proyecto está listo para sustentación y despliegue.

---

## Sección I — Criterios Obligatorios (checklist por PBI)

### Calidad de Código

| Criterio | Herramienta | Umbral |
|---|---|---|
| Sin errores de estilo | `flake8` | 0 errores (`max-line-length: 120`) |
| Calidad de código | `pylint` | Score ≥ 7.5/10 por módulo |
| Formato consistente | `black` | Sin diferencias al ejecutar `black --check` |
| Docstrings en funciones públicas | revisión manual | 100% con Args/Returns/Raises |
| Principio de responsabilidad única | Revisión de par | Cada módulo tiene una sola razón para cambiar |
| Estructura de carpetas (`src/`, `scripts/`, `tests/`, `qa/`) | Revisión estructural | Código fuente en `src/`; ejecutables en `scripts/` |

---

### Pruebas (TDD)

| Criterio | Evidencia requerida |
|---|---|
| Tests escritos ANTES del código | Commit separado con tests en estado FAIL (rojo) |
| Cobertura de nuevos módulos | `pytest --cov` ≥ 90% para `lsp_auth`, `lsp_audit` |
| Cobertura del núcleo | `pytest --cov=lsp_core` ≥ 96% mantenida |
| Cero fallos en la suite | `pytest tests/ -v` retorna 0 FAIL y 0 ERROR en el entorno de referencia |
| Pruebas de integración | Al menos 1 test de flujo end-to-end por Historia de Usuario |
| Pruebas de carga / estrés | `qa/benchmark.py` sin etapa > 200 ms · `qa/fps_test.py` ≥ 24 FPS en 60 s · sesión 300 s sin memory leak (HU-22) |

---

### Seguridad (DevSecOps)

| Criterio | Verificación |
|---|---|
| Sin credenciales en código fuente | `git log --all -S "password"` no devuelve coincidencias en texto plano |
| Tokens de sesión con firma HMAC | `lsp_auth.verificar_token()` rechaza tokens manipulados (test incluido) |
| Rate limiting anti-fuerza-bruta | `MAX_INTENTOS=5`, `BLOQUEO_SEGUNDOS=300` verificados en `test_seguridad.py` |
| Integridad del modelo PKL | `calcular_hash_modelo` + `verificar_integridad_modelo` con HMAC-compare_digest |
| Log de auditoría sin datos personales | Ningún campo contiene IP, user-agent ni nombre de usuario |
| Trazas de error ocultas en producción | `.streamlit/config.toml` contiene `showErrorDetails = false` |
| Protección XSRF activa | `.streamlit/config.toml` contiene `enableXsrfProtection = true` |
| Dependencias actualizadas | `pip list --outdated` revisado; vulnerabilidades conocidas atendidas |
| Imagen Docker sin usuario root | `USER lspuser` (UID 1001) en `Dockerfile` |
| Escaneo de vulnerabilidades | `trivy.yaml` configurado; ejecutar `trivy fs .` antes de desplegar |

---

### Accesibilidad (WCAG 2.1 — Nivel AA)

| Criterio | Verificación |
|---|---|
| Contraste de texto ≥ 4.5:1 | Chrome DevTools → Accessibility → sin fallos AA de contraste |
| Elemento de resultado con `aria-live="polite"` | Presente en el HTML del panel de resultado |
| Barra de confianza con `role="progressbar"` + `aria-valuenow` | Presente en el HTML generado |
| Regiones semánticas: `role="banner"` y `role="contentinfo"` | Verificar en DevTools → Elements |
| Enlace skip-nav funcional (WCAG 2.4.1) | Visible al presionar Tab desde el inicio de la página |
| Emojis decorativos con `aria-hidden="true"` | Verificado en el HTML del pipeline |
| `focus-visible` para teclado | CSS en `render_estilos` |
| `lang="es"` en documento | Script inyectado en `render_estilos` |
| Pasos del pipeline con `aria-label` únicos | `render_pipeline_explicado` |

---

### IA Ética y Explicabilidad (XAI)

| Criterio | Verificación |
|---|---|
| Explicabilidad del pipeline visible en UI | Expander con tabla de confianza y pipeline paso a paso |
| Limitaciones y sesgos documentados en UI | Sección "Limitaciones conocidas" en el expander de la app |
| Documento `IA_ETICA.md` completo | Principios, análisis de sesgos, métricas de equidad, plan de mejora |
| Equidad por clase (recall ≠ 0 para ninguna letra) | `tests/test_etica.py::test_todas_las_clases` |
| Calibración de confianza (Platt) | `tests/test_etica.py::test_predict_proba_suma_uno` |
| Privacidad de datos biométricos | `tests/test_etica.py::test_log_no_almacena_landmarks` |

---

### Privacidad y Protección de Datos (GDPR Art. 25)

| Criterio | Estado |
|---|---|
| Frames de video NO se persisten a disco | Procesamiento en memoria — verificado en `src/lsp_video.py` |
| Vector de 42 landmarks NO se almacena | Solo se usa para predicción inmediata y se descarta |
| IDs de sesión en audit log son hash truncado | SHA-256[:8] del token, no reversible a identidad |
| En Streamlit Cloud el log es efímero | Documentado en `SEGURIDAD.md` como comportamiento esperado |

---

### Documentación

| Criterio | Archivo |
|---|---|
| Historias de Usuario con AC actualizados | `HISTORIAS_USUARIO.md` (22 HUs, Gherkin, MoSCoW) |
| Requerimientos (15 RF + 15 RNF) | `docs/requerimientos.md` |
| Arquitectura modular (diagramas Mermaid) | `docs/arquitectura/COMPONENTES.md` |
| Modelo de datos incremental por sprint | `docs/arquitectura/MODELO_DATOS.md` |
| Matriz de trazabilidad HU↔Código↔Test | `MATRIZ_TRAZABILIDAD.md` |
| Guía de instalación y ejecución vigente | `README.md` |
| Análisis de seguridad actualizado | `SEGURIDAD.md` |
| Guía de calidad y pruebas | `GUIA_QA.md` |
| Manual de Usuario Preliminar | `MANUAL_USUARIO.md` |
| Registro de Lecciones Aprendidas | `LECCIONES_APRENDIDAS.md` |
| Plantilla UAT con criterios de aceptación | `docs/plantilla_UAT.md` |
| IA Ética y equidad | `IA_ETICA.md` |
| Log de incidentes y bugs resueltos | `INCIDENTES.md` |

---

### Revisión de Par

| Criterio | Evidencia |
|---|---|
| Pull Request aprobado | Al menos 1 revisión de otro integrante del equipo |
| Checklist manual ejecutado | Verificado en Chrome + Firefox |
| Sin comentarios de revisión pendientes | Todos los hilos resueltos antes de mergear |

---

## Sección II — Estado de Cumplimiento al Cierre (v2.0 · 2026-06-13)

> Checkpoint ejecutivo: evidencia de que cada criterio de la Sección I está satisfecho.

### Calidad de Código — ✅ CUMPLE

| Criterio | Estado |
|---|---|
| Sin errores de estilo | ✅ `make lint` → 0 errores |
| Calidad de código | ✅ Módulos core ≥ 7.5/10 |
| Formato consistente | ✅ `make format` aplicado |
| Docstrings en funciones públicas | ✅ 100% con Args/Returns/Raises |
| Principio de responsabilidad única | ✅ 6 módulos independientes (`src/`) |
| Estructura `src/` + `scripts/` | ✅ Reingeniería aplicada en v1.0 |

### Pruebas (TDD) — ✅ CUMPLE

| Criterio | Evidencia | Estado |
|---|---|---|
| Tests escritos ANTES del código | Commit separado con tests en rojo | ✅ |
| Cobertura `lsp_auth`, `lsp_audit` | 14 + 9 tests con `--cov` ≥ 90% | ✅ |
| Cobertura `lsp_core` | 5 + landmarks + errores ≥ 96% | ✅ |
| Cero fallos en la suite | 0 FAIL, 0 ERROR | ✅ |
| Tests de integración | `tests/test_integracion.py` — 3 tests E2E | ✅ |
| Tests de carga / estrés | `qa/benchmark.py`, `qa/fps_test.py`, `qa/stress_test.py` | ✅ |
| Tests de video | `tests/test_video.py` — 11 tests | ✅ |
| Tests de seguridad | `tests/test_seguridad.py` — 20 tests | ✅ |
| Tests de ética IA | `tests/test_etica.py` — 15 tests | ✅ |
| Tests de sistema | `test_sistema.py` — 18 tests (assertions reales) | ✅ |

**Total tests automatizados: 49+ tests (tests/) + 18 (test_sistema.py) = 67+ en total**

### Seguridad (DevSecOps) — ✅ CUMPLE

| Criterio | Estado |
|---|---|
| Sin credenciales en código | ✅ `test_seguridad.py::test_no_credenciales` |
| Tokens HMAC-SHA256 | ✅ 14 tests de firma y expiración |
| Rate limiting anti-fuerza-bruta | ✅ `MAX_INTENTOS=5`, `BLOQUEO_SEGUNDOS=300` |
| Integridad del modelo PKL | ✅ `calcular_hash_modelo` + `verificar_integridad_modelo` |
| Log de auditoría sin PII | ✅ SHA-256[:8], 9 tests |
| Trazas ocultas en producción | ✅ `showErrorDetails = false` |
| XSRF activo | ✅ `enableXsrfProtection = true` |
| Docker non-root user | ✅ `USER lspuser` (UID 1001) |
| `.dockerignore` configurado | ✅ Excluye `data/`, `.git`, `secrets.toml` |
| `trivy.yaml` configurado | ✅ Escaneo CRITICAL+HIGH+MEDIUM |

### Accesibilidad (WCAG 2.1 AA) — ✅ CUMPLE

| Criterio | Estado |
|---|---|
| Contraste texto ≥ 4.5:1 | ✅ `#6b6b6b`, `#767676` verificados |
| `aria-live="polite"` en resultado | ✅ `render_resultado` |
| `role="progressbar"` + aria-valuenow | ✅ Barra de confianza |
| Regiones semánticas `banner`/`contentinfo` | ✅ `render_topbar`/`render_footer` |
| Skip-nav funcional (WCAG 2.4.1) | ✅ `render_skip_nav` |
| Emojis con `aria-hidden` | ✅ Pipeline y topbar |
| `focus-visible` para teclado | ✅ CSS en `render_estilos` |
| `lang="es"` en documento | ✅ Script inyectado |
| `aria-label` únicos por paso | ✅ `render_pipeline_explicado` |

### IA Ética (XAI) — ✅ CUMPLE

| Criterio | Estado |
|---|---|
| Explicabilidad del pipeline en UI | ✅ Expander con tabla de confianza |
| Sesgos documentados | ✅ `IA_ETICA.md` + sección en UI |
| Equidad por clase | ✅ `tests/test_etica.py::test_todas_las_clases` |
| Calibración de confianza | ✅ `tests/test_etica.py::test_predict_proba_suma_uno` |
| Privacidad de landmarks | ✅ `tests/test_etica.py::test_log_no_almacena_landmarks` |

---

## Cobertura de Historias de Usuario

| Sprint | HUs completadas | SP completados | % |
|--------|----------------|---------------|---|
| Sprint 1 | 7/7 | 36/36 SP | 100% |
| Sprint 2 | 10/10 | 57/57 SP | 100% |
| Sprint 3 | 5/5 | 24/24 SP | 100% |
| Sprint Reingeniería | 13 tareas TR | 20/20 SP | 100% |
| **Total** | **22/22 HUs** | **137/137 SP** | **100%** |

---

## Deuda Técnica Pendiente (v1.1+)

| Item | Tipo | Prioridad |
|------|------|-----------|
| Logout explícito (botón de cerrar sesión) | Feature | Media |
| GitHub Actions CI/CD con `trivy` y `pytest` | Infraestructura | Media |
| Log de auditoría persistente (SQLite) | Mejora | Media |
| Soporte letras dinámicas J y Z (LSTM) | Feature IA | Alta |
| Dataset con diversidad demográfica | IA Ética | Alta |

> La deuda técnica no bloquea la entrega del Capstone v1.0. Los 22 criterios DoD están satisfechos.

---

## Firmas de Aceptación

| Rol | Nombre | Estado |
|-----|--------|--------|
| Lead Developer / Scrum Master | Rodriguez Chacara, Oscar Daniel | ✅ |
| QA Lead | Rodriguez Chacara, Oscar Daniel | ✅ |
| Docente evaluador | *Pendiente de revisión* | ⏳ |

---

## Historial de Versiones

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0 | 2026-06-10 | Versión inicial — TDD, DevSecOps, WCAG 2.1 AA, privacidad |
| 1.1 | 2026-06-10 | HU-22 (Carga/Estrés) · CA-13.6 (sanitización) · CA-21.4 (Manual y Lecciones) |
| 1.2 | 2026-06-12 | Rate limiting, SHA-256 PKL, tests de video/seguridad/ética |
| 1.3 | 2026-06-13 | Fusión con DoD.md · src/ restructuring · Docker non-root · trivy.yaml · plantilla UAT · INCIDENTES.md |
| 2.0 | 2026-06-13 | **CIERRE DE PROYECTO** — Sprint Reingeniería completado, 137/137 SP, 22/22 HUs, 67+ tests, todos los criterios DoD satisfechos |
