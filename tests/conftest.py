"""Fixtures compartidos por toda la suite de pruebas."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import lsp_core


@pytest.fixture(scope="session")
def modelo():
    """Modelo SVM entrenado (se omiten las pruebas si no existe)."""
    if not os.path.exists(lsp_core.MODELO_PATH):
        pytest.skip("modelo.pkl no encontrado; ejecuta entrenar_modelo.py")
    return lsp_core.cargar_modelo()


@pytest.fixture(scope="session")
def imagen_con_mano():
    """Ruta de una imagen del dataset en la que MediaPipe SÍ detecta mano."""
    for ruta in lsp_core.imagenes_disponibles():
        if lsp_core.extraer_landmarks_de_archivo(ruta) is not None:
            return ruta
    pytest.skip("No hay imágenes con mano detectable en data/")


@pytest.fixture(scope="session")
def landmarks_validos(imagen_con_mano):
    """Un vector de 42 landmarks real extraído del dataset."""
    return lsp_core.extraer_landmarks_de_archivo(imagen_con_mano)


@pytest.fixture
def imagen_negra():
    """Imagen en negro (sin mano)."""
    return np.zeros((240, 320, 3), dtype=np.uint8)
