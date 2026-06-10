# Fase 15 — Análisis de Seguridad

Análisis del frontend/backend web (Streamlit) del Traductor LSP.

## Contexto

La app **no es un backend HTTP tradicional** (no hay Flask/FastAPI, ni rutas, ni
base de datos, ni formularios de texto libre). Es una app **Streamlit** que:
- Recibe video de la cámara del usuario vía **WebRTC** (peer-to-peer cifrado, DTLS-SRTP).
- Procesa frames en memoria y devuelve la letra. **No almacena imágenes**.
- No tiene login, ni cookies de sesión personalizadas, ni almacenamiento de datos del usuario.

## Vectores evaluados

| Riesgo | Estado | Justificación |
|---|---|---|
| **XSS** | ✅ Bajo | Se usa `unsafe_allow_html=True`, pero solo se inyectan datos NO controlados por el usuario (la letra predicha — una sola letra a-z — y un número). No hay texto de usuario reflejado en el HTML. |
| **Inyección SQL** | ✅ N/A | No hay base de datos ni consultas. |
| **CSRF** | ✅ Bajo | No hay endpoints que muten estado del servidor con credenciales; Streamlit gestiona el ciclo de request. |
| **Inputs inválidos** | ✅ Controlado | `lsp_core.predecir()` valida el vector (42 valores finitos) y lanza `ValueError`; cubierto por pruebas. |
| **Sanitización** | ✅ OK | El único "input" es el frame de cámara (binario), procesado por OpenCV/MediaPipe. |
| **Errores expuestos** | ⚠️ Medio | Streamlit puede mostrar trazas en pantalla. En producción conviene ocultarlas. |
| **Secretos en el repo** | ✅ OK | No hay claves API ni credenciales en el código. |
| **Permiso de cámara** | ✅ OK | Lo gestiona el navegador; el usuario debe autorizar explícitamente. |

## Recomendaciones

1. **No agregar `st.file_uploader`** sin validar tipo/tamaño/MIME si en el futuro se sube imágenes.
2. Mantener `unsafe_allow_html` **solo** con datos generados por el sistema (nunca con texto escrito por el usuario).
3. En `.streamlit/config.toml` (producción) considerar `client.showErrorDetails = false` para no exponer trazas.
4. No subir `modelo.pkl` desde fuentes no confiables: un pickle malicioso puede ejecutar código al cargarse. Entrenar siempre con `entrenar_modelo.py`/`entrenar_desde_csv.py` propios.
5. Mantener dependencias actualizadas (revisar con `pip list --outdated`).

## Conclusión

La superficie de ataque es **mínima** por diseño (sin BD, sin auth, sin datos
persistentes, procesamiento efímero en memoria). El riesgo principal a vigilar es
la **deserialización de `modelo.pkl`**: solo cargar modelos generados por el equipo.
