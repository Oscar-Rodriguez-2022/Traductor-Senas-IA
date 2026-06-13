"""
lsp_auth.py — Autenticación de sesión académica para LSP Vision AI (HU-13).

Implementa un esquema JWT-inspirado usando solo stdlib (hashlib, hmac, secrets).
No requiere base de datos ni dependencias externas.

Flujo:
  1. hash_password()       → genera el hash de la clave para almacenar en secrets.
  2. generar_token_sesion() → verifica la clave y emite un token firmado.
  3. verificar_token()     → valida la firma HMAC y la expiración.
  4. login_requerido()     → función de alto nivel para app.py.

Uso en producción:
  Almacenar LSP_PASSWORD_HASH en .streamlit/secrets.toml (no subir al repositorio).
  En modo demo (sin secrets.toml), se usa DEMO_PASSWORD como fallback visible.
"""
import hashlib
import hmac
import secrets
import threading
import time

# ──────────────────────────────── Constantes ──────���───────────────────────���───
PEPPER = "LSP_UPN_2026"              # sal fija de aplicación (no es un secreto criptográfico)
SESSION_EXPIRY_MINUTES = 60
DEMO_PASSWORD = "UPN2026"           # clave de demostración académica — visible intencionalmente
_PBKDF2_ITERATIONS = 260_000        # OWASP 2023 mínimo para PBKDF2-HMAC-SHA256

# ──────────────────────── Rate limiting (brute-force protection) ───────────────
MAX_INTENTOS = 5            # intentos fallidos consecutivos antes de bloquear
BLOQUEO_SEGUNDOS = 300      # duración del bloqueo: 5 minutos

_intentos_fallidos: int = 0
_ultimo_fallo_ts: float = 0.0
_rate_lock = threading.Lock()


def esta_bloqueado() -> bool:
    """
    Indica si el sistema está en período de bloqueo por intentos fallidos.

    Returns:
        bool: True si se superó MAX_INTENTOS y el tiempo de bloqueo aún no ha expirado.
    """
    with _rate_lock:
        if _intentos_fallidos < MAX_INTENTOS:
            return False
        if time.time() - _ultimo_fallo_ts >= BLOQUEO_SEGUNDOS:
            return False   # período de bloqueo expirado automáticamente
        return True


def _registrar_fallo() -> None:
    global _intentos_fallidos, _ultimo_fallo_ts
    with _rate_lock:
        _intentos_fallidos += 1
        _ultimo_fallo_ts = time.time()


def _resetear_intentos() -> None:
    global _intentos_fallidos, _ultimo_fallo_ts
    with _rate_lock:
        _intentos_fallidos = 0
        _ultimo_fallo_ts = 0.0


# ──────────────────────────────── Funciones públicas ──────────────────────────
def hash_password(password: str) -> str:
    """
    Genera el hash PBKDF2-HMAC-SHA256 de una clave para almacenamiento seguro.

    Args:
        password: Clave en texto plano.

    Returns:
        str: Hash hexadecimal de 64 caracteres (256 bits).
    """
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        (password + PEPPER).encode("utf-8"),
        PEPPER.encode("utf-8"),
        _PBKDF2_ITERATIONS,
    )
    return dk.hex()


def generar_token_sesion(password_ingresada: str, password_hash_esperado: str) -> str | None:
    """
    Verifica la clave y emite un token de sesión firmado con HMAC-SHA256.

    Incluye protección anti-fuerza-bruta: devuelve None si el sistema está
    bloqueado por superar MAX_INTENTOS intentos fallidos consecutivos.

    Args:
        password_ingresada: Clave introducida por el usuario.
        password_hash_esperado: Hash almacenado (generado con hash_password()).

    Returns:
        str | None: Token con formato "timestamp.nonce.firma", o None si la clave
            es incorrecta o el sistema está bloqueado por rate limiting.
    """
    if esta_bloqueado():
        return None

    hash_ingresada = hash_password(password_ingresada)
    if not hmac.compare_digest(hash_ingresada, password_hash_esperado):
        _registrar_fallo()
        return None

    _resetear_intentos()
    ts = str(int(time.time()))
    nonce = secrets.token_hex(8)
    firma = _firmar(ts, nonce)
    return f"{ts}.{nonce}.{firma}"


