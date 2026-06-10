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
| **CSRF** | ✅ Implementado | `enableXsrfProtection = true` activo en `.streamlit/config.toml`. |
| **Inputs inválidos** | ✅ Controlado | `lsp_core.predecir()` valida el vector (42 valores finitos) y lanza `ValueError`; cubierto por pruebas. |
| **Sanitización** | ✅ OK | El único "input" es el frame de cámara (binario), procesado por OpenCV/MediaPipe. |
| **Errores expuestos** | ✅ Implementado | `showErrorDetails = false` activo en `.streamlit/config.toml` desde v1.1. |
| **Secretos en el repo** | ✅ OK | No hay claves API ni credenciales en el código. `secrets.toml` en `.gitignore`. |
| **Permiso de cámara** | ✅ OK | Lo gestiona el navegador; el usuario debe autorizar explícitamente. |
| **Autenticación** | ✅ Implementado | Módulo `lsp_auth.py`: tokens HMAC-SHA256 con expiración de 60 min (v1.1). |
| **Auditoría** | ✅ Implementado | Módulo `lsp_audit.py`: log JSON Lines sin datos personales (v1.1). |

## Recomendaciones (actualizadas v1.1)

1. **No agregar `st.file_uploader`** sin validar tipo/tamaño/MIME si en el futuro se sube imágenes.
2. Mantener `unsafe_allow_html` **solo** con datos generados por el sistema (nunca con texto escrito por el usuario).
3. ~~En producción considerar `client.showErrorDetails = false`~~ → **Implementado** en `.streamlit/config.toml`.
4. No subir `modelo.pkl` desde fuentes no confiables: un pickle malicioso puede ejecutar código al cargarse. Entrenar siempre con `entrenar_modelo.py`/`entrenar_desde_csv.py` propios.
5. Mantener dependencias actualizadas (revisar con `pip list --outdated`).
6. La clave de acceso debe almacenarse como hash en `.streamlit/secrets.toml` (no subir al repo). Ver `lsp_auth.hash_password()` para generar el hash inicial.

---

## Sección de Privacidad y Protección de Datos (GDPR Art. 25)

**Privacidad por diseño** — implementada desde la arquitectura del sistema:

### Datos que se procesan

| Dato | Persistencia | Justificación |
|---|---|---|
| Frames de video de la cámara | **NO** — solo en memoria RAM | Procesados por MediaPipe y descartados inmediatamente |
| Vector de 42 landmarks | **NO** — solo en memoria | Usado para predicción y descartado; nunca escrito a disco |
| Token de sesión | **Solo en `st.session_state`** | En memoria del proceso Streamlit; expira en 60 min |
| Log de auditoría (`audit_log.jsonl`) | **Sí, en disco local** | Solo timestamps, eventos y hashes anónimos de 8 chars |

### ID de sesión en el log de auditoría

El campo `sesion` en cada entrada del log es `SHA-256[:8]` del token de sesión.
- **No reversible** a identidad del usuario.
- **No vinculable** a IP, navegador ni nombre.
- Permite correlacionar eventos de una misma sesión sin identificar a la persona.

### Comportamiento en Streamlit Cloud

El filesystem de Streamlit Cloud es **efímero**: al reiniciar el servidor (automático tras 7 días de inactividad o deploys), `audit_log.jsonl` se borra. Este comportamiento es **correcto y esperado** para un proyecto académico de demostración.

---

## Conclusión (v1.1)

La superficie de ataque es **mínima** por diseño (sin BD, sin datos de usuario
persistentes, procesamiento efímero en memoria). Los controles de seguridad de la
versión 1.1 implementan: autenticación HMAC, trazas ocultas en producción, XSRF activo
y auditoría anónima. El riesgo principal a vigilar sigue siendo la **deserialización
de `modelo.pkl`**: solo cargar modelos generados por el equipo.

| Versión | Fecha | Cambios de seguridad |
|---|---|---|
| 1.0 | 2026-06-09 | Análisis inicial — sin controles implementados |
| 1.1 | 2026-06-10 | Auth HMAC (`lsp_auth`), audit log (`lsp_audit`), `showErrorDetails=false`, XSRF, privacidad GDPR documentada |
