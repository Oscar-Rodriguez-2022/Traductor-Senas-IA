"""
lsp_video.py — Procesador de video WebRTC para el Traductor LSP.

Extrae la clase Traductor de app.py aplicando el principio de responsabilidad única:
este módulo solo gestiona el procesamiento de frames de video, sin código de UI.

El modelo se inyecta como dependencia en __init__ en lugar de accederse como
variable global, lo que facilita las pruebas unitarias con mocks.
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import threading
import time

import av
import cv2
import mediapipe as mp
from streamlit_webrtc import VideoProcessorBase

import lsp_core


class Traductor(VideoProcessorBase):
    """
    Procesador de frames WebRTC para reconocimiento de señas LSP en tiempo real.

    Cada frame recibido es procesado por MediaPipe Hands para extraer landmarks,
    que luego se clasifican con el modelo SVM. Los resultados se almacenan en
    atributos protegidos por un Lock para acceso thread-safe desde el hilo de UI.

    Attributes:
        letra (str): Última letra detectada. Valor '-' si no hay mano visible.
        confianza (float): Confianza en % de la última predicción (0–100).
        mano (bool): True si MediaPipe detectó una mano en el último frame.
        fps (float): FPS suavizados con EMA (alpha=0.2) para visualización estable.
    """

    def __init__(self, modelo):
        """
        Inicializa el procesador con el modelo SVM inyectado.

        Args:
            modelo: Clasificador scikit-learn con predict_proba(). Puede ser None
                si el modelo no está disponible; en ese caso no habrá predicciones.
        """
        self._modelo = modelo
        self.hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=0,          # modo rápido para menor latencia en CPU
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5,
        )
        self._mp_drawing = mp.solutions.drawing_utils
        self._mp_hands = mp.solutions.hands
        self.lock = threading.Lock()
        self.letra = "-"
        self.confianza = 0.0
        self.mano = False
        self._t_prev = time.time()
        self.fps = 0.0

    def recv(self, frame) -> av.VideoFrame:
        """
        Procesa un frame de video: detecta mano, predice letra y dibuja overlay.

        El frame se reduce a 320×240 para aliviar la CPU antes de enviarlo a
        MediaPipe — las coordenadas de landmarks son normalizadas (0–1), por lo
        que la resolución reducida no afecta la precisión de la clasificación.

        Args:
            frame: av.VideoFrame recibido desde el stream WebRTC.

        Returns:
            av.VideoFrame: Frame anotado con skeleton de mano y badges informativos.
        """
        img = frame.to_ndarray(format="bgr24")
        h, w, _ = img.shape

        # Procesar a menor resolución para aliviar la CPU
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        rgb_small = cv2.resize(rgb, (320, 240))
        results = self.hands.process(rgb_small)

        letra, conf, mano = "-", 0.0, False

        if results.multi_hand_landmarks:
            mano = True
            for hand_landmarks in results.multi_hand_landmarks:
                self._mp_drawing.draw_landmarks(
                    img, hand_landmarks, self._mp_hands.HAND_CONNECTIONS,
                    self._mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=3),
                    self._mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2),
                )
                if self._modelo is not None:
                    landmarks = [coord for lm in hand_landmarks.landmark
                                 for coord in (lm.x, lm.y)]
                    if lsp_core.landmarks_validos(landmarks):
                        try:
                            letra, conf = lsp_core.predecir(self._modelo, landmarks)
                        except Exception:
                            pass

        # FPS con suavizado EMA
        ahora = time.time()
        dt = ahora - self._t_prev
        self._t_prev = ahora
        fps_actual = (0.8 * self.fps + 0.2 * (1.0 / dt)) if dt > 0 else self.fps

        with self.lock:
            self.letra, self.confianza, self.mano = letra, conf, mano
            self.fps = fps_actual

        # Badge "EN VIVO"
        cv2.rectangle(img, (12, 12), (132, 46), (19, 6, 227), -1)
        cv2.circle(img, (28, 29), 6, (255, 255, 255), -1)
        cv2.putText(img, "EN VIVO", (42, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # FPS abajo-izquierda
        cv2.rectangle(img, (12, h - 42), (120, h - 12), (40, 40, 40), -1)
        cv2.putText(img, f"FPS: {int(self.fps)}", (22, h - 21), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        return av.VideoFrame.from_ndarray(img, format="bgr24")
