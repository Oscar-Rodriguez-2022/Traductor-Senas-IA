"""
tests/test_seguridad.py — TDD: Plan de Seguridad Integral por capas (DevSecOps).

Capa de Aplicación : sanitización de inputs, protección HMAC, rate limiting.
Capa de Almacenamiento : integridad del modelo PKL, anonimato del log de auditoría.
Capa de Infraestructura: configuración Streamlit segura, privacidad por diseño.

Trazabilidad:
  HU-13 CA-13.6 — Sanitización / XSS / inyección SQL tratados como texto plano
  HU-13         — Rate limiting anti-fuerza-bruta (MAX_INTENTOS, BLOQUEO_SEGUNDOS)
  HU-14 CA-14.2 — IDs de sesión no reversibles (SHA-256[:8])
  HU-20         — Privacidad por diseño: frames no persistidos
  SEGURIDAD.md  — Riesgos XSS, CSRF, secretos, modelo PKL
"""
import os
import re
import glob
import json
import pytest
import numpy as np
import lsp_auth
import lsp_audit
import lsp_core


# ═══════════════════════════════════════════════════════════════════════════════
# CAPA DE APLICACIÓN — Sanitización y autenticación robusta
# ═══════════════════════════════════════════════════════════════════════════════

class TestSanitizacionInputs:
    """CA-13.6 — Inputs maliciosos se tratan como texto plano, nunca ejecutados."""

    @pytest.mark.parametrize("payload", [
        "<script>alert('xss')</script>",
        "javascript:void(0)",
        "UPN2026<img src=x onerror=alert(1)>",
        "' OR '1'='1",
        "'; DROP TABLE sessions; --",
        "../../etc/passwd",
        "%3Cscript%3Ealert%281%29%3C%2Fscript%3E",
    ])
    def test_payload_malicioso_no_concede_acceso(self, payload):
        """Ningún payload XSS/SQLi debe generar un token válido con la clave real."""
        hash_real = lsp_auth.hash_password(lsp_auth.DEMO_PASSWORD)
        token = lsp_auth.generar_token_sesion(payload, hash_real)
        assert token is None, f"Payload '{payload[:40]}' concedió acceso indebido"

    @pytest.mark.parametrize("payload", [
        "<script>alert(1)</script>",
        "'; DROP TABLE users;--",
        "\x00\x01\x02",          # bytes nulos / control
        "A" * 10_000,            # input muy largo
    ])
    def test_hash_payload_no_lanza_excepcion(self, payload):
        """hash_password debe tolerar cualquier string sin lanzar excepciones."""
        h = lsp_auth.hash_password(payload)
        assert isinstance(h, str) and len(h) == 64

    def test_token_manipulado_en_timestamp_rechazado(self):
        """Modificar el timestamp de un token no produce un token válido."""
        h = lsp_auth.hash_password(lsp_auth.DEMO_PASSWORD)
        token = lsp_auth.generar_token_sesion(lsp_auth.DEMO_PASSWORD, h)
        partes = token.split(".")
        partes[0] = "1"  # timestamp manipulado a epoch 0
        assert lsp_auth.verificar_token(".".join(partes)) is False

    def test_token_manipulado_en_nonce_rechazado(self):
        """Modificar el nonce de un token invalida la firma HMAC."""
        h = lsp_auth.hash_password(lsp_auth.DEMO_PASSWORD)
        token = lsp_auth.generar_token_sesion(lsp_auth.DEMO_PASSWORD, h)
        partes = token.split(".")
        partes[1] = "nonce_falso"
        assert lsp_auth.verificar_token(".".join(partes)) is False


