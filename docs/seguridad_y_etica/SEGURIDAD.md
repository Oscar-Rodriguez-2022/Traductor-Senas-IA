# Plan de Seguridad Integral — LSP Vision AI
## Capstone Project Sistemas 2026 · Universidad Privada del Norte
### Responsable: Rodriguez Chacara, Oscar Daniel
### Versión: 2.1 · Fecha: 2026-06-13

> Este documento describe el modelo de seguridad completo del sistema, organizado en
> tres capas: Aplicación, Almacenamiento e Infraestructura. Cumple con los requisitos
> de DevSecOps del Capstone y con GDPR Art. 25 (Privacidad por Diseño).

---

## Contexto del Sistema

**LSP Vision AI** no es un backend HTTP tradicional. Es una aplicación **Streamlit** que:
- Recibe video de la cámara del usuario vía **WebRTC** (peer-to-peer cifrado, DTLS-SRTP).
- Procesa frames en memoria RAM y los descarta inmediatamente — **no almacena imágenes**.
- Autentica usuarios con tokens HMAC-SHA256 propios de stdlib Python (sin JWT externo).
- Registra eventos en un log JSON Lines anónimo (sin IP, sin nombre, sin user-agent).
- Se despliega como aplicación web en Streamlit Cloud o HuggingFace Spaces con Docker.

La **superficie de ataque es mínima por diseño**: sin base de datos SQL, sin formularios de texto libre del usuario, sin almacenamiento de datos personales.

---

## Capa 1 — Aplicación

### 1.1 Autenticación y Gestión de Sesión

**Módulo:** `src/lsp_auth.py`

| Control | Implementación | Verificación |
|---------|---------------|-------------|
| **Hashing de contraseña** | PBKDF2-HMAC-SHA256 con 260 000 iteraciones y PEPPER constante. Cumple OWASP 2023 para almacenamiento de credenciales. | `test_auth.py::test_hash_password_*` |
| **Token de sesión** | Formato `timestamp.nonce.HMAC-SHA256`. Generado con `secrets.token_hex(16)` (CSPRNG). Expira a los 60 minutos. | `test_auth.py::test_generar_token_*` |
| **Verificación de token** | `hmac.compare_digest()` previene timing attacks. Rechaza tokens manipulados, malformados o expirados. | `test_auth.py::test_verificar_token_*` |
| **Rate limiting anti-fuerza-bruta** | Bloqueo automático tras `MAX_INTENTOS = 5` fallos consecutivos. Duración del bloqueo: `BLOQUEO_SEGUNDOS = 300` (5 min). `threading.Lock` para thread-safety. | `test_seguridad.py::TestRateLimiting` |
| **Protección timing attacks** | Comparación con `hmac.compare_digest()` en lugar de `==`. | `test_auth.py::test_firma_resiste_*` |

**Flujo de autenticación:**

```
Usuario → contraseña en texto plano
    ↓
lsp_auth.generar_token_sesion(pwd, hash_esperado)
    ↓ (PBKDF2-HMAC-SHA256)
¿Coincide el hash? → SÍ → Token "ts.nonce.firma" emitido → st.session_state["token"]
                  → NO → contador++ → ¿MAX_INTENTOS? → Bloqueo 300 s
```

### 1.2 Sanitización de Entradas

| Riesgo | Estado | Justificación |
|--------|--------|--------------|
| **XSS en formulario de login** | ✅ Controlado | `hash_password()` trata cualquier input como texto plano vía PBKDF2-HMAC-SHA256. Ningún input del usuario se renderiza como HTML. Verificado con 11 payloads OWASP Top 10. |
| **Inyección SQL** | ✅ N/A | No existe base de datos ni consultas SQL en el sistema. |
| **Inyección de comandos** | ✅ N/A | No hay ejecución de comandos del sistema a partir de input del usuario. |
| **Inyección en campo contraseña** | ✅ Controlado | Payloads `<script>`, `' OR '1'='1`, `\x00`, Unicode son tratados como texto plano por PBKDF2. Ninguno concede acceso. |
| **Inputs inválidos en predicción** | ✅ Controlado | `lsp_core.predecir()` valida 42 valores finitos antes de clasificar; lanza `ValueError` en caso de vector inválido. |
| **`unsafe_allow_html`** | ✅ Controlado | Solo inyecta datos generados por el sistema (letra a-z, número, CSS). Nunca texto libre del usuario. |

