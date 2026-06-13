"""
tests/test_video.py — TDD: pruebas unitarias de lsp_video.Traductor (HU-08, HU-09, HU-10).

Verifica el procesador WebRTC con frames sintéticos (arrays NumPy) sin requerir
hardware de cámara. Cubre inicialización, thread-safety, overlay y actualizacion de FPS.

Trazabilidad:
  HU-08 CA-08.1  — Stream inicia y el procesador acepta frames
  HU-08 CA-08.3  — Frames procesados correctamente (reduce a 320×240 antes de MediaPipe)
  HU-08 CA-08.4  — Thread-safety del Lock para acceso concurrente UI/video
  HU-09 CA-09.2  — Skeleton de mano dibujado sobre el frame de salida
  HU-10 CA-10.2  — Atributos letra/confianza/mano actualizados en cada recv()
  HU-10 CA-10.3  — Borde rojo/amarillo disponible via atributo confianza
  HU-22 CA-22.1  — FPS tracked via EMA y accesible para qa/fps_test.py
"""
import threading
import numpy as np
import pytest

try:
    import av
    _AV_DISPONIBLE = True
except ImportError:
    _AV_DISPONIBLE = False

pytestmark = pytest.mark.skipif(not _AV_DISPONIBLE, reason="pyav no instalado")


def _make_frame(h=240, w=320, color=(0, 0, 0)):
    """Crea un av.VideoFrame sintético con dimensiones y color dados."""
    arr = np.full((h, w, 3), color, dtype=np.uint8)
    return av.VideoFrame.from_ndarray(arr, format="bgr24")


# ──────────────────────────── Inicialización ──────────────────────────────────

class TestTraductorInicializacion:

    def test_inicializa_con_modelo_none(self):
        """Traductor acepta modelo=None; no predice pero sí procesa frames. HU-08 CA-08.1."""
        from lsp_video import Traductor
        t = Traductor(None)
        assert t.letra == "-"
        assert t.confianza == 0.0
        assert t.mano is False
        assert t.fps == 0.0

    def test_inicializa_con_modelo_real(self, modelo):
        """Traductor acepta el SVM como dependencia inyectada. HU-10 CA-10.1."""
        from lsp_video import Traductor
        t = Traductor(modelo)
        assert t._modelo is modelo

    def test_lock_disponible_al_inicio(self):
        """Lock debe estar libre (no adquirido) al construir el objeto."""
        from lsp_video import Traductor
        t = Traductor(None)
        adquirido = t.lock.acquire(blocking=False)
        assert adquirido, "Lock debe estar libre en el estado inicial"
        t.lock.release()

    def test_atributos_accesibles_sin_lock(self):
        """Los atributos públicos deben ser accesibles desde el hilo de UI."""
        from lsp_video import Traductor
        t = Traductor(None)
        assert isinstance(t.letra, str)
        assert isinstance(t.confianza, float)
        assert isinstance(t.mano, bool)
        assert isinstance(t.fps, float)


# ──────────────────────────── Procesamiento de frames ─────────────────────────

class TestTraductorRecv:

    def test_recv_retorna_av_videoframe(self):
        """recv() debe devolver siempre un av.VideoFrame. HU-08 CA-08.3."""
        from lsp_video import Traductor
        t = Traductor(None)
        resultado = t.recv(_make_frame())
        assert isinstance(resultado, av.VideoFrame)

    def test_recv_frame_sin_mano_deja_mano_false(self):
        """Frame completamente negro → mano=False (sin detección de mano)."""
        from lsp_video import Traductor
        t = Traductor(None)
        t.recv(_make_frame(color=(0, 0, 0)))
        with t.lock:
            assert t.mano is False

    def test_recv_sin_mano_preserva_letra_guion(self):
        """Sin mano detectada, la letra no debe cambiar de '-'. HU-10 CA-10.2."""
        from lsp_video import Traductor
        t = Traductor(None)
        t.recv(_make_frame())
        with t.lock:
            assert t.letra == "-"

    def test_recv_actualiza_fps_tras_multiples_llamadas(self):
        """Tras 5 frames el EMA de FPS debe ser > 0. HU-22 CA-22.1."""
        from lsp_video import Traductor
        t = Traductor(None)
        for _ in range(5):
            t.recv(_make_frame())
        with t.lock:
            assert t.fps > 0.0, "EMA de FPS debe ser positivo tras varios frames"

    def test_recv_dibuja_overlay_en_frame(self):
        """El frame de salida debe diferir del frame negro original (overlay dibujado)."""
        from lsp_video import Traductor
        t = Traductor(None)
        frame_entrada = _make_frame(h=480, w=640, color=(0, 0, 0))
        frame_salida = t.recv(frame_entrada)
        arr_salida = frame_salida.to_ndarray(format="bgr24")
        arr_entrada = frame_entrada.to_ndarray(format="bgr24")
        assert not np.array_equal(arr_salida, arr_entrada), \
            "El frame de salida debe tener el badge 'EN VIVO' y FPS dibujados"

    def test_recv_frame_no_modifica_dimensiones(self):
        """Las dimensiones del frame devuelto deben ser idénticas al de entrada."""
        from lsp_video import Traductor
        t = Traductor(None)
        frame = _make_frame(h=480, w=640)
        resultado = t.recv(frame)
        arr = resultado.to_ndarray(format="bgr24")
        assert arr.shape == (480, 640, 3)


# ──────────────────────────── Thread-safety ──────────────────────────────────

class TestTraductorThreadSafety:

    def test_multiples_hilos_leen_sin_condicion_de_carrera(self):
        """HU-08 CA-08.4: acceso concurrente desde UI thread y video thread."""
        from lsp_video import Traductor
        t = Traductor(None)
        errores = []

        def lector():
            for _ in range(100):
                try:
                    with t.lock:
                        _, _, _ = t.letra, t.confianza, t.mano
                except Exception as e:
                    errores.append(e)

        def escritor():
            for c in "abcdefghij":
                with t.lock:
                    t.letra = c

        hilos = [threading.Thread(target=lector) for _ in range(3)]
        hilos.append(threading.Thread(target=escritor))
        for h in hilos:
            h.start()
        for h in hilos:
            h.join()
        assert len(errores) == 0, f"Condiciones de carrera detectadas: {errores}"

    def test_escritura_atomica_bajo_lock(self):
        """La escritura de (letra, confianza, mano) bajo lock es atómica."""
        from lsp_video import Traductor
        t = Traductor(None)
        with t.lock:
            t.letra = "x"
            t.confianza = 99.9
            t.mano = True
        with t.lock:
            assert t.letra == "x"
            assert t.confianza == 99.9
            assert t.mano is True
