"""
Web app del Traductor de Lengua de Señas Peruana (LSP).
Carga el modelo ya entrenado ('modelo.pkl') y traduce en vivo usando la cámara
del navegador del usuario (funciona en PC y celular, sin instalar nada).

Probar localmente:   streamlit run app.py
Desplegar gratis:    subir el repo a GitHub y conectarlo en streamlit.io
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import warnings
warnings.filterwarnings("ignore")

import av
import cv2
import numpy as np
import joblib
import mediapipe as mp
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration

st.set_page_config(page_title="Traductor LSP", page_icon="🤟", layout="centered")

st.title("🤟 Traductor de Lengua de Señas Peruana")
st.caption("Universidad Privada del Norte (UPN) — Capstone Project Sistemas")

st.markdown(
    "Haz una seña frente a la cámara y el sistema mostrará la **letra** detectada en tiempo real. "
    "Pulsa **START** para activar tu cámara (el navegador pedirá permiso)."
)


@st.cache_resource
def cargar_modelo():
    """Carga el modelo entrenado una sola vez y lo reutiliza."""
    if not os.path.exists("modelo.pkl"):
        return None
    return joblib.load("modelo.pkl")


modelo = cargar_modelo()

if modelo is None:
    st.error(
        "No se encontró 'modelo.pkl'. Ejecuta primero `python entrenar_modelo.py` "
        "para generar el modelo a partir del dataset."
    )
    st.stop()

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Servidor STUN público de Google para que la cámara conecte a través del navegador.
RTC_CONFIG = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)


class Traductor(VideoProcessorBase):
    def __init__(self):
        self.hands = mp_hands.Hands(
            static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7
        )

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        letra = "-"
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    img, hand_landmarks, mp_hands.HAND_CONNECTIONS
                )
                landmarks = []
                for lm in hand_landmarks.landmark:
                    landmarks.append(lm.x)
                    landmarks.append(lm.y)
                if len(landmarks) == 42:
                    try:
                        letra = modelo.predict([landmarks])[0]
                    except Exception:
                        pass

        cv2.putText(
            img, f"Letra: {letra.upper()}", (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3, cv2.LINE_AA,
        )
        return av.VideoFrame.from_ndarray(img, format="bgr24")


webrtc_streamer(
    key="traductor-lsp",
    video_processor_factory=Traductor,
    rtc_configuration=RTC_CONFIG,
    media_stream_constraints={"video": True, "audio": False},
)

with st.expander("ℹ️ ¿Cómo funciona?"):
    st.markdown(
        "1. **MediaPipe** detecta 21 puntos clave de tu mano (42 coordenadas).\n"
        "2. Un modelo **SVM** ya entrenado clasifica esos puntos en una letra.\n"
        "3. Todo el cómputo de la seña ocurre en el servidor; tú solo necesitas un navegador."
    )
