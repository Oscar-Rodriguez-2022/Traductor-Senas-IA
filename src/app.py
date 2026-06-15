"""
LSP Vision AI — Traductor de Lengua de Señas Peruana
Universidad Privada del Norte (UPN) — Capstone Project Sistemas 2026

Orquestador principal de la aplicación Streamlit. Delega:
  - Autenticación de sesión  → lsp_auth.login_requerido()
  - Log de auditoría         → lsp_audit.registrar_acceso()
  - Componentes de UI/HTML   → lsp_ui.*
  - Procesamiento de video   → lsp_video.Traductor
  - Lógica de modelo         → lsp_core.*

Probar local:  streamlit run src/app.py

Trazabilidad de Historias de Usuario:
  HU-08 CA-08.1 — Captura de video en tiempo real       (webrtc_streamer)
  HU-10 CA-10.1 — Carga del modelo al iniciar           (cargar_modelo)
  HU-10 CA-10.2 — Panel de resultado actualizado ≤0.4 s (panel_resultado fragment)
  HU-11 CA-11.1 — Historial de señas                    (lsp_ui.render_resultado)
  HU-12 CA-12.1 — Integración completa de módulos       (orquestación de los 5 módulos)
  HU-13 CA-13.4 — Guard de autenticación                (lsp_auth.login_requerido)
  HU-14 CA-14.1 — Registro de PAGINA_VISITADA           (lsp_audit.registrar_acceso)
  HU-15 CA-15.3 — Skip-nav y estilos WCAG               (lsp_ui.render_estilos / render_skip_nav)
  HU-16 CA-16.1 — Diagrama del pipeline de IA           (lsp_ui.render_pipeline_explicado)
  HU-16 CA-16.2 — Panel XAI de alternativas del SVM     (lsp_ui.render_alternativas)
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import warnings
warnings.filterwarnings("ignore")

import joblib
import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration, VideoHTMLAttributes

import lsp_auth
import lsp_audit
import lsp_ui
from lsp_video import Traductor

# ─────────────────────────── Configuración general ────────────────────────────
st.set_page_config(
    page_title="LSP Vision AI — Traductor de Señas",
    page_icon="🤟",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_resource
def cargar_modelo():
    """Carga el modelo SVM desde disco. Retorna None si no existe."""
    if not os.path.exists("modelo.pkl"):
        return None
    return joblib.load("modelo.pkl")


# ─────────────────────────── Guard de autenticación ───────────────────────────
# Si el usuario no está autenticado, se muestra el formulario de login y se detiene.
if not lsp_auth.login_requerido(st.session_state):
    st.stop()

# Solo registra la visita una vez por sesión (no en cada rerun del fragment)
if not st.session_state.get("_pagina_registrada"):
    lsp_audit.registrar_acceso("PAGINA_VISITADA", st_state=st.session_state)
    st.session_state["_pagina_registrada"] = True

# ─────────────────────────── Carga del modelo ─────────────────────────────────
modelo = cargar_modelo()

# ─────────────────────────── UI estática ──────────────────────────────────────
lsp_ui.render_estilos()
lsp_ui.render_skip_nav()

n_senas = len(modelo.classes_) if modelo is not None else 0
lsp_ui.render_topbar(n_senas)

if modelo is None:
    st.error("No se encontró 'modelo.pkl'. Ejecuta primero `python entrenar_modelo.py`.")
    st.stop()

lsp_ui.render_hero()

# ─────────────────────────── Layout principal ─────────────────────────────────
@st.cache_resource(ttl=3600)
def _get_rtc_config():
    try:
        import requests as _req
        app_url = st.secrets.get("METERED_APP_URL", "")
        api_key = st.secrets.get("METERED_SECRET_KEY", "")
        if app_url and api_key:
            resp = _req.get(
                f"https://{app_url}/api/v1/turn/credentials?apiKey={api_key}",
                timeout=5,
            )
            if resp.status_code == 200:
                return RTCConfiguration({"iceServers": resp.json()})
    except Exception:
        pass
    return RTCConfiguration({
        "iceServers": [
            {"urls": ["stun:stun.l.google.com:19302"]},
            {"urls": ["stun:stun1.l.google.com:19302"]},
            {"urls": ["stun:stun2.l.google.com:19302"]},
            {
                "urls": ["turn:openrelay.metered.ca:443?transport=tcp"],
                "username": "openrelayproject",
                "credential": "openrelayproject",
            },
        ]
    })

col_main, col_side = st.columns([3, 2], gap="large")

with col_main:
    st.markdown('<div class="card-title" aria-hidden="true">📷 Cámara en vivo</div>', unsafe_allow_html=True)
    ctx = webrtc_streamer(
        key="lsp",
        video_processor_factory=lambda: Traductor(modelo),
        rtc_configuration=_get_rtc_config(),
        media_stream_constraints={"video": True, "audio": False},
        video_html_attrs=VideoHTMLAttributes(
            autoPlay=True,
            controls=False,
            muted=True,
            style={"width": "100%", "border-radius": "14px"},
        ),
    )

with col_side:
    @st.fragment(run_every=0.4)
    def panel_resultado():
        """Actualiza el panel de resultado y XAI cada 0.4 s con los datos del procesador."""
        # HU-10 CA-10.2: lectura thread-safe del estado del video processor
        letra, conf, mano, alternativas = "-", 0.0, False, []
        if ctx and ctx.video_processor:
            with ctx.video_processor.lock:
                letra = ctx.video_processor.letra
                conf = ctx.video_processor.confianza
                mano = ctx.video_processor.mano
                alternativas = list(ctx.video_processor.alternativas)
        lsp_ui.render_resultado(letra, conf, mano)
        # HU-16 CA-16.2: mostrar panel XAI solo cuando hay predicción activa
        if alternativas:
            lsp_ui.render_alternativas(alternativas)

    panel_resultado()

# ─────────────────────────── Secciones informativas ───────────────────────────
lsp_ui.render_estado_sistema(n_senas, modelo_cargado=True)
lsp_ui.render_pipeline_explicado()

fps_real = None
if ctx and ctx.video_processor:
    with ctx.video_processor.lock:
        fps_real = ctx.video_processor.fps

lsp_ui.render_estadisticas(n_senas, fps_real=fps_real)
lsp_ui.render_footer()