**Verificación:** `tests/test_seguridad.py::TestSanitizacionInputs` — 13 tests: 7 de acceso con payloads OWASP, 4 de hash con caracteres especiales/overflow, 2 de manipulación de token (timestamp y nonce).

### 1.3 Gestión de Errores

| Control | Configuración |
|---------|--------------|
| **Ocultar detalles de error** | `.streamlit/config.toml`: `showErrorDetails = false`. No expone trazas de pila al usuario. |
| **Protección XSRF** | `.streamlit/config.toml`: `enableXsrfProtection = true`. |
| **Manejo de cámara no disponible** | `src/lsp_video.py` maneja la ausencia de cámara sin crashear; muestra mensaje "Cámara no disponible". |
| **Manejo de modelo no cargado** | `src/app.py` verifica que `modelo.pkl` exista antes de instanciar `Traductor`. |

**Verificación:** `tests/test_seguridad.py::TestConfiguracionStreamlit` — 2 tests.

---

## Capa 2 — Almacenamiento

### 2.1 Autenticación y Tokens

| Dato | Almacenamiento | Duración |
|------|---------------|----------|
| Token de sesión | `st.session_state["token"]` (memoria del proceso) | 60 minutos |
| Hash de contraseña | `.streamlit/secrets.toml` (excluido de Git) | Permanente (configuración) |
| Contador de intentos | Memoria del proceso (`threading.Lock`) | Duración del proceso |

> **El hash de contraseña NUNCA debe almacenarse en texto plano en el código fuente.**
> Generar el hash con `lsp_auth.hash_password("mi_contraseña")` y almacenarlo en `secrets.toml`.

### 2.2 Log de Auditoría (GDPR Art. 25)

**Módulo:** `src/lsp_audit.py`

| Campo en el log | Tipo | Dato almacenado | PII |
|-----------------|------|----------------|-----|
| `ts` | Timestamp ISO 8601 | Momento del evento | ❌ No |
| `evento` | String | Tipo de evento (LOGIN, PAGINA_VISITADA) | ❌ No |
| `sesion` | SHA-256[:8] | Hash truncado del token de sesión | ❌ No — no reversible |
| `detalle` | String | Texto libre del evento (sin datos personales) | ❌ No |

**Datos que NUNCA aparecen en el log:**
- Dirección IP del usuario
- Nombre o identificador de usuario
- User-agent del navegador
- Contraseñas o hashes de contraseñas
- Vectores de landmarks (datos biométricos)
- Imágenes o capturas de pantalla

**Purga automática:** `lsp_audit.purgar_log_antiguo(dias=7)` elimina entradas con más de 7 días.

**Verificación:** `tests/test_seguridad.py::TestAuditLogAnonimato` (4 tests: IP, user-agent, token reversibility, distintas sesiones) + `tests/test_audit.py` (9 tests: campos, formato, purga, retención).

### 2.3 Integridad del Modelo SVM

**Riesgo:** Un archivo `modelo.pkl` malicioso puede ejecutar código arbitrario al ser cargado con `joblib.load()` (deserialización insegura).

| Control | Implementación |
|---------|---------------|
| **Cálculo de hash** | `lsp_core.calcular_hash_modelo(path)` → SHA-256 del archivo `.pkl` |
| **Verificación de integridad** | `lsp_core.verificar_integridad_modelo(path, hash_esperado)` → `hmac.compare_digest()` para comparación segura |
| **Procedimiento recomendado** | Calcular el hash después del entrenamiento; almacenarlo; verificar antes de cada despliegue |

**Verificación:** `tests/test_seguridad.py::TestIntegridadModelo` — 7 tests: cálculo hash, determinismo, detección de tampering, archivo inexistente, verificación correcta/incorrecta.

### 2.4 Frames y Landmarks

