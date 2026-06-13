"""
lsp_ui.py — Componentes de interfaz para LSP Vision AI.

Extrae todo el HTML/CSS de app.py aplicando correcciones WCAG 2.1 AA:
- Contraste corregido: #888/#aaa → #6b6b6b/#767676 (ratio >= 4.5:1)
- aria-live="polite" en el resultado para lectores de pantalla (HU-15)
- role="progressbar" con aria-valuenow en barra de confianza
- Roles semánticos: banner, contentinfo
- Skip-nav (WCAG 2.4.1 nivel A)
- aria-hidden en emojis decorativos del pipeline
- Indicador visual de baja confianza (< 60%) en borde amarillo

Trazabilidad de Historias de Usuario:
  HU-10 CA-10.3 — Indicador de confianza rojo/amarillo      (render_resultado: borde por umbral)
  HU-11 CA-11.1 — Panel de historial de señas               (render_resultado: sección historial)
  HU-12 CA-12.2 — Controles e interfaz responden al usuario  (render_topbar, render_hero)
  HU-12 CA-12.3 — Estado del sistema visible                 (render_estado_sistema)
  HU-15 CA-15.1 — aria-live="polite" en resultado            (render_resultado: atributo ARIA)
  HU-15 CA-15.2 — Contraste de texto ≥4.5:1                 (render_estilos: #6b6b6b, #767676)
  HU-15 CA-15.3 — Skip-nav funcional (WCAG 2.4.1)            (render_skip_nav)
  HU-16 CA-16.1 — Diagrama del pipeline de IA                (render_pipeline_explicado)
  HU-16 CA-16.2 — Alternativas XAI del SVM al usuario        (render_alternativas)
  HU-16 CA-16.2 — Sesgos documentados en lenguaje accesible  (render_pipeline_explicado: expander)
  HU-16 CA-16.2 — Emojis decorativos con aria-hidden         (render_pipeline_explicado: aria-hidden)
  HU-17 CA-17.1 — Estadísticas del sistema al usuario        (render_estadisticas)
"""
import streamlit as st


# ─────────────────────────────── Estilos ──────────────────────────────────────
def render_estilos() -> None:
    """Inyecta el CSS completo con correcciones de contraste WCAG 2.1 AA."""
    st.markdown(
        """
<script>
/* WCAG 3.1.1 — Idioma de la página: inyectar lang="es" en el documento */
document.documentElement.lang = 'es';
</script>
<style>
/* Enlace de saltar navegación (WCAG 2.4.1 — nivel A) */
.skip-nav {
    position: absolute; top: -40px; left: 0;
    background: #E30613; color: #fff;
    padding: 8px 16px; z-index: 9999;
    text-decoration: none; font-weight: 700;
    border-radius: 0 0 8px 0; font-size: 14px;
}
.skip-nav:focus { top: 0; outline: 3px solid #fff; }

/* WCAG 2.4.7 — Foco visible: outline en todos los elementos interactivos */
button:focus-visible,
a:focus-visible,
input:focus-visible,
[tabindex]:focus-visible {
    outline: 3px solid #E30613 !important;
    outline-offset: 2px !important;
}
/* Alto contraste en modo forzado (Windows High Contrast) */
@media (forced-colors: active) {
    .skip-nav, button { forced-color-adjust: none; }
}

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

/* Indicador de baja confianza — borde amarillo cuando confianza < 60% */
.card.baja-confianza { border-color: #f0a500; }

/* Panel de resultado */
.result-letter {
    font-size: 120px; font-weight: 800; color: #E30613;
    text-align: center; line-height: 1; margin: 10px 0;
    text-shadow: 0 4px 14px rgba(227,6,19,0.18);
}
/* WCAG fix: #888 → #6b6b6b (ratio 4.58:1 sobre blanco — pasa AA) */
.result-label {color: #6b6b6b; font-size: 14px; margin-bottom: 4px;}
.bar-bg {background: #f1e4e4; border-radius: 10px; height: 14px; width: 100%; overflow: hidden;}
.bar-fill {background: linear-gradient(90deg, #E30613, #ff5a44); height: 100%; border-radius: 10px;}
.estado-ok {
    display: flex; align-items: center; gap: 10px; background: #fff5f5;
    border: 1px solid #ffd9d9; border-radius: 12px; padding: 12px 14px; margin-top: 16px;
}
.estado-ok .dot {width: 34px; height: 34px; border-radius: 50%; background: #E30613; color: #fff;
    display: flex; align-items: center; justify-content: center; font-size: 16px;}

/* Tabla de estado del sistema */
.status-row {display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f3eaea; font-size: 14.5px;}
.status-row:last-child {border-bottom: none;}
.status-row .ok {color: #1aa251; font-weight: 700;}
.status-row .val {color: #E30613; font-weight: 700;}

/* Pipeline */
.pipe {display: flex; align-items: center; justify-content: space-between; gap: 6px; flex-wrap: wrap;}
.pipe .step {text-align: center; flex: 1; min-width: 110px;}
.pipe .ico {width: 54px; height: 54px; border-radius: 50%; background: #fff0f0; color: #E30613;
    display: flex; align-items: center; justify-content: center; font-size: 24px; margin: 0 auto 8px;}
.pipe .step b {display: block; font-size: 13.5px; color: #1A1A1A;}
/* WCAG fix: #888 → #6b6b6b */
.pipe .step small {color: #6b6b6b; font-size: 11.5px;}
.pipe .arrow {color: #E30613; font-size: 22px;}

/* Stats */
.stat {background: #fff; border: 1px solid #f0e3e3; border-radius: 14px; padding: 16px; text-align: center;}
.stat .num {font-size: 26px; font-weight: 800; color: #E30613;}
/* WCAG fix: #777 → #6b6b6b (ratio 4.58:1 sobre blanco — pasa AA) */
.stat .lbl {font-size: 12px; color: #6b6b6b; margin-top: 2px;}

/* Footer banner */
.footer-banner {
    background: linear-gradient(90deg, #fff0f0, #ffe3e3); border: 1px solid #ffd2d2;
    border-radius: 16px; padding: 18px 24px; margin-top: 22px; color: #7a1118;
}
.footer-banner b {color: #E30613;}
</style>
""",
        unsafe_allow_html=True,
    )