def verificar_token(token) -> bool:
    """
    Valida la firma HMAC y la vigencia temporal del token.

    Args:
        token: Token de sesión (string "timestamp.nonce.firma") o cualquier valor.

    Returns:
        bool: True si el token es válido y no ha expirado.
    """
    if not isinstance(token, str):
        return False
    partes = token.split(".")
    if len(partes) != 3:
        return False

    ts_str, nonce, firma_recibida = partes

    try:
        ts = int(ts_str)
    except ValueError:
        return False

    firma_esperada = _firmar(ts_str, nonce)
    if not hmac.compare_digest(firma_recibida, firma_esperada):
        return False

    ahora = int(time.time())
    if ahora - ts > SESSION_EXPIRY_MINUTES * 60:
        return False

    return True


def login_requerido(st_state: dict) -> bool:
    """
    Verifica la autenticación de la sesión actual de Streamlit.

    Muestra el formulario de acceso si no hay sesión válida.
    Devuelve True si el usuario está autenticado; False si se debe detener la app.

    Args:
        st_state: Referencia a st.session_state de Streamlit.

    Returns:
        bool: True si autenticado, False si no.
    """
    import streamlit as st

    token = st_state.get("lsp_token")
    if token and verificar_token(token):
        return True

    _render_login(st, st_state)
    return False


# ──────────────────────────────── Helpers internos ────────────────────────────
def _firmar(ts_str: str, nonce: str) -> str:
    """Genera la firma HMAC-SHA256 para el par (timestamp, nonce)."""
    return hmac.new(
        PEPPER.encode("utf-8"),
        f"{ts_str}.{nonce}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _obtener_hash_esperado() -> str:
    """
    Lee el hash de la clave desde st.secrets o usa el hash del DEMO_PASSWORD.
    En producción, configurar LSP_PASSWORD_HASH en .streamlit/secrets.toml.
    """
    try:
        import streamlit as st
        return st.secrets["LSP_PASSWORD_HASH"]
    except Exception:
        return hash_password(DEMO_PASSWORD)


def _render_login(st, st_state: dict) -> None:
    """Renderiza el formulario de acceso con estilos accesibles."""
    st.markdown(
        """
<style>
.login-card {
    max-width: 420px; margin: 80px auto; padding: 40px;
    background: #fff; border: 1px solid #ffd2d2; border-radius: 20px;
    box-shadow: 0 8px 32px rgba(227,6,19,0.10);
}
.login-title {font-size:26px; font-weight:800; color:#1A1A1A; margin-bottom:6px;}
.login-sub {font-size:14px; color:#6b6b6b; margin-bottom:24px;}
</style>
<div class="login-card" role="main" aria-label="Formulario de acceso">
  <div class="login-title">🤟 LSP Vision AI</div>
  <div class="login-sub">Sistema académico — Universidad Privada del Norte</div>
</div>
""",
        unsafe_allow_html=True,
    )

    with st.form("form_login", clear_on_submit=False):
        clave = st.text_input(
            "Clave de acceso",
            type="password",
            placeholder="Ingresa la clave académica",
            help="Clave de demostración: UPN2026",
        )
        enviado = st.form_submit_button("Ingresar", use_container_width=True)

    if enviado:
        if esta_bloqueado():
            st.error(
                f"Acceso bloqueado por {MAX_INTENTOS} intentos fallidos. "
                f"Espera {BLOQUEO_SEGUNDOS // 60} minutos antes de intentar nuevamente."
            )
        else:
            hash_esperado = _obtener_hash_esperado()
            token = generar_token_sesion(clave, hash_esperado)
            if token:
                st_state["lsp_token"] = token
                import lsp_audit
                lsp_audit.registrar_acceso("LOGIN_OK", st_state=st_state)
                st.rerun()
            else:
                import lsp_audit
                lsp_audit.registrar_acceso("LOGIN_FAIL")
                restantes = max(0, MAX_INTENTOS - _intentos_fallidos)
                if restantes > 0:
                    st.error(f"Clave incorrecta. Intentos restantes antes del bloqueo: {restantes}.")
                else:
                    st.error(
                        f"Acceso bloqueado. Espera {BLOQUEO_SEGUNDOS // 60} minutos."
                    )
