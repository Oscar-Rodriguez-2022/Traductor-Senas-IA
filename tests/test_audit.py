"""
tests/test_audit.py — TDD: pruebas del log de auditoría anónimo (HU-14).
Escritas ANTES de implementar lsp_audit.py (commit en rojo es evidencia TDD).
"""
import json
from datetime import datetime, timedelta

import pytest
import lsp_audit


def test_registrar_acceso_crea_archivo(tmp_path, monkeypatch):
    monkeypatch.setattr(lsp_audit, "AUDIT_FILE", str(tmp_path / "audit.jsonl"))
    lsp_audit.registrar_acceso("LOGIN_OK")
    assert (tmp_path / "audit.jsonl").exists()


def test_entrada_tiene_campos_obligatorios(tmp_path, monkeypatch):
    ruta = tmp_path / "audit.jsonl"
    monkeypatch.setattr(lsp_audit, "AUDIT_FILE", str(ruta))
    lsp_audit.registrar_acceso("TRADUCCION_INICIADA", "demo")
    entrada = json.loads(ruta.read_text(encoding="utf-8").strip())
    assert "ts" in entrada
    assert "evento" in entrada
    assert "sesion" in entrada
    assert entrada["evento"] == "TRADUCCION_INICIADA"
    assert entrada["detalle"] == "demo"


def test_ts_es_iso8601(tmp_path, monkeypatch):
    ruta = tmp_path / "audit.jsonl"
    monkeypatch.setattr(lsp_audit, "AUDIT_FILE", str(ruta))
    lsp_audit.registrar_acceso("PAGINA_VISITADA")
    entrada = json.loads(ruta.read_text(encoding="utf-8").strip())
    datetime.fromisoformat(entrada["ts"])  # debe parsear sin excepción


def test_sesion_es_hash_corto(tmp_path, monkeypatch):
    ruta = tmp_path / "audit.jsonl"
    monkeypatch.setattr(lsp_audit, "AUDIT_FILE", str(ruta))
    lsp_audit.registrar_acceso("LOGIN_OK")
    entrada = json.loads(ruta.read_text(encoding="utf-8").strip())
    assert len(entrada["sesion"]) == 8  # hash truncado a 8 caracteres hex


def test_no_almacena_datos_personales(tmp_path, monkeypatch):
    ruta = tmp_path / "audit.jsonl"
    monkeypatch.setattr(lsp_audit, "AUDIT_FILE", str(ruta))
    lsp_audit.registrar_acceso("LOGIN_OK")
    contenido = ruta.read_text(encoding="utf-8").lower()
    assert "192.168" not in contenido
    assert "user-agent" not in contenido
    assert "password" not in contenido


def test_leer_log_reciente_devuelve_lista_vacia_sin_archivo(tmp_path, monkeypatch):
    monkeypatch.setattr(lsp_audit, "AUDIT_FILE", str(tmp_path / "no_existe.jsonl"))
    assert lsp_audit.leer_log_reciente() == []


def test_leer_log_reciente_respeta_limite(tmp_path, monkeypatch):
    ruta = tmp_path / "audit.jsonl"
    monkeypatch.setattr(lsp_audit, "AUDIT_FILE", str(ruta))
    for i in range(10):
        lsp_audit.registrar_acceso("PAGINA_VISITADA", str(i))
    entradas = lsp_audit.leer_log_reciente(n=5)
    assert len(entradas) == 5


def test_leer_log_reciente_devuelve_ultimas(tmp_path, monkeypatch):
    ruta = tmp_path / "audit.jsonl"
    monkeypatch.setattr(lsp_audit, "AUDIT_FILE", str(ruta))
    for i in range(3):
        lsp_audit.registrar_acceso("PAGINA_VISITADA", f"ev{i}")
    entradas = lsp_audit.leer_log_reciente(n=2)
    assert entradas[-1]["detalle"] == "ev2"


def test_purgar_log_antiguo(tmp_path, monkeypatch):
    ruta = tmp_path / "audit.jsonl"
    monkeypatch.setattr(lsp_audit, "AUDIT_FILE", str(ruta))

    vieja = {
        "ts": (datetime.now() - timedelta(days=10)).isoformat(),
        "evento": "VIEJA",
        "sesion": "aaaaaaaa",
        "detalle": "",
    }
    nueva = {
        "ts": datetime.now().isoformat(),
        "evento": "NUEVA",
        "sesion": "bbbbbbbb",
        "detalle": "",
    }
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(json.dumps(vieja) + "\n")
        f.write(json.dumps(nueva) + "\n")

    eliminadas = lsp_audit.purgar_log_antiguo(dias=7)
    assert eliminadas == 1
    restantes = lsp_audit.leer_log_reciente()
    assert len(restantes) == 1
    assert restantes[0]["evento"] == "NUEVA"
