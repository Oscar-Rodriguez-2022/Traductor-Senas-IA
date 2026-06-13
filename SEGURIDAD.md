# Fase 15 — Análisis de Seguridad

Análisis del frontend/backend web (Streamlit) del Traductor LSP.

## Contexto

La app **no es un backend HTTP tradicional** (no hay Flask/FastAPI, ni rutas, ni
base de datos, ni formularios de texto libre). Es una app **Streamlit** que:
- Recibe video de la cámara del usuario vía **WebRTC** (peer-to-peer cifrado, DTLS-SRTP).
- Procesa frames en memoria y devuelve la letra. **No almacena imágenes**.
- No tiene login, ni cookies de sesión personalizadas, ni almacenamiento de datos del usuario.

## Vectores evaluados (Plan de Seguridad Integral — tres capas)

### Capa de Aplicación

| Riesgo | Estado | Justificación |
|---|---|---|
| **XSS** | ✅ Bajo | `unsafe_allow_html=True` solo inyecta datos del sistema (letra a-z, número). Nunca texto libre del usuario. Verificado en `tests/test_seguridad.py::TestSanitizacionInputs`. |
| **Inyección SQL** | ✅ N/A | No hay base de datos ni consultas SQL. |
| **Inyección en hash** | ✅ Controlado | `hash_password()` trata cualquier input como texto plano (PBKDF2-HMAC-SHA256); inyecciones son hasheadas, no ejecutadas. |
| **CSRF** | ✅ Implementado | `enableXsrfProtection = true` en `.streamlit/config.toml`. |
| **Inputs inválidos** | ✅ Controlado | `lsp_core.predecir()` valida 42 valores finitos y lanza `ValueError`. |
| **Fuerza bruta (brute-force)** | ✅ Implementado v1.2 | Rate limiting: tras `MAX_INTENTOS=5` fallidos consecutivos, `lsp_auth.generar_token_sesion()` retorna `None` durante `BLOQUEO_SEGUNDOS=300` (5 min). Auto-reset en login exitoso. |
| **Errores expuestos** | ✅ Implementado | `showErrorDetails = false` en `.streamlit/config.toml`. |
| **Secretos en el repo** | ✅ OK | Sin claves en código. `secrets.toml` en `.gitignore`. Detectado por `tests/test_seguridad.py::test_no_credenciales_en_texto_plano`. |

### Capa de Almacenamiento

| Riesgo | Estado | Justificación |
|---|---|---|
| **Deserialización maliciosa (PKL)** | ✅ Implementado v1.2 | `lsp_core.calcular_hash_modelo()` y `verificar_integridad_modelo()` calculan SHA-256 del modelo. Verificar antes de cargar modelos de fuentes externas. |
| **Datos personales en audit log** | ✅ OK | IDs de sesión son SHA-256[:8], no reversibles. Sin IP, user-agent ni nombre. Verificado en `tests/test_seguridad.py::TestAuditLogAnonimato`. |
| **Landmarks biométricos en log** | ✅ OK | El log solo registra el evento y detalle textual; nunca vectores de 42 floats. |
| **Autenticación** | ✅ Implementado | Tokens HMAC-SHA256 con expiración de 60 min. PBKDF2 260k iteraciones. |
| **Auditoría** | ✅ Implementado | Log JSON Lines anónimo, purga automática 7 días. |

### Capa de Infraestructura

| Riesgo | Estado | Justificación |
|---|---|---|
| **Permiso de cámara** | ✅ OK | Controlado por el navegador; el usuario debe autorizar explícitamente. |
| **Frames persistidos** | ✅ OK | Procesamiento en memoria únicamente. Verificado en `tests/test_seguridad.py::TestPrivacidadPorDiseno`. |
| **Configuración insegura** | ✅ OK | `showErrorDetails=false`, `enableXsrfProtection=true`. Verificado en `tests/test_seguridad.py::TestConfiguracionStreamlit`. |

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

## Conclusión (v1.2)

La superficie de ataque es **mínima** por diseño (sin BD, sin datos de usuario
persistentes, procesamiento efímero en memoria). Los controles de la v1.2 añaden:
rate limiting anti-fuerza-bruta y verificación SHA-256 del modelo PKL.

La suite `tests/test_seguridad.py` cubre las tres capas con 20 tests automatizados.

| Versión | Fecha | Cambios de seguridad |
|---|---|---|
| 1.0 | 2026-06-09 | Análisis inicial — sin controles implementados |
| 1.1 | 2026-06-10 | Auth HMAC (`lsp_auth`), audit log (`lsp_audit`), `showErrorDetails=false`, XSRF, privacidad GDPR documentada |
| 1.2 | 2026-06-12 | Rate limiting anti-brute-force (`MAX_INTENTOS=5`, `BLOQUEO_SEGUNDOS=300`); verificación de integridad `modelo.pkl` SHA-256 (`calcular_hash_modelo`, `verificar_integridad_modelo`); suite `tests/test_seguridad.py` con 20 tests por capas |
