"""Fase 14 — Manejo de errores: modelo inexistente / archivo corrupto."""
import pytest
import lsp_core


def test_modelo_inexistente_lanza_filenotfound():
    with pytest.raises(FileNotFoundError):
        lsp_core.cargar_modelo("no_existe_modelo.pkl")


def test_archivo_corrupto_lanza_excepcion(tmp_path):
    corrupto = tmp_path / "modelo_corrupto.pkl"
    corrupto.write_bytes(b"esto no es un pickle valido")
    with pytest.raises(Exception):
        lsp_core.cargar_modelo(str(corrupto))


def test_imagen_inexistente_devuelve_none():
    # cv2.imread de una ruta inexistente devuelve None -> extraer debe tolerarlo
    assert lsp_core.extraer_landmarks_de_archivo("ruta_que_no_existe.png") is None


def test_imagen_corrupta_devuelve_none(tmp_path):
    falsa = tmp_path / "falsa.png"
    falsa.write_bytes(b"PNG falso corrupto")
    assert lsp_core.extraer_landmarks_de_archivo(str(falsa)) is None