| Dato | Persistencia |
|------|-------------|
| Frames de video de la cámara | **NO** — procesados en RAM y descartados por el recolector de basura de Python |
| Vector de 42 coordenadas (landmarks) | **NO** — usado para predicción inmediata y descartado |
| Predicción (letra + confianza) | **NO** — solo se muestra en UI; no se escribe a disco |

**Verificación:** `tests/test_seguridad.py::TestPrivacidadPorDiseno` — 3 tests: frames no persistidos, sin credenciales en texto plano, audit log sin landmarks biométricos.

---

## Capa 3 — Infraestructura

### 3.1 Docker — Imagen de Producción

**Dockerfile:** imagen basada en `python:3.12-slim` con las siguientes medidas de seguridad:

| Medida | Configuración | Propósito |
|--------|--------------|-----------|
| **Usuario no-root** | `RUN adduser --uid 1001 lspuser` + `USER lspuser` | Limita el daño potencial si hay exploit en la app |
| **PYTHONDONTWRITEBYTECODE** | `ENV PYTHONDONTWRITEBYTECODE=1` | Evita archivos `.pyc` en la imagen |
| **PYTHONUNBUFFERED** | `ENV PYTHONUNBUFFERED=1` | Logs inmediatos (mejor trazabilidad) |
| **PYTHONPATH** | `ENV PYTHONPATH=/app/src` | Resuelve imports del src-layout |
| **Sin caché pip** | `pip install --no-cache-dir` | Reduce tamaño de imagen |
| **HEALTHCHECK** | `curl -f http://localhost:7860/_stcore/health` | Detecta si la app está caída |
| **Flags de seguridad Streamlit** | `CMD streamlit run ... --server.showErrorDetails=false --server.enableXsrfProtection=true` | Prioridad máxima sobre variables de entorno |

### 3.2 .dockerignore

El archivo `.dockerignore` excluye del contexto de build:
- `.git/` — historial Git no necesario en producción
- `.venv/` — entorno virtual local
- `data/` — dataset de entrenamiento (grande, no necesario en prod)
- `reportes/` — reportes QA locales
- `*.env`, `secrets.toml` — credenciales
- `__pycache__/`, `.pytest_cache/`, `htmlcov/` — artefactos de desarrollo

### 3.3 Escaneo de Vulnerabilidades

**Herramienta:** Trivy (configurado en `trivy.yaml`)

| Parámetro | Valor |
|-----------|-------|
| Severidades escaneadas | CRITICAL, HIGH, MEDIUM |
| Timeout | 10 minutos |
| Directorios excluidos | `.venv/`, `data/`, `reportes/` |
| Comando de ejecución | `trivy fs .` (antes de cada despliegue) |

**Procedimiento recomendado:**
```bash
# Escanear antes de construir la imagen Docker
trivy fs . --severity CRITICAL,HIGH,MEDIUM

# Escanear la imagen Docker construida
trivy image lsp-vision-ai:latest
```

### 3.4 WebRTC — Comunicación de Video

| Aspecto | Detalle |
|---------|---------|
| **Cifrado** | DTLS-SRTP (estándar WebRTC) — tráfico de video cifrado en tránsito |
| **Permiso de cámara** | Controlado por el navegador del usuario — el sistema no puede acceder a la cámara sin aprobación explícita |
| **STUN server** | `stun:stun.l.google.com:19302` — resuelve NAT básico |
| **TURN server** | `openrelay.metered.ca` (puertos 80, 443, 443/TCP) — resuelve NAT simétrico (redes corporativas/universitarias) |

### 3.5 Gestión de Secretos

| Secreto | Almacenamiento | En Git |
|---------|---------------|--------|
| Clave de acceso (hash) | `.streamlit/secrets.toml` | ❌ excluido por `.gitignore` |
| Credenciales TURN | `.streamlit/secrets.toml` | ❌ excluido por `.gitignore` |
| Cualquier API key | Variables de entorno del servidor | ❌ nunca en código |

**Regla absoluta:** ningún secreto en texto plano en el código fuente.