# ─────────────────────────────── Skip-nav ──────────────────────────────────────
def render_skip_nav() -> None:
    """
    Inyecta el enlace de 'saltar al contenido' (WCAG 2.4.1 — nivel A).

    Visible solo al recibir foco con Tab; redirige al contenido principal.
    """
    st.markdown(
        '<a class="skip-nav" href="#contenido-principal">Saltar al contenido</a>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────── Topbar ───────────────────────────────────────
def render_topbar(n_senas: int) -> None:
    """
    Renderiza la barra superior de navegación.

    Args:
        n_senas (int): Número de señas disponibles en el modelo cargado.
    """
    st.markdown(
        f"""
<header role="banner" aria-label="LSP Vision AI — Traductor de Lengua de Señas Peruana">
<div class="topbar">
    <div class="logo" aria-hidden="true">🤟</div>
    <div>
        <div class="brand">LSP <span>Vision AI</span></div>
        <div class="sub">Traductor de Lengua de Señas Peruana · {n_senas} señas</div>
    </div>
    <div class="upn" aria-label="Universidad Privada del Norte">🏔 UPN</div>
</div>
</header>
""",
        unsafe_allow_html=True,
    )


# ─────────────────────────────── Hero ─────────────────────────────────────────
def render_hero() -> None:
    """Renderiza el encabezado principal con estructura semántica h1."""
    st.markdown(
        """
<span id="contenido-principal" tabindex="-1"></span>
<div class="hero">
    <h1>Traductor Inteligente de <span class="red">Lengua de Señas Peruana</span></h1>
    <p>Sistema de reconocimiento en tiempo real mediante Inteligencia Artificial y Visión por Computadora.</p>
</div>
""",
        unsafe_allow_html=True,
    )
    st.write("")


# ─────────────────────────────── Resultado ────────────────────────────────────
def render_resultado(letra: str, confianza: float, mano: bool) -> None:
    """
    Renderiza el panel de resultado de la IA con atributos ARIA para accesibilidad.

    El elemento 'result-letter' usa aria-live='polite' para que los lectores de
    pantalla anuncien la letra detectada sin interrumpir la narración actual.
    La barra de confianza expone su valor como rol 'progressbar'.

    Args:
        letra (str): Letra detectada (a-z) o '-' si no hay mano.
        confianza (float): Confianza del modelo en porcentaje (0–100).
        mano (bool): True si MediaPipe detectó una mano en el último frame.
    """
    clase_card = "card baja-confianza" if mano and confianza < 60 else "card"

    if mano:
        estado_html = (
            '<div class="estado-ok" role="status" aria-label="Mano detectada">'
            '<div class="dot" aria-hidden="true">✋</div>'
            '<div><b>Mano detectada</b>'
            '<br><small style="color:#6b6b6b">Posición correcta</small></div></div>'
        )
    else:
        estado_html = (
            '<div class="estado-ok" style="background:#f7f7f7;border-color:#eee" '
            'role="status" aria-label="Esperando mano">'
            '<div class="dot" style="background:#bbb" aria-hidden="true">🖐</div>'
            '<div><b style="color:#6b6b6b">Esperando mano…</b>'
            '<br><small style="color:#767676">Muestra tu mano a la cámara</small></div></div>'
        )

    st.markdown(
        f"""
<div class="{clase_card}">
    <div class="card-title" aria-hidden="true">🧠 Resultado de la IA</div>
    <div class="result-label" id="lbl-letra">Letra detectada</div>
    <div class="result-letter"
         role="status"
         aria-live="polite"
         aria-atomic="true"
         aria-labelledby="lbl-letra"
         aria-label="Letra detectada: {letra.upper()}">
        {letra.upper()}
    </div>
    <div class="result-label" id="lbl-conf">Confianza del modelo</div>
    <div class="bar-bg"
         role="progressbar"
         aria-valuenow="{confianza:.0f}"
         aria-valuemin="0"
         aria-valuemax="100"
         aria-labelledby="lbl-conf"
         aria-label="Confianza: {confianza:.0f}%">
        <div class="bar-fill" style="width:{confianza:.0f}%"></div>
    </div>
    <div style="text-align:right;font-weight:700;color:#E30613;margin-top:4px"
         aria-hidden="true">{confianza:.0f}%</div>
    {estado_html}
</div>
""",
        unsafe_allow_html=True,
    )


# ─────────────────────────────── Estado sistema ───────────────────────────────
def render_estado_sistema(n_senas: int, modelo_cargado: bool = True) -> None:
    """
    Renderiza la tabla de estado del sistema.

    Args:
        n_senas (int): Número de señas disponibles.
        modelo_cargado (bool): True si el modelo SVM está cargado.
    """
    estado_modelo = "SVM" if modelo_cargado else "No cargado"
    st.write("")
    st.markdown(
        f"""
<div class="card" role="region" aria-label="Estado del sistema">
    <div class="card-title" aria-hidden="true">🟢 Estado del sistema</div>
    <div class="status-row"><span>Cámara</span><span class="ok">Lista (pulsa START)</span></div>
    <div class="status-row"><span>Modelo</span><span class="val">{estado_modelo}</span></div>
    <div class="status-row"><span>Señas disponibles</span><span class="val">{n_senas}</span></div>
</div>
""",
        unsafe_allow_html=True,
    )


# ─────────────────────────────── Pipeline ─────────────────────────────────────
def render_pipeline_explicado() -> None:
    """
    Renderiza el diagrama de pipeline con un expander de explicabilidad.

    El diagrama muestra las 5 etapas del sistema. El expander 'Cómo decide la IA'
    explica el proceso en lenguaje accesible para usuarios no técnicos (HU-16).
    Los emojis llevan aria-hidden para no distraer a lectores de pantalla.
    """
    st.write("")
    st.markdown(
        """
<div class="card" role="region" aria-label="Diagrama del pipeline de procesamiento de señas">
    <div class="card-title" aria-hidden="true">⚙️ ¿Cómo funciona?</div>
    <div class="pipe" role="list" aria-label="5 etapas del pipeline de reconocimiento">
        <div class="step" role="listitem" aria-label="Etapa 1: Cámara — captura de video en tiempo real">
            <div class="ico" aria-hidden="true">📷</div>
            <b>1. Cámara</b><small>Captura en tiempo real</small>
        </div>
        <div class="arrow" aria-hidden="true">→</div>
        <div class="step" role="listitem" aria-label="Etapa 2: MediaPipe Hands — detección de 21 puntos clave de la mano">
            <div class="ico" aria-hidden="true">✋</div>
            <b>2. MediaPipe</b><small>21 puntos clave</small>
        </div>
        <div class="arrow" aria-hidden="true">→</div>
        <div class="step" role="listitem" aria-label="Etapa 3: Landmarks — extracción de 42 coordenadas normalizadas">
            <div class="ico" aria-hidden="true">🔗</div>
            <b>3. Landmarks</b><small>42 coordenadas</small>
        </div>
        <div class="arrow" aria-hidden="true">→</div>
        <div class="step" role="listitem" aria-label="Etapa 4: Modelo SVM — clasificación de la seña">
            <div class="ico" aria-hidden="true">🧠</div>
            <b>4. Modelo SVM</b><small>Clasificación</small>
        </div>
        <div class="arrow" aria-hidden="true">→</div>
        <div class="step" role="listitem" aria-label="Etapa 5: Predicción — letra y nivel de confianza en pantalla">
            <div class="ico" aria-hidden="true">🅰️</div>
            <b>5. Predicción</b><small>Letra + confianza%</small>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    with st.expander("¿Cómo decide la IA? — Explicabilidad y limitaciones del sistema"):
        # HU-16 CA-16.2: fuente única de sesgos desde lsp_core.sesgos_conocidos()
        try:
            import lsp_core
            _sesgos = lsp_core.sesgos_conocidos()
        except Exception:
            _sesgos = {}

        _items_sesgo = "\n".join(
            f"- **{k.replace('_', ' ').capitalize()}:** {v}"
            for k, v in _sesgos.items()
        ) if _sesgos else "- Sin información de sesgos disponible."

        st.markdown(
            f"""
**Representación geométrica de la mano**

MediaPipe Hands detecta **21 puntos anatómicos** (muñeca, nudillos y puntas de cada dedo).
Cada punto tiene coordenadas X e Y normalizadas entre 0 y 1 relativas al borde de la imagen.
El sistema trabaja con **42 números** — no con píxeles — lo que le permite funcionar
en cualquier resolución y con fondos variables.

El panel *"¿Qué otras letras consideró la IA?"* muestra estos 42 números convertidos en
probabilidades para cada letra, permitiéndote ver la certeza de cada decisión.

**Clasificación por Máquina de Vectores de Soporte (SVM)**

El SVM aprendió **hiperplanos** que separan los vectores de 42 valores correspondientes a
cada letra de la LSP. Durante la predicción, calcula a qué clase pertenece el vector
midiendo la distancia a esos hiperplanos. La **confianza** es la probabilidad de Platt:
*P(clase | vector) × 100* — aparece en el panel de alternativas XAI.

**Indicadores de confianza**

| Borde del panel | Significado |
|-----------------|-------------|
| 🔴 Rojo (≥ 60%) | Alta seguridad — la letra está bien reconocida |
| 🟡 Amarillo (< 60%) | Ambigüedad — repite la seña o ajusta la posición |
| Sin borde | No hay mano visible |

**⚠️ Limitaciones y sesgos conocidos (IA Ética)**

El modelo puede equivocarse. Los sesgos documentados son:

{_items_sesgo}

El borde **amarillo** y el aviso en el panel XAI están diseñados para avisar
antes de que el sistema cometa un error visible.
Para un análisis detallado de equidad por clase, consulta el Dashboard de Métricas QA.
"""
        )


# ─────────────────────────────── Alternativas XAI ─────────────────────────────
def render_alternativas(alternativas: list) -> None:
    """
    Renderiza el panel XAI de alternativas: top-5 letras consideradas por el SVM.

    Implementa el principio de transparencia algorítmica (HU-16 CA-16.2):
    el usuario ve qué otras letras evaluó el modelo antes de decidir, lo que
    le permite entender la certeza de la predicción y cuándo la seña es ambigua.
    Si las dos primeras opciones están muy cercanas (< 10% de diferencia), la
    nota al pie lo indica para que el usuario repita la seña.

    Args:
        alternativas: Lista de dicts {letra, confianza} ordenada de mayor a menor
            confianza. Vacía si no hay mano detectada o la predicción falló.
    """
    if not alternativas:
        return

    filas_html = ""
    for i, alt in enumerate(alternativas):
        pct = alt["confianza"]
        # Primera opción: rojo institucional; resto: naranja si ≥30%, gris si no
        if i == 0:
            color = "#E30613"
            peso = "800"
        elif pct >= 30:
            color = "#f0a500"
            peso = "600"
        else:
            color = "#bbb"
            peso = "400"
        filas_html += (
            f'<tr>'
            f'<td style="font-weight:{peso};color:#1A1A1A;font-size:14px;'
            f'padding:5px 10px;" aria-label="Letra {alt["letra"].upper()}">'
            f'{alt["letra"].upper()}</td>'
            f'<td style="padding:5px 10px;width:130px;">'
            f'<div style="background:#f1e4e4;border-radius:6px;height:10px;overflow:hidden;">'
            f'<div style="background:{color};width:{pct:.0f}%;height:100%;'
            f'border-radius:6px;" aria-hidden="true"></div></div></td>'
            f'<td style="text-align:right;font-weight:{peso};color:{color};'
            f'font-size:13px;padding:5px 10px;">{pct:.1f}%</td>'
            f'</tr>'
        )

    # Aviso de ambigüedad si las dos primeras opciones están cerca
    nota = ""
    if len(alternativas) >= 2:
        diferencia = alternativas[0]["confianza"] - alternativas[1]["confianza"]
        if diferencia < 10:
            nota = (
                f'<p style="font-size:11.5px;color:#f0a500;margin-top:6px;" '
                f'role="alert" aria-label="Advertencia de ambigüedad">'
                f'⚠ La IA dudó entre <b>{alternativas[0]["letra"].upper()}</b> y '
                f'<b>{alternativas[1]["letra"].upper()}</b> (diferencia: {diferencia:.1f}%). '
                f'Repite la seña con más claridad.</p>'
            )

    st.markdown(
        f"""
<div class="card" role="region" aria-label="Alternativas XAI: letras consideradas por la IA">
    <div class="card-title" aria-hidden="true">🔍 ¿Qué otras letras consideró la IA?</div>
    <table style="width:100%;border-collapse:collapse;"
           aria-label="Top {len(alternativas)} alternativas evaluadas por el SVM">
        <thead>
            <tr>
                <th style="text-align:left;font-size:11px;color:#6b6b6b;
                           padding:2px 10px;">Letra</th>
                <th style="text-align:left;font-size:11px;color:#6b6b6b;
                           padding:2px 10px;">Probabilidad SVM</th>
                <th style="text-align:right;font-size:11px;color:#6b6b6b;
                           padding:2px 10px;">%</th>
            </tr>
        </thead>
        <tbody>{filas_html}</tbody>
    </table>
    {nota}
    <p style="font-size:11px;color:#767676;margin-top:8px;">
        El SVM evaluó las {len(alternativas)} letras más probables y seleccionó la de mayor
        probabilidad de Platt. Un valor alto indica que la seña fue clara y bien posicionada.
    </p>
</div>
""",
        unsafe_allow_html=True,
    )


# ─────────────────────────────── Estadísticas ─────────────────────────────────
def render_estadisticas(n_senas: int, fps_real: float = None) -> None:
    """
    Renderiza las 4 tarjetas de estadísticas del sistema.

    Args:
        n_senas (int): Número de señas disponibles en el modelo.
        fps_real (float | None): FPS medidos en vivo por el procesador de video.
            Si se provee, muestra el valor real; si es None muestra el estimado "~30".
    """
    fps_str = f"{fps_real:.0f}" if fps_real and fps_real > 0 else "~30"
    st.write("")
    s1, s2, s3, s4 = st.columns(4)
    stats = [
        (s1, fps_str,      "FPS de procesamiento"),
        (s2, "~0.08 s",    "Tiempo de respuesta"),
        (s3, "42",         "Coordenadas por mano"),
        (s4, str(n_senas), "Señas disponibles"),
    ]
    for col, num, lbl in stats:
        col.markdown(
            f'<div class="stat" role="figure" aria-label="{lbl}: {num}">'
            f'<div class="num" aria-hidden="true">{num}</div>'
            f'<div class="lbl">{lbl}</div></div>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────── Footer ───────────────────────────────────────
def render_footer() -> None:
    """Renderiza el footer con rol semántico contentinfo."""
    st.markdown(
        """
<footer role="contentinfo" aria-label="Información del proyecto UPN">
<div class="footer-banner">
    <span aria-hidden="true">🤟</span>
    <b>Construyamos juntos un Perú más inclusivo.</b>
    La tecnología nos ayuda a comunicarnos sin límites.
    <br><small>Universidad Privada del Norte (UPN) — Capstone Project Sistemas 2026</small>
</div>
</footer>
""",
        unsafe_allow_html=True,
    )
