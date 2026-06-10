"""Fase 4 — Pruebas de integración: flujo completo imagen → predicción."""
import cv2
import lsp_core


def test_flujo_completo_imagen_a_letra(modelo, imagen_con_mano):
    """Imagen → MediaPipe → landmarks → SVM → letra."""
    img = cv2.imread(imagen_con_mano)
    landmarks = lsp_core.extraer_landmarks(img)
    assert landmarks is not None, "MediaPipe debió detectar la mano"

    letra, confianza = lsp_core.predecir(modelo, landmarks)
    assert str(letra).lower() in lsp_core.LETTERS
    assert confianza > 0


def test_flujo_desde_archivo(modelo, imagen_con_mano):
    landmarks = lsp_core.extraer_landmarks_de_archivo(imagen_con_mano)
    letra, _ = lsp_core.predecir(modelo, landmarks)
    assert letra in modelo.classes_


def test_dataset_carga_consistente():
    """X e y deben tener el mismo largo y X debe tener 42 columnas."""
    X, y = lsp_core.cargar_dataset(limite_por_letra=3)
    assert len(X) == len(y)
    if len(X) > 0:
        assert X.shape[1] == lsp_core.NUM_FEATURES
