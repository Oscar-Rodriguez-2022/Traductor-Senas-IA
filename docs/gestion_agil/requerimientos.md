# Documento de Requerimientos — LSP Vision AI
## Universidad Privada del Norte · Capstone Project Sistemas 2026
### Autor: Rodriguez Chacara, Oscar Daniel
### Versión: 1.1 · Fecha: 2026-06-13

> Este documento cumple con **CA-01.1** (≥15 RF y ≥15 RNF, cada uno con código,
> tipo, nombre y descripción) y **CA-01.2** (revisado y validado por el líder técnico).

---

## Objetivo del Sistema

Desarrollar un sistema web de visión artificial capaz de reconocer en tiempo real
señas del alfabeto manual de la Lengua de Señas Peruana (LSP) usando MediaPipe y
un clasificador SVM, con una interfaz accesible (WCAG 2.1 AA), controles de
seguridad (DevSecOps) y principios de IA ética.

---

## Requerimientos Funcionales (RF)

| Código | Nombre | Descripción |
|--------|--------|-------------|
| **RF-01** | Captura de video en tiempo real | El sistema debe iniciar automáticamente la cámara web del usuario mediante WebRTC al cargar la página, mostrando el flujo de video sin configuración manual. |
| **RF-02** | Detección de manos con MediaPipe | El sistema debe detectar la mano del usuario en cada frame usando MediaPipe Hands y extraer los 21 puntos anatómicos (landmarks), devolviendo un vector de 42 coordenadas normalizadas. |
| **RF-03** | Clasificación de señas con SVM | El sistema debe clasificar el vector de landmarks mediante un clasificador SVM entrenado, devolviendo la letra predicha (a–z) y su nivel de confianza (0–100%). |
| **RF-04** | Visualización del resultado con confianza | El sistema debe mostrar la letra detectada con un indicador de confianza: borde rojo (#E30613) cuando la confianza es ≥60%, borde amarillo (#f0a500) cuando es <60%. |
| **RF-05** | Superposición del esqueleto de mano | El sistema debe dibujar el esqueleto de landmarks sobre el frame de video en tiempo real para dar retroalimentación visual al usuario. |
| **RF-06** | Historial de señas y construcción de texto | El sistema debe acumular las señas reconocidas con confianza superior al umbral configurado en un historial de texto, mostrándolo en tiempo real en el panel principal. |
| **RF-07** | Control del historial | El usuario debe poder limpiar el historial de texto sin detener la captura de video, y configurar el umbral mínimo de confianza para aceptar una predicción. |
| **RF-08** | Autenticación de sesión académica | El sistema debe requerir una clave de acceso antes de mostrar el traductor. La sesión se basa en tokens HMAC-SHA256 con expiración de 60 minutos. |
| **RF-09** | Registro anónimo de accesos (auditoría) | El sistema debe registrar eventos de acceso (LOGIN_OK, LOGIN_FAIL, PAGINA_VISITADA, etc.) en un log JSON Lines sin almacenar datos personales identificables. |
| **RF-10** | Dashboard de métricas de calidad | El sistema debe exponer una página de métricas que muestre accuracy, precision, recall, F1-score, FPS sostenidos, latencias por etapa, matriz de confusión y log de auditoría. |
| **RF-11** | Entrenamiento del modelo desde dataset | El sistema debe permitir entrenar el clasificador SVM a partir de imágenes PNG organizadas en `data/<letra>/`, guardando el modelo resultante como `modelo.pkl`. |
| **RF-12** | Construcción colaborativa del dataset | El sistema debe permitir que múltiples integrantes del equipo exporten sus landmarks a CSV y que el modelo se entrene desde esos archivos combinados. |
| **RF-13** | Aumento de datos (data augmentation) | El sistema debe aplicar transformaciones geométricas (rotaciones, escala, ruido) a los vectores de landmarks para multiplicar el dataset × 16 sin capturar imágenes adicionales. |
| **RF-14** | Explicabilidad del pipeline de IA | La interfaz debe contener una sección que explique al usuario cómo funciona el sistema (captura → detección → extracción → clasificación → resultado) con indicadores visuales accesibles. `src/lsp_core.py` expone `explicar_prediccion()` (dict con letra, confianza y top-5 alternativas), `nombres_landmarks()` (mapa anatómico de 21 puntos en español) y `sesgos_conocidos()` (5 limitaciones documentadas del modelo) como API de XAI verificable por `tests/test_etica.py::TestXAI`. |
| **RF-15** | Captura colaborativa del dataset | El script de captura (`scripts/capturar_dataset.py`) debe evitar sobreescribir las imágenes de otros integrantes usando índices autoincrementales, permitiendo que todos contribuyan a la misma carpeta. |

---

## Requerimientos No Funcionales (RNF)

| Código | Nombre | Descripción |
|--------|--------|-------------|
| **RNF-01** | Rendimiento — FPS mínimo | El sistema debe mantener una tasa mínima de **24 FPS** sostenidos durante al menos 60 segundos, validado por `qa/fps_test.py`. |
| **RNF-02** | Latencia extremo a extremo | El tiempo entre la realización de la seña y la visualización del resultado en el panel debe ser inferior a **2 segundos** en condiciones normales de red y hardware. |
| **RNF-03** | Latencia por etapa de pipeline | Ninguna etapa del pipeline (captura, detección, extracción, clasificación, renderizado) debe superar **200 ms**, validado por `qa/benchmark.py`. |
| **RNF-04** | Exactitud del modelo | El clasificador SVM debe alcanzar una exactitud mínima de **85%** sobre el conjunto de prueba, validado por `qa/evaluate.py`. |
| **RNF-05** | Seguridad — Autenticación fuerte | Los tokens de sesión deben usar firma HMAC-SHA256. Las contraseñas deben hashearse con PBKDF2-HMAC-SHA256 con mínimo 260 000 iteraciones (OWASP 2023). Rate limiting anti-fuerza-bruta: bloqueo automático tras `MAX_INTENTOS=5` intentos fallidos consecutivos por `BLOQUEO_SEGUNDOS=300` s. No se almacenan credenciales en el repositorio; el pre-commit hook (`scripts/hooks/pre-commit`, 3 capas de detección) bloquea secretos antes de cada commit. |
| **RNF-06** | Privacidad por diseño (GDPR Art. 25) | Ningún frame de video ni vector de landmarks debe persistirse a disco. Los IDs de sesión en el log de auditoría deben ser hash SHA-256[:8] no reversibles. |
| **RNF-07** | Accesibilidad WCAG 2.1 AA | La interfaz debe cumplir nivel AA: contraste ≥4.5:1, aria-live en el resultado, role="progressbar" con aria-valuenow, skip-nav (WCAG 2.4.1), emojis decorativos con aria-hidden. |
| **RNF-08** | Disponibilidad y despliegue | El sistema debe poder desplegarse en Streamlit Cloud y como contenedor Docker sin cambios de código, usando únicamente `requirements.txt` y `packages.txt`. |
| **RNF-09** | Portabilidad | El sistema debe funcionar en Python 3.12 en Windows, Linux y macOS, con soporte en entornos sin GPU mediante MediaPipe CPU-mode. (MediaPipe 0.10.21 no es compatible con Python 3.13; versión mínima soportada y probada: 3.12.) |
| **RNF-10** | Mantenibilidad — Arquitectura modular | El código debe distribuirse en módulos con responsabilidad única (`lsp_core`, `lsp_auth`, `lsp_audit`, `lsp_ui`, `lsp_video`) sin dependencias circulares. |
| **RNF-11** | Calidad de código | Cada módulo debe obtener score Pylint ≥7.5/10. El código debe estar formateado con Black (max-line-length: 120). Flake8 debe reportar 0 errores. |
| **RNF-12** | Cobertura de pruebas (TDD) | Los módulos `lsp_auth` y `lsp_audit` deben tener cobertura ≥90%. El módulo `lsp_core` debe tener cobertura ≥96%, validado por `pytest --cov`. |
| **RNF-13** | Confiabilidad — Sin fugas de memoria | El sistema no debe presentar fugas de memoria en sesiones de 300 segundos, validado por `qa/stress_test.py` con monitoreo de RAM. |
| **RNF-14** | Uso de recursos | El consumo de RAM durante operación normal no debe superar **512 MB**. El uso de CPU no debe superar el **80%** en estado estacionario, validado por `qa/recursos.py`. |
| **RNF-15** | Documentación técnica completa | El 100% de las funciones públicas deben tener docstrings con campos Args, Returns y (cuando aplica) Raises. Los artefactos académicos (HUs, DoD, Manual, Lecciones) deben mantenerse actualizados con cada sprint. |

---

## Trazabilidad RF/RNF → Historias de Usuario

| Requerimiento | Historia de Usuario |
|---------------|---------------------|
| RF-01 | HU-08 — Captura de video en tiempo real |
| RF-02 | HU-09 — Detección de manos con MediaPipe |
| RF-03 | HU-10 — Reconocimiento y traducción en tiempo real |
| RF-04 | HU-10 — Indicador de confianza |
| RF-05 | HU-09 — Visualización de landmarks |
| RF-06 | HU-11 — Historial de señas y construcción de texto |
| RF-07 | HU-11 — Control del historial |
| RF-08 | HU-13 — Acceso controlado |
| RF-09 | HU-14 — Registro anónimo de accesos |
| RF-10 | HU-17 — Dashboard de métricas de calidad |
| RF-11 | HU-07 — Entrenamiento y validación del SVM |
| RF-12 | HU-05 — Dataset colaborativo |
| RF-13 | HU-05 — Aumento de datos |
| RF-14 | HU-16 — Explicabilidad del sistema de IA |
| RF-15 | HU-04 — Recolección inicial del dataset |
| RNF-01 | HU-22 — Pruebas de rendimiento, carga y estrés |
| RNF-02 | HU-10 CA-10.2 — Tiempo de respuesta |
| RNF-03 | HU-22 — Benchmark por etapa |
| RNF-04 | HU-07 CA-07.2 — Precisión mínima 85% |
| RNF-05 | HU-13 — Seguridad DevSecOps |
| RNF-06 | HU-14, HU-20 — Privacidad GDPR Art. 25 |
| RNF-07 | HU-15 — Interfaz accesible WCAG 2.1 AA |
| RNF-08 | HU-21 — Despliegue del sistema |
| RNF-09 | HU-03 — Entorno de desarrollo |
| RNF-10 | HU-02 — Arquitectura modular |
| RNF-11 | HU-18 — Pruebas unitarias automatizadas |
| RNF-12 | HU-18 — Cobertura TDD |
| RNF-13 | HU-22 — Pruebas de estrés |
| RNF-14 | HU-22 — Uso de recursos |
| RNF-15 | HU-01 — Documentación técnica |

---

## Historial de Versiones

| Versión | Fecha | Cambio |
|---------|-------|--------|
| 1.0 | 2026-06-12 | Versión inicial — 15 RF + 15 RNF con trazabilidad HU |
| 1.1 | 2026-06-13 | RF-14: funciones XAI (`explicar_prediccion`, `nombres_landmarks`, `sesgos_conocidos`); RF-15: `A.py` → `scripts/capturar_dataset.py`; RNF-05: rate limiting + pre-commit hook; RNF-09: Python 3.12 (no 3.13) |
