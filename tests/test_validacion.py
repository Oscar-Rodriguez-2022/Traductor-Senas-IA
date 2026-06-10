"""Fase 2 — Pruebas unitarias: validación de entradas y manejo de errores."""
import numpy as np
import pytest
import lsp_core


def test_validacion_acepta_vector_correcto(landmarks_validos):
    assert lsp_core.landmarks_validos(landmarks_validos) is True


@pytest.mark.parametrize("entrada", [
    None,
    [],
    [0.1] * 41,          # faltan valores
    [0.1] * 43,          # sobran valores
    [0.5] * 40 + [np.nan, 0.5],   # contiene NaN
    [0.5] * 40 + [np.inf, 0.5],   # contiene infinito
])
def test_validacion_rechaza_entradas_invalidas(entrada):
    assert lsp_core.landmarks_validos(entrada) is False


def test_predecir_lanza_error_con_vector_invalido(modelo):
    with pytest.raises(ValueError):
        lsp_core.predecir(modelo, [0.1, 0.2, 0.3])


def test_predecir_lanza_error_con_none(modelo):
    with pytest.raises(ValueError):
        lsp_core.predecir(modelo, None)