**Pre-commit hook anti-secretos (DT-20):** `scripts/hooks/pre-commit` — 87 líneas, 3 capas de detección:
1. **Nombres bloqueados:** archivos con nombres de credenciales (`.env`, `secrets.*`, `*_key.*`, etc.) no pueden incluirse en el commit.
2. **Patrones en el diff:** detección de `AKIA…` (AWS), `ghp_…` (GitHub PAT), `sk-…` (OpenAI), `password=`, `SECRET=` en el contenido del diff.
3. **Archivos de config:** escaneo de archivos `.toml`, `.yaml`, `.cfg` y `.ini` del staging area en busca de valores en texto plano.

Instalación en Windows: `scripts/setup_hooks.bat` copia el hook a `.git/hooks/pre-commit` y lo marca ejecutable.

**Verificación en tests:** `tests/test_seguridad.py::TestPrivacidadPorDiseno::test_no_credenciales_en_texto_plano_en_codigo` — escanea el repo completo en busca de patrones de secretos.

---

## Privacidad por Diseño (GDPR Art. 25)

### Datos procesados por el sistema

| Dato | ¿Se persiste? | Base legal de procesamiento |
|------|--------------|----------------------------|
| Frames de video (cámara web) | **No** — solo en RAM | Consentimiento implícito al iniciar WebRTC |
| Vector de 42 landmarks | **No** — solo en RAM | Procesamiento técnico para predicción |
| Token de sesión | Sí, en `st.session_state` (memoria proceso, 60 min) | Seguridad de la sesión |
| Log de auditoría anónimo | Sí, en `audit_log.jsonl` (7 días máximo) | Interés legítimo de seguridad operacional |

### ID de sesión anónimo

El campo `sesion` en el log es `SHA-256(token)[:8]`:
- **No es reversible** al token original (función one-way).
- **No vincula** a identidad, IP o nombre del usuario.
- Permite correlacionar eventos de una misma sesión para auditoría sin identificar a la persona.

### Comportamiento en Streamlit Cloud / HuggingFace Spaces

El filesystem es **efímero**: al reiniciar el servidor (automático tras inactividad o nuevo deploy), `audit_log.jsonl` se borra. Este comportamiento es **correcto y esperado** para un proyecto académico de demostración.

---

## Recomendaciones para Producción Avanzada (v2.0+)

1. **No agregar `st.file_uploader`** sin validar tipo MIME, tamaño y contenido si en el futuro se sube imágenes.
2. Mantener `unsafe_allow_html` **solo** con datos generados por el sistema.
3. La clave de acceso debe regenerarse antes de cada presentación pública.
4. No cargar `modelo.pkl` de fuentes externas sin verificar el hash SHA-256 con `verificar_integridad_modelo()`.
5. Configurar **GitHub Actions** con `trivy` y `pytest` como pipeline CI/CD antes de cualquier deploy automatizado.
6. Para producción real (no académica), implementar HTTPS con certificado válido y sesiones con refresh tokens.

---

## Historial de Versiones

| Versión | Fecha | Cambios de seguridad |
|---------|-------|---------------------|
| 1.0 | 2026-06-09 | Análisis inicial de superficie de ataque |
| 1.1 | 2026-06-10 | Auth HMAC (`lsp_auth`), audit log (`lsp_audit`), `showErrorDetails=false`, XSRF, GDPR documentada |
| 1.2 | 2026-06-12 | Rate limiting anti-fuerza-bruta (`MAX_INTENTOS=5`, `BLOQUEO=300s`); verificación SHA-256 del modelo PKL; `tests/test_seguridad.py` con 34 tests (4 clases: sanitización, rate limiting, audit log, integridad PKL) |
| 2.0 | 2026-06-13 | **PLAN DE SEGURIDAD INTEGRAL** — Docker non-root, `.dockerignore`, `trivy.yaml`, INC-09 resuelto (flags Docker), todos los controles verificados y documentados; 9/9 incidentes cerrados |
| 2.1 | 2026-06-13 | Conteos reales de tests (Sanitización 13, IntegridadModelo 7, PrivacidadPorDiseno 3, AuditLog 4+9); §3.5 pre-commit hook DT-20 (3 capas); nombre de test corregido a `TestPrivacidadPorDiseno::test_no_credenciales_en_texto_plano_en_codigo` |