class TestRateLimiting:
    """Protección anti-fuerza-bruta: bloqueo tras MAX_INTENTOS fallidos."""

    @pytest.fixture(autouse=True)
    def resetear_contador(self, monkeypatch):
        """Aislar el estado del rate limiter entre tests."""
        monkeypatch.setattr(lsp_auth, "_intentos_fallidos", 0)
        monkeypatch.setattr(lsp_auth, "_ultimo_fallo_ts", 0.0)
        yield
        # Resetear tras el test también
        monkeypatch.setattr(lsp_auth, "_intentos_fallidos", 0)
        monkeypatch.setattr(lsp_auth, "_ultimo_fallo_ts", 0.0)

    def test_sin_intentos_no_esta_bloqueado(self):
        """Estado inicial: sin intentos fallidos → no bloqueado."""
        assert lsp_auth.esta_bloqueado() is False

    def test_bloquea_tras_max_intentos(self, monkeypatch):
        """Tras MAX_INTENTOS fallidos consecutivos el sistema debe bloquearse."""
        hash_real = lsp_auth.hash_password(lsp_auth.DEMO_PASSWORD)
        for _ in range(lsp_auth.MAX_INTENTOS):
            lsp_auth.generar_token_sesion("clave_erronea_test", hash_real)
        assert lsp_auth.esta_bloqueado() is True

    def test_bloqueado_devuelve_none_aunque_clave_correcta(self, monkeypatch):
        """Si está bloqueado, incluso la clave correcta debe ser rechazada."""
        monkeypatch.setattr(lsp_auth, "_intentos_fallidos", lsp_auth.MAX_INTENTOS)
        import time as _time
        monkeypatch.setattr(lsp_auth, "_ultimo_fallo_ts", _time.time())

        hash_real = lsp_auth.hash_password(lsp_auth.DEMO_PASSWORD)
        token = lsp_auth.generar_token_sesion(lsp_auth.DEMO_PASSWORD, hash_real)
        assert token is None, "Sistema bloqueado debe rechazar incluso la clave correcta"

    def test_login_exitoso_resetea_contador(self, monkeypatch):
        """Un login exitoso debe resetear el contador de intentos fallidos."""
        hash_real = lsp_auth.hash_password(lsp_auth.DEMO_PASSWORD)
        # Dos fallos previos
        lsp_auth.generar_token_sesion("erronea", hash_real)
        lsp_auth.generar_token_sesion("erronea", hash_real)
        # Login exitoso
        token = lsp_auth.generar_token_sesion(lsp_auth.DEMO_PASSWORD, hash_real)
        assert token is not None
        assert lsp_auth.esta_bloqueado() is False
        assert lsp_auth._intentos_fallidos == 0

    def test_bloqueo_expira_automaticamente(self, monkeypatch):
        """El bloqueo debe expirar cuando BLOQUEO_SEGUNDOS han transcurrido."""
        import time as _time
        monkeypatch.setattr(lsp_auth, "_intentos_fallidos", lsp_auth.MAX_INTENTOS)
        # Timestamp de hace más tiempo que el período de bloqueo
        monkeypatch.setattr(lsp_auth, "_ultimo_fallo_ts",
                            _time.time() - lsp_auth.BLOQUEO_SEGUNDOS - 1)
        assert lsp_auth.esta_bloqueado() is False, \
            "El bloqueo debe expirar automáticamente tras BLOQUEO_SEGUNDOS"


# ═══════════════════════════════════════════════════════════════════════════════
# CAPA DE ALMACENAMIENTO — Audit log y modelo PKL
# ═══════════════════════════════════════════════════════════════════════════════

