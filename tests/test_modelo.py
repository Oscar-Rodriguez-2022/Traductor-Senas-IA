"""Fase 2 — Pruebas unitarias: carga del modelo y predicción."""
import numpy as np
import lsp_core


def test_modelo_se_carga(modelo):
    assert modelo is not None
    assert hasattr(modelo, "predict")


def test_modelo_tiene_clases(modelo):
    assert len(modelo.classes_) >= 2
    # Todas las clases son letras del alfabeto
    for c in modelo.classes_:
        assert str(c).lower() in lsp_core.LETTERS


def test_prediccion_devuelve_letra_valida(modelo, landmarks_validos):
    letra, confianza = lsp_core.predecir(modelo, landmarks_validos)
    assert str(letra).lower() in lsp_core.LETTERS
    assert 0.0 <= confianza <= 100.0


def test_prediccion_es_determinista(modelo, landmarks_validos):
    r1 = lsp_core.predecir(modelo, landmarks_validos)
    r2 = lsp_core.predecir(modelo, landmarks_validos)
    assert r1 == r2


def test_modelo_acepta_vector_de_42(modelo):
    vector = np.full((1, lsp_core.NUM_FEATURES), 0.5)
    pred = modelo.predict(vector)
    assert len(pred) == 1
