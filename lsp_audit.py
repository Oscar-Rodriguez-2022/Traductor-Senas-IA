"""
lsp_audit.py — Log de auditoría anónimo para LSP Vision AI (HU-14).

Registra eventos de acceso y uso sin almacenar datos personales identificables.
Cumple GDPR Artículo 25 (privacidad por diseño): ninguna entrada contiene
IP, user-agent, nombre, ni información reversible al usuario.

El ID de sesión es SHA-256[:8] derivado de un nonce interno — no reversible.
En Streamlit Cloud el archivo es efímero (filesystem volátil); en entorno
local persiste entre reinicios para auditoría offline.

Eventos estándar: LOGIN_OK, LOGIN_FAIL, SESION_EXPIRADA,
                  TRADUCCION_INICIADA, TRADUCCION_DETENIDA, PAGINA_VISITADA.
"""
import hashlib
import json
import os
from datetime import datetime, timedelta

AUDIT_FILE = "audit_log.jsonl"   # JSON Lines: un evento por línea

# ─────────────────────────── Funciones públicas ────────────────────────────────

def registrar_acceso(evento: str, detalle: str = "", st_state: dict = None) -> None:
    """
    Escribe una entrada de auditoría en AUDIT_FILE.

    Args:
        evento: Identificador del evento (ej. "LOGIN_OK", "PAGINA_VISITADA").
        detalle: Información contextual opcional, sin datos personales.
        st_state: st.session_state de Streamlit (para extraer ID de sesión anónimo).
    """
    entrada = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "evento": evento,
        "sesion": _id_sesion(st_state),
        "detalle": detalle,
    }
    try:
        with open(AUDIT_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entrada, ensure_ascii=False) + "\n")
    except OSError:
        pass  # No interrumpir la app si el log no puede escribirse


def leer_log_reciente(n: int = 50) -> list:
    """
    Lee las últimas n entradas del log de auditoría.

    Args:
        n: Número máximo de entradas a devolver.

    Returns:
        list[dict]: Lista de entradas como dicts. Vacía si el archivo no existe.
    """
    if not os.path.exists(AUDIT_FILE):
        return []
    try:
        with open(AUDIT_FILE, "r", encoding="utf-8") as f:
            lineas = [l.strip() for l in f if l.strip()]
        ultimas = lineas[-n:]
        return [json.loads(l) for l in ultimas]
    except (OSError, json.JSONDecodeError):
        return []


def purgar_log_antiguo(dias: int = 7) -> int:
    """
    Elimina entradas con más de `dias` días de antigüedad.

    Args:
        dias: Umbral de antigüedad en días.

    Returns:
        int: Número de entradas eliminadas.
    """
    if not os.path.exists(AUDIT_FILE):
        return 0

    limite = datetime.now() - timedelta(days=dias)
    conservadas = []
    eliminadas = 0

    try:
        with open(AUDIT_FILE, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                try:
                    entrada = json.loads(linea)
                    ts = datetime.fromisoformat(entrada.get("ts", ""))
                    if ts >= limite:
                        conservadas.append(linea)
                    else:
                        eliminadas += 1
                except (ValueError, KeyError):
                    conservadas.append(linea)

        with open(AUDIT_FILE, "w", encoding="utf-8") as f:
            for linea in conservadas:
                f.write(linea + "\n")
    except OSError:
        pass

    return eliminadas


# ─────────────────────────── Helpers internos ─────────────────────────────────

def _id_sesion(st_state: dict = None) -> str:
    """
    Genera un ID de sesión anónimo de 8 caracteres hexadecimales.

    Deriva el ID del token de sesión almacenado en st_state (si existe),
    o genera uno basado en el timestamp actual. Nunca almacena datos personales.
    """
    fuente = ""
    if st_state and isinstance(st_state, dict):
        fuente = st_state.get("lsp_token", "")
    if not fuente:
        fuente = str(id(st_state)) if st_state is not None else "anonimo"
    return hashlib.sha256(fuente.encode("utf-8")).hexdigest()[:8]
