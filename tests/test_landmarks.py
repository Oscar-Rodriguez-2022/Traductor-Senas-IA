"""Fase 2 — Pruebas unitarias: extracción de landmarks y preprocesamiento."""
import numpy as np
import lsp_core


def test_extraccion_devuelve_42_valores(landmarks_validos):
    assert landmarks_validos is not None
    assert len(landmarks_validos) == lsp_core.NUM_FEATURES


def test_landmarks_normalizados_en_rango(landmarks_validos):
    arr = np.array(landmarks_validos)
    assert np.all(arr >= -0.5) and np.all(arr <= 1.5)


def test_imagen_negra_no_detecta_mano(imagen_negra):
    assert lsp_core.extraer_landmarks(imagen_negra) is None


def test_imagen_none_devuelve_none():
    assert lsp_core.extraer_landmarks(None) is None


def test_imagen_vacia_devuelve_none():
    vacia = np.zeros((0, 0, 3), dtype=np.uint8)
    assert lsp_core.extraer_landmarks(vacia) is None


def test_lectura_imagen_real_del_dataset(imagen_con_mano):
    import cv2
    img = cv2.imread(imagen_con_mano)
    assert img is not None
    assert img.ndim == 3 and img.shape[2] == 3
