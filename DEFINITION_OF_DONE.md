# Definition of Done — LSP Vision AI
## Universidad Privada del Norte · Capstone Project Sistemas 2026

Todo trabajo se considera **"Done"** cuando cumple la totalidad de los siguientes criterios antes de marcarse como completado en el tablero Scrum.

---

## ✅ Calidad de Código

| Criterio | Herramienta | Umbral |
|---|---|---|
| Sin errores de estilo | `flake8` | 0 errores (max-line-length: 120) |
| Calidad de código | `pylint` | Score ≥ 7.5/10 por módulo |
| Formato consistente | `black` | Sin diferencias al ejecutar `black --check` |
| Docstrings en funciones públicas | `pydoc` / revisión manual | 100% de funciones públicas documentadas con Args/Returns/Raises |
| Principio de responsabilidad única | Revisión de par | Cada módulo tiene una sola razón para cambiar |

---

## ✅ Pruebas (TDD)

| Criterio | Evidencia requerida |
|---|---|
| Tests escritos ANTES del código | Commit separado con tests en estado FAIL (rojo) |
| Cobertura de nuevos módulos | `pytest --cov` ≥ 90% para `lsp_auth`, `lsp_audit` |
| Cobertura del núcleo | `pytest --cov=lsp_core` ≥ 96% mantenida |
| Cero fallos en la suite | `pytest tests/ -v` retorna 0 FAIL y 0 ERROR en el entorno de referencia |
| Pruebas de integración | Al menos 1 test de flujo end-to-end por Historia de Usuario |
| Pruebas de carga / estrés | `qa/benchmark.py` sin etapa > 200 ms · `qa/fps_test.py` ≥ 24 FPS en 60 s · sesión de 300 s sin memory leak (HU-22) |

---

## ✅ Seguridad (DevSecOps)

| Criterio | Verificación |
|---|---|
| Sin credenciales en código fuente | `git log --all -S "password"` no devuelve coincidencias en texto plano |
| Tokens de sesión con firma HMAC | `lsp_auth.verificar_token()` rechaza tokens manipulados (test incluido) |
| Log de auditoría sin datos personales | Ningún campo contiene IP, user-agent ni nombre de usuario |
| Trazas de error ocultas en producción | `.streamlit/config.toml` contiene `showErrorDetails = false` |
| Protección XSRF activa | `.streamlit/config.toml` contiene `enableXsrfProtection = true` |
| Dependencias actualizadas | `pip list --outdated` revisado; vulnerabilidades conocidas atendidas |
| Modelo pkl de fuente confiable | El archivo `modelo.pkl` es generado localmente por `entrenar_modelo.py` |

---

## ✅ Accesibilidad (WCAG 2.1 — Nivel AA)

| Criterio | Verificación |
|---|---|
| Contraste de texto ≥ 4.5:1 | Chrome DevTools → Accessibility → sin fallos AA de contraste |
| Elemento de resultado con `aria-live="polite"` | Presente en el HTML del panel de resultado |
| Barra de confianza con `role="progressbar"` + aria-valuenow | Presente en el HTML generado |
| Regiones semánticas: `role="banner"` y `role="contentinfo"` | Verificar en DevTools → Elements |
| Enlace skip-nav funcional (WCAG 2.4.1) | Visible al presionar Tab desde el inicio de la página |
| Emojis decorativos con `aria-hidden="true"` | Verificar en el HTML del pipeline |
| Navegación por teclado hasta botón START | Tab desde skip-nav llega al control de cámara |

---

## ✅ Privacidad y Protección de Datos (GDPR Art. 25)

| Criterio | Estado |
|---|---|
| Frames de video NO se persisten a disco | Procesamiento en memoria únicamente — verificado en `lsp_video.py` |
| Vector de 42 landmarks NO se almacena | Solo se usa para predicción inmediata y se descarta |
| IDs de sesión en audit log son hash truncado | SHA-256[:8] del token, no reversible a identidad |
| En Streamlit Cloud el log es efímero | Documentado en `SEGURIDAD.md` como comportamiento esperado |