class TestAuditLogAnonimato:
    """HU-14 CA-14.2 — El log no debe contener datos personales identificables."""

    def test_log_no_contiene_ip(self, tmp_path, monkeypatch):
        """Ninguna entrada debe contener una dirección IP."""
        monkeypatch.setattr(lsp_audit, "AUDIT_FILE", str(tmp_path / "audit.jsonl"))
        lsp_audit.registrar_acceso("LOGIN_OK", "detalle_test")
        contenido = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
        assert not re.search(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", contenido), \
            "El log no debe contener ninguna dirección IP"

    def test_log_no_contiene_user_agent(self, tmp_path, monkeypatch):
        """Ninguna entrada debe mencionar user-agent u otros headers HTTP."""
        monkeypatch.setattr(lsp_audit, "AUDIT_FILE", str(tmp_path / "audit.jsonl"))
        lsp_audit.registrar_acceso("PAGINA_VISITADA")
        contenido = (tmp_path / "audit.jsonl").read_text(encoding="utf-8").lower()
        assert "user-agent" not in contenido
        assert "mozilla" not in contenido

    def test_id_sesion_no_contiene_token_original(self):
        """El hash de sesión de 8 chars no debe contener el token en texto plano."""
        token_secreto = "mi_token_secreto_123456"
        hash_sesion = lsp_audit._id_sesion({"lsp_token": token_secreto})
        assert token_secreto not in hash_sesion
        assert len(hash_sesion) == 8

    def test_id_sesion_distintos_tokens_producen_distintos_ids(self):
        """Tokens distintos deben producir hashes distintos (sin colisiones triviales)."""
        id1 = lsp_audit._id_sesion({"lsp_token": "token_A"})
        id2 = lsp_audit._id_sesion({"lsp_token": "token_B"})
        assert id1 != id2


class TestIntegridadModelo:
    """Verificación SHA-256 del modelo PKL contra deserialización maliciosa."""

    def test_calcular_hash_devuelve_sha256_hex(self, tmp_path):
        """calcular_hash_modelo retorna un string hexadecimal de 64 chars."""
        modelo_falso = tmp_path / "modelo.pkl"
        modelo_falso.write_bytes(b"contenido de prueba del modelo")
        h = lsp_core.calcular_hash_modelo(str(modelo_falso))
        assert isinstance(h, str)
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_calcular_hash_es_determinista(self, tmp_path):
        """El mismo archivo siempre produce el mismo hash."""
        modelo_falso = tmp_path / "modelo.pkl"
        modelo_falso.write_bytes(b"contenido estable")
        h1 = lsp_core.calcular_hash_modelo(str(modelo_falso))
        h2 = lsp_core.calcular_hash_modelo(str(modelo_falso))
        assert h1 == h2

    def test_calcular_hash_distinto_tras_modificacion(self, tmp_path):
        """Modificar el archivo cambia su hash SHA-256."""
        archivo = tmp_path / "modelo.pkl"
        archivo.write_bytes(b"contenido original")
        hash_original = lsp_core.calcular_hash_modelo(str(archivo))
        archivo.write_bytes(b"contenido MANIPULADO")
        hash_modificado = lsp_core.calcular_hash_modelo(str(archivo))
        assert hash_original != hash_modificado

    def test_verificar_integridad_acepta_hash_correcto(self, tmp_path):
        """verificar_integridad_modelo retorna True si el hash coincide."""
        archivo = tmp_path / "modelo.pkl"
        archivo.write_bytes(b"modelo legitimo")
        hash_correcto = lsp_core.calcular_hash_modelo(str(archivo))
        assert lsp_core.verificar_integridad_modelo(str(archivo), hash_correcto) is True

    def test_verificar_integridad_detecta_tampering(self, tmp_path):
        """verificar_integridad_modelo retorna False si el archivo fue modificado."""
        archivo = tmp_path / "modelo.pkl"
        archivo.write_bytes(b"modelo legitimo")
        hash_guardado = lsp_core.calcular_hash_modelo(str(archivo))
        archivo.write_bytes(b"modelo MANIPULADO por atacante")
        assert lsp_core.verificar_integridad_modelo(str(archivo), hash_guardado) is False

    def test_verificar_integridad_archivo_inexistente(self, tmp_path):
        """verificar_integridad_modelo retorna False si el archivo no existe."""
        assert lsp_core.verificar_integridad_modelo(
            str(tmp_path / "no_existe.pkl"), "hash_cualquiera"
        ) is False

    def test_calcular_hash_lanza_filenotfound(self, tmp_path):
        """calcular_hash_modelo lanza FileNotFoundError si el archivo no existe."""
        with pytest.raises(FileNotFoundError):
            lsp_core.calcular_hash_modelo(str(tmp_path / "inexistente.pkl"))


# ═══════════════════════════════════════════════════════════════════════════════
# CAPA DE INFRAESTRUCTURA — Configuración Streamlit y privacidad por diseño
# ═══════════════════════════════════════════════════════════════════════════════

class TestConfiguracionStreamlit:
    """Verificación de la configuración segura de Streamlit (.streamlit/config.toml)."""

    @pytest.fixture(scope="class")
    def config(self):
        import sys
        if sys.version_info >= (3, 11):
            import tomllib
            with open(".streamlit/config.toml", "rb") as f:
                return tomllib.load(f)
        else:
            pytest.skip("tomllib requiere Python 3.11+")

    def test_show_error_details_desactivado(self, config):
        """[client] showErrorDetails debe ser false para no exponer trazas en producción."""
        valor = config.get("client", {}).get("showErrorDetails")
        assert valor is False or str(valor).lower() == "false", \
            "showErrorDetails debe estar desactivado"

    def test_xsrf_protection_activo(self, config):
        """[server] enableXsrfProtection debe ser true."""
        valor = config.get("server", {}).get("enableXsrfProtection", True)
        assert valor is True or str(valor).lower() == "true", \
            "enableXsrfProtection debe estar activo"


class TestPrivacidadPorDiseno:
    """HU-20 / GDPR Art. 25 — Ningún frame ni landmark se persiste a disco."""

    def test_frames_no_se_persisten_durante_recv(self, tmp_path):
        """recv() no debe crear archivos de imagen en el sistema de ficheros."""
        try:
            import av
            from lsp_video import Traductor
        except ImportError:
            pytest.skip("av o lsp_video no disponibles")

        t = Traductor(None)
        frame = av.VideoFrame.from_ndarray(
            np.zeros((240, 320, 3), dtype=np.uint8), format="bgr24"
        )
        antes = set(glob.glob("*.png") + glob.glob("*.jpg") + glob.glob("data/**/*.png"))
        t.recv(frame)
        despues = set(glob.glob("*.png") + glob.glob("*.jpg") + glob.glob("data/**/*.png"))
        nuevos = despues - antes
        assert len(nuevos) == 0, f"recv() creó archivos de imagen inesperados: {nuevos}"

    def test_no_credenciales_en_texto_plano_en_codigo(self):
        """Ningún archivo .py del proyecto debe contener contraseñas en texto plano."""
        archivos = glob.glob("*.py") + glob.glob("tests/*.py")
        patron_clave = re.compile(r'password\s*=\s*["\'][^"\']{4,}["\']', re.IGNORECASE)
        excepciones = {"demo_password", "upn2026", "lsp_password_hash"}  # académico documentado

        for ruta in archivos:
            with open(ruta, encoding="utf-8", errors="ignore") as f:
                for n, linea in enumerate(f, 1):
                    if patron_clave.search(linea):
                        linea_lower = linea.lower()
                        if not any(exc in linea_lower for exc in excepciones):
                            pytest.fail(
                                f"Posible clave en texto plano en {ruta}:{n} → {linea.strip()}"
                            )

    def test_audit_log_no_contiene_landmarks(self, tmp_path, monkeypatch):
        """El log de auditoría no debe almacenar vectores de landmarks (datos biométricos)."""
        monkeypatch.setattr(lsp_audit, "AUDIT_FILE", str(tmp_path / "audit.jsonl"))
        lsp_audit.registrar_acceso("TRADUCCION_INICIADA", "letra=A,conf=95.0")
        contenido = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
        # Un vector de landmarks contiene muchos floats decimales seguidos; detectar ese patrón
        assert not re.search(r"\d+\.\d+,\s*\d+\.\d+,\s*\d+\.\d+,\s*\d+\.\d+", contenido), \
            "El log no debe contener vectores de landmarks (datos biométricos)"
