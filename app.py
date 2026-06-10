"""
LSP Vision AI — Traductor de Lengua de Señas Peruana
Universidad Privada del Norte (UPN) — Capstone Project Sistemas

Web app con interfaz tipo dashboard. Carga el modelo entrenado ('modelo.pkl')
y traduce señas en vivo usando la cámara del navegador (PC o celular).

Probar local:  streamlit run app.py
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import warnings
warnings.filterwarnings("ignore")

import time
import threading

import av
import cv2
import numpy as np
import joblib
import mediapipe as mp
import streamlit as st
from streamlit_webrtc import (
    webrtc_streamer,
    VideoProcessorBase,
    RTCConfiguration,
    VideoHTMLAttributes,
)

# ───────────────────────────── Configuración general ─────────────────────────────
st.set_page_config(
    page_title="LSP Vision AI — Traductor de Señas",
    page_icon="🤟",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ROJO = "#E30613"


@st.cache_resource
def cargar_modelo():
    if not os.path.exists("modelo.pkl"):
        return None
    return joblib.load("modelo.pkl")


modelo = cargar_modelo()

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

RTC_CONFIG = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

# ───────────────────────────── Estilos (CSS) ─────────────────────────────
st.markdown(
    """
<style>
    /* Ocultar elementos por defecto de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1250px;}

    /* Barra superior */
    .topbar {
        display: flex; align-items: center; gap: 14px;
        background: linear-gradient(90deg, #E30613 0%, #b00410 100%);
        color: #fff; padding: 16px 26px; border-radius: 16px;
        box-shadow: 0 8px 24px rgba(227,6,19,0.25); margin-bottom: 22px;
    }
    .topbar .logo {
        background: #fff; color: #E30613; width: 52px; height: 52px;
        border-radius: 14px; display: flex; align-items: center; justify-content: center;
        font-size: 28px; font-weight: 800;
    }
    .topbar .brand {font-size: 24px; font-weight: 800; line-height: 1;}
    .topbar .brand span {opacity: .85; font-weight: 600;}
    .topbar .sub {font-size: 12.5px; opacity: .9; margin-top: 3px;}
    .topbar .upn {margin-left: auto; font-weight: 800; font-size: 18px; letter-spacing: 1px;}

    /* Hero */
    .hero h1 {font-size: 40px; font-weight: 800; margin: 0; color: #1A1A1A; line-height: 1.1;}
    .hero h1 .red {color: #E30613;}
    .hero p {color: #555; font-size: 16px; margin-top: 8px;}

    /* Tarjetas */
    .card {
        background: #fff; border: 1px solid #f0e3e3; border-radius: 18px;
        padding: 22px; box-shadow: 0 6px 20px rgba(0,0,0,0.05); height: 100%;
    }
    .card-title {display:flex; align-items:center; gap:8px; font-weight:700; font-size:17px; margin-bottom:14px; color:#1A1A1A;}

    /* Panel de resultado */
    .result-letter {
        font-size: 120px; font-weight: 800; color: #E30613;
        text-align: center; line-height: 1; margin: 10px 0;
        text-shadow: 0 4px 14px rgba(227,6,19,0.18);
    }
    .result-label {color:#888; font-size:14px; margin-bottom:4px;}
    .bar-bg {background:#f1e4e4; border-radius:10px; height:14px; width:100%; overflow:hidden;}
    .bar-fill {background:linear-gradient(90deg,#E30613,#ff5a44); height:100%; border-radius:10px;}
    .estado-ok {
        display:flex; align-items:center; gap:10px; background:#fff5f5;
        border:1px solid #ffd9d9; border-radius:12px; padding:12px 14px; margin-top:16px;
    }
    .estado-ok .dot {width:34px;height:34px;border-radius:50%;background:#E30613;color:#fff;
        display:flex;align-items:center;justify-content:center;font-size:16px;}

    /* Tabla de estado del sistema */
    .status-row {display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #f3eaea; font-size:14.5px;}
    .status-row:last-child {border-bottom:none;}
    .status-row .ok {color:#1aa251; font-weight:700;}
    .status-row .val {color:#E30613; font-weight:700;}

    /* Pipeline */
    .pipe {display:flex; align-items:center; justify-content:space-between; gap:6px; flex-wrap:wrap;}
    .pipe .step {text-align:center; flex:1; min-width:110px;}
    .pipe .ico {width:54px;height:54px;border-radius:50%;background:#fff0f0;color:#E30613;
        display:flex;align-items:center;justify-content:center;font-size:24px;margin:0 auto 8px;}
    .pipe .step b {display:block;font-size:13.5px;color:#1A1A1A;}
    .pipe .step small {color:#888;font-size:11.5px;}
    .pipe .arrow {color:#E30613;font-size:22px;}

    /* Stats */
    .stat {background:#fff;border:1px solid #f0e3e3;border-radius:14px;padding:16px;text-align:center;}
    .stat .num {font-size:26px;font-weight:800;color:#E30613;}
    .stat .lbl {font-size:12px;color:#777;margin-top:2px;}

    /* Footer banner */
    .footer-banner {
        background:linear-gradient(90deg,#fff0f0,#ffe3e3); border:1px solid #ffd2d2;
        border-radius:16px; padding:18px 24px; margin-top:22px; color:#7a1118;
    }
    .footer-banner b {color:#E30613;}
</style>
""",
    unsafe_allow_html=True,
)

# ───────────────────────────── Barra superior ─────────────────────────────
n_senas = len(modelo.classes_) if modelo is not None else 0
st.markdown(
    f"""
<div class="topbar">
    <div class="logo">🤟</div>
    <div>
        <div class="brand">LSP <span>Vision AI</span></div>
        <div class="sub">Traductor de Lengua de Señas Peruana</div>
    </div>
    <div class="upn">🏔 UPN</div>
</div>
""",
    unsafe_allow_html=True,
)

if modelo is None:
    st.error("No se encontró 'modelo.pkl'. Ejecuta primero `python entrenar_modelo.py`.")
    st.stop()

# ───────────────────────────── Hero ─────────────────────────────
st.markdown(
    """
<div class="hero">
    <h1>Traductor Inteligente de <span class="red">Lengua de Señas Peruana</span></h1>
    <p>Sistema de reconocimiento en tiempo real mediante Inteligencia Artificial y Visión por Computadora.</p>
</div>
""",
    unsafe_allow_html=True,
)
st.write("")


# ───────────────────────────── Procesador de video ─────────────────────────────
class Traductor(VideoProcessorBase):
    def __init__(self):
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=0,          # modo rápido (menos carga de CPU)
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5,
        )
        self.lock = threading.Lock()
        self.letra = "-"
        self.confianza = 0.0
        self.mano = False
        self._t_prev = time.time()
        self.fps = 0.0

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        h, w, _ = img.shape
        # Procesar a menor resolución para aliviar la CPU. Los landmarks de MediaPipe
        # son coordenadas normalizadas (0-1), así que NO se pierde precisión al reducir.
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        rgb_small = cv2.resize(rgb, (320, 240))
        results = self.hands.process(rgb_small)

        letra, conf, mano = "-", 0.0, False
        if results.multi_hand_landmarks:
            mano = True
            for hand_landmarks in results.multi_hand_landmarks:
                # Landmarks ROJOS (estilo LSP Vision AI)
                mp_drawing.draw_landmarks(
                    img, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=3),
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2),
                )
                landmarks = []
                for lm in hand_landmarks.landmark:
                    landmarks.append(lm.x)
                    landmarks.append(lm.y)
                if len(landmarks) == 42:
                    try:
                        probas = modelo.predict_proba([landmarks])[0]
                        idx = int(np.argmax(probas))
                        letra = str(modelo.classes_[idx])
                        conf = float(probas[idx]) * 100.0
                    except Exception:
                        pass

        # FPS
        ahora = time.time()
        dt = ahora - self._t_prev
        self._t_prev = ahora
        if dt > 0:
            self.fps = 0.8 * self.fps + 0.2 * (1.0 / dt)

        with self.lock:
            self.letra, self.confianza, self.mano = letra, conf, mano

        # Badge "EN VIVO"
        cv2.rectangle(img, (12, 12), (132, 46), (19, 6, 227), -1)
        cv2.circle(img, (28, 29), 6, (255, 255, 255), -1)
        cv2.putText(img, "EN VIVO", (42, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        # FPS abajo-izquierda
        cv2.rectangle(img, (12, h - 42), (120, h - 12), (40, 40, 40), -1)
        cv2.putText(img, f"FPS: {int(self.fps)}", (22, h - 21), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        return av.VideoFrame.from_ndarray(img, format="bgr24")


# ───────────────────────────── Estado del sistema ─────────────────────────────
col_main, col_side = st.columns([3, 2], gap="large")

with col_main:
    st.markdown('<div class="card-title">📷 Cámara en vivo</div>', unsafe_allow_html=True)
    ctx = webrtc_streamer(
        key="lsp",
        video_processor_factory=Traductor,
        rtc_configuration=RTC_CONFIG,
        media_stream_constraints={"video": True, "audio": False},
        video_html_attrs=VideoHTMLAttributes(
            autoPlay=True,
            controls=False,   # oculta play/pausa, tiempo, volumen, pantalla completa
            muted=True,
            style={"width": "100%", "border-radius": "14px"},
        ),
    )

with col_side:
    @st.fragment(run_every=0.4)
    def panel_resultado():
        letra, conf, mano = "-", 0.0, False
        if ctx and ctx.video_processor:
            with ctx.video_processor.lock:
                letra = ctx.video_processor.letra
                conf = ctx.video_processor.confianza
                mano = ctx.video_processor.mano

        estado = (
            f'<div class="estado-ok"><div class="dot">✋</div>'
            f'<div><b>Mano detectada</b><br><small style="color:#888">Posición correcta</small></div></div>'
            if mano else
            f'<div class="estado-ok" style="background:#f7f7f7;border-color:#eee">'
            f'<div class="dot" style="background:#bbb">🖐</div>'
            f'<div><b style="color:#777">Esperando mano…</b><br>'
            f'<small style="color:#aaa">Muestra tu mano a la cámara</small></div></div>'
        )

        st.markdown(
            f"""
<div class="card">
    <div class="card-title">🧠 Resultado de la IA</div>
    <div class="result-label">Letra detectada</div>
    <div class="result-letter">{letra.upper()}</div>
    <div class="result-label">Confianza del modelo</div>
    <div class="bar-bg"><div class="bar-fill" style="width:{conf:.0f}%"></div></div>
    <div style="text-align:right;font-weight:700;color:#E30613;margin-top:4px">{conf:.0f}%</div>
    {estado}
</div>
""",
            unsafe_allow_html=True,
        )

    panel_resultado()

# ───────────────────────────── Estado del sistema (fila) ─────────────────────────────
st.write("")
st.markdown(
    f"""
<div class="card">
    <div class="card-title">🟢 Estado del sistema</div>
    <div class="status-row"><span>Cámara</span><span class="ok">Lista (pulsa START)</span></div>
    <div class="status-row"><span>Modelo</span><span class="val">SVM</span></div>
    <div class="status-row"><span>Señas disponibles</span><span class="val">{n_senas}</span></div>
</div>
""",
    unsafe_allow_html=True,
)

# ───────────────────────────── ¿Cómo funciona? ─────────────────────────────
st.write("")
st.markdown(
    """
<div class="card">
    <div class="card-title">⚙️ ¿Cómo funciona?</div>
    <div class="pipe">
        <div class="step"><div class="ico">📷</div><b>Cámara</b><small>Captura en tiempo real</small></div>
        <div class="arrow">→</div>
        <div class="step"><div class="ico">✋</div><b>MediaPipe Hands</b><small>21 puntos clave</small></div>
        <div class="arrow">→</div>
        <div class="step"><div class="ico">🔗</div><b>Landmarks</b><small>Extracción de rasgos</small></div>
        <div class="arrow">→</div>
        <div class="step"><div class="ico">🧠</div><b>Modelo SVM</b><small>Clasificación</small></div>
        <div class="arrow">→</div>
        <div class="step"><div class="ico">🅰️</div><b>Predicción</b><small>Letra en pantalla</small></div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ───────────────────────────── Estadísticas ─────────────────────────────
st.write("")
s1, s2, s3, s4 = st.columns(4)
for col, num, lbl in [
    (s1, "~30", "FPS de procesamiento"),
    (s2, "~0.08 s", "Tiempo de respuesta"),
    (s3, "42", "Coordenadas por mano"),
    (s4, str(n_senas), "Señas disponibles"),
]:
    col.markdown(f'<div class="stat"><div class="num">{num}</div><div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)

# ───────────────────────────── Footer ─────────────────────────────
st.markdown(
    """
<div class="footer-banner">
    🤟 <b>Construyamos juntos un Perú más inclusivo.</b> La tecnología nos ayuda a comunicarnos sin límites.
    <br><small>Universidad Privada del Norte (UPN) — Capstone Project Sistemas 2026</small>
</div>
""",
    unsafe_allow_html=True,
)