---

## ✅ Documentación

| Criterio | Archivo |
|---|---|
| Historia de Usuario con AC actualizados | `HISTORIAS_USUARIO.md` |
| Criterios de este DoD satisfechos | Este archivo (`DEFINITION_OF_DONE.md`) |
| Guía de instalación y ejecución vigente | `README.md` |
| Análisis de seguridad actualizado | `SEGURIDAD.md` |
| Guía de calidad y pruebas | `GUIA_QA.md` |
| Manual de Usuario Preliminar | Describe inicio de sesión, uso del traductor, confianza, historial y dashboard (HU-21 CA-21.4) |
| Registro de Lecciones Aprendidas | Documenta decisiones técnicas, obstáculos y mejoras identificadas (HU-21 CA-21.4) |

---

## ✅ Revisión de Par

| Criterio | Evidencia |
|---|---|
| Pull Request aprobado | Al menos 1 revisión de otro integrante del equipo |
| Checklist manual ejecutado | Verificado en Chrome + Firefox (o Chromium en Streamlit Cloud) |
| Sin comentarios de revisión pendientes | Todos los hilos resueltos antes de mergear |

---

## 📋 Cobertura de Historias de Usuario

| HU | Descripción | Criterios DoD aplicables |
|---|---|---|
| HU-01 | Definición de requerimientos y alcance | Documentación |
| HU-02 | Arquitectura modular | Documentación, Revisión de par |
| HU-03 | Entorno de desarrollo y repositorio | Código, Documentación |
| HU-04 | Recolección inicial del dataset | Documentación, Revisión de par |
| HU-05 | Dataset completo LSP | Documentación |
| HU-06 | Extracción de landmarks y preprocesamiento | Código, Pruebas, Documentación |
| HU-07 | Entrenamiento y validación del SVM | Código, Pruebas, Documentación |
| HU-08 | Captura de video en tiempo real | Código, Pruebas, Documentación |
| HU-09 | Detección de manos con MediaPipe | Código, Pruebas, Documentación |
| HU-10 | Reconocimiento y traducción en tiempo real | Todos los criterios |
| HU-11 | Historial de señas y construcción de texto | Código, Pruebas, Documentación |
| HU-12 | Integración completa de módulos | Código, Pruebas, Revisión de par |
| HU-13 | Acceso controlado (autenticación) | Código, Pruebas (TDD), Seguridad |
| HU-14 | Registro anónimo de accesos (auditoría) | Código, Pruebas (TDD), Privacidad |
| HU-15 | Interfaz accesible WCAG 2.1 AA | Código, Accesibilidad, Revisión de par |
| HU-16 | Explicabilidad del sistema de IA | Código, Documentación |
| HU-17 | Dashboard de métricas de calidad | Código, Pruebas (QA), Documentación |
| HU-18 | Pruebas unitarias automatizadas | Pruebas (TDD), Documentación |
| HU-19 | Pruebas de aceptación con usuarios | Revisión de par, Documentación |
| HU-20 | Validación de privacidad y datos | Seguridad, Privacidad, Documentación |
| HU-21 | Despliegue del sistema | Documentación, Revisión de par |
| HU-22 | Pruebas de rendimiento, carga y estrés | Pruebas (QA), Documentación |

> La referencia completa de cada historia (rol, beneficio, criterios Gherkin y tests) está en `HISTORIAS_USUARIO.md`.

---

## 📋 Historial de Versiones de este DoD

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0 | 2026-06-10 | Versión inicial — incluye TDD, DevSecOps, WCAG 2.1 AA, privacidad |
| 1.1 | 2026-06-10 | Tabla de cobertura actualizada para las 21 HUs definitivas |
| 1.2 | 2026-06-10 | HU-22 (Pruebas de Carga/Estrés) · CA-13.6 (sanitización) · CA-21.4 (Manual de Usuario) · Manual de Usuario y Lecciones Aprendidas como criterios de documentación |
