"""
tests/test_auth.py — TDD: pruebas de autenticación (HU-13).
Escritas ANTES de implementar lsp_auth.py (commit en rojo es evidencia del proceso TDD).
"""
import time
import pytest
import lsp_auth


def test_hash_password_devuelve_string_no_vacio():
    h = lsp_auth.hash_password("UPN2026")
    assert isinstance(h, str) and len(h) > 0


def test_hash_password_es_determinista():
    assert lsp_auth.hash_password("UPN2026") == lsp_auth.hash_password("UPN2026")


def test_hash_passwords_distintas_son_diferentes():
    assert lsp_auth.hash_password("UPN2026") != lsp_auth.hash_password("otra_clave")


def test_generar_token_clave_correcta():
    h = lsp_auth.hash_password("UPN2026")
    token = lsp_auth.generar_token_sesion("UPN2026", h)
    assert token is not None
    assert isinstance(token, str)
    assert token.count(".") == 2  # formato: timestamp.nonce.firma


def test_generar_token_clave_incorrecta_devuelve_none():
    h = lsp_auth.hash_password("UPN2026")
    assert lsp_auth.generar_token_sesion("clave_erronea", h) is None


def test_verificar_token_valido():
    h = lsp_auth.hash_password("UPN2026")
    token = lsp_auth.generar_token_sesion("UPN2026", h)
    assert lsp_auth.verificar_token(token) is True


@pytest.mark.parametrize("token_malo", ["basura", "a.b", "", "x.y.z.w"])
def test_verificar_token_malformado(token_malo):
    assert lsp_auth.verificar_token(token_malo) is False


def test_verificar_token_none():
    assert lsp_auth.verificar_token(None) is False


def test_verificar_token_manipulado():
    h = lsp_auth.hash_password("UPN2026")
    token = lsp_auth.generar_token_sesion("UPN2026", h)
    partes = token.split(".")
    partes[2] = "firmafalsificada"
    assert lsp_auth.verificar_token(".".join(partes)) is False


def test_verificar_token_expirado():
    """Token generado con timestamp de hace 2 horas debe rechazarse."""
    import hmac
    import hashlib

    ts_viejo = str(int(time.time()) - 7200)  # 2 horas atrás
    nonce = "nonce_fijo_test"
    firma = hmac.new(
        lsp_auth.PEPPER.encode(),
        f"{ts_viejo}.{nonce}".encode(),
        hashlib.sha256,
    ).hexdigest()
    token_viejo = f"{ts_viejo}.{nonce}.{firma}"
    assert lsp_auth.verificar_token(token_viejo) is False


def test_password_con_caracteres_xss_tratado_como_texto():
    """CA-13.6: inputs con HTML/XSS se procesan como texto plano sin excepciones."""
    xss = "<script>alert('xss')</script>"
    h = lsp_auth.hash_password(xss)
    # Genera un hash válido (64 chars hex) — no lanza excepción
    assert isinstance(h, str) and len(h) == 64
    # El hash del XSS es diferente al de la clave legítima
    assert h != lsp_auth.hash_password(lsp_auth.DEMO_PASSWORD)
    # El XSS como clave no concede acceso (es rechazado como clave incorrecta)
    hash_demo = lsp_auth.hash_password(lsp_auth.DEMO_PASSWORD)
    assert lsp_auth.generar_token_sesion(xss, hash_demo) is None
