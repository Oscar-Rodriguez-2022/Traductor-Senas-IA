"""
Fase 19 — Dashboard de métricas QA (página secundaria de la web).
Muestra los resultados de las pruebas (reportes/) y recursos en vivo.
Se abre desde el menú lateral de la app, o en la URL .../Metricas_QA

Requiere autenticación previa (HU-17 CA-17.3): si el token de sesión
no es válido, redirige al formulario de login de la página principal.
"""
import os
import csv
import json

import streamlit as st
import lsp_auth
import lsp_audit

st.set_page_config(page_title="Métricas QA — LSP", page_icon="📊", layout="wide")

# ── Guard de autenticación (HU-17 CA-17.3) ──────────────────────────────────
if not lsp_auth.login_requerido(st.session_state):
    st.stop()

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTES = os.path.join(RAIZ, "reportes")

st.title("📊 Dashboard de Calidad de Software")
st.caption("Resultados de la suite de pruebas — Traductor LSP (UPN)")


def leer_csv(nombre):
    ruta = os.path.join(REPORTES, nombre)
    if not os.path.exists(ruta):
        return None
    with open(ruta, encoding="utf-8", newline="") as f:
        filas = list(csv.reader(f))
    return filas


def mostrar_tabla(titulo, nombre):
    filas = leer_csv(nombre)
    st.subheader(titulo)
    if not filas or len(filas) < 2:
        st.info("Aún no generado. Ejecuta la suite (QA.bat).")
        return
    encabezado = filas[0]
    n_cols = len(encabezado)
    datos = [fila for fila in filas[1:] if len(fila) >= n_cols]
    if not datos:
        st.info("El archivo existe pero no tiene filas de datos.")
        return
    st.dataframe(
        {col: [fila[i] for fila in datos] for i, col in enumerate(encabezado)},
        use_container_width=True,
    )


# ── Tarjetas resumen ──
meta_path = os.path.join(REPORTES, "metricas.json")
if os.path.exists(meta_path):
    with open(meta_path, encoding="utf-8") as f:
        m = json.load(f)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Accuracy", f"{m.get('accuracy', 0)*100:.1f}%")
    c2.metric("Precision", f"{m.get('precision_macro', 0)*100:.1f}%")
    c3.metric("Recall", f"{m.get('recall_macro', 0)*100:.1f}%")
    c4.metric("F1-Score", f"{m.get('f1_macro', 0)*100:.1f}%")
else:
    st.info("Ejecuta `qa/evaluate.py` (o QA.bat) para ver las métricas del modelo.")

# ── Recursos en vivo ──
st.subheader("🖥 Recursos en vivo")
try:
    import psutil
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    r1, r2 = st.columns(2)
    r1.metric("CPU", f"{cpu:.0f}%")
    r2.metric("RAM usada", f"{ram.percent:.0f}%")
    if st.button("🔄 Actualizar"):
        st.rerun()
except Exception:
    st.caption("psutil no disponible en este entorno.")

# ── Tablas de reportes ──
mostrar_tabla("⚡ Rendimiento por etapa (ms)", "benchmark.csv")
mostrar_tabla("🎬 FPS sostenidos", "fps.csv")
mostrar_tabla("🎯 Métricas por letra", "metricas_por_clase.csv")
mostrar_tabla("🔁 Validación cruzada", "cross_validation.csv")
mostrar_tabla("🏋️ Test de estrés", "stress.csv")
mostrar_tabla("🛡️ Robustez ante condiciones adversas", "robustez.csv")
mostrar_tabla("💾 Consumo de RAM y CPU", "recursos.csv")

png = os.path.join(REPORTES, "matriz_confusion.png")
if os.path.exists(png):
    st.subheader("🔢 Matriz de confusión")
    st.image(png, width=560)

# ── Log de auditoría de la sesión (HU-17 CA-17.3) ───────────────────────────
st.subheader("🔐 Log de auditoría (últimas 20 entradas de la sesión)")
entradas = lsp_audit.leer_log_reciente(n=20)
if not entradas:
    st.info("Sin eventos registrados aún. Usa la aplicación para generar entradas.")
else:
    st.dataframe(
        {
            "Timestamp": [e.get("ts", "") for e in entradas],
            "Evento": [e.get("evento", "") for e in entradas],
            "Sesión (hash)": [e.get("sesion", "") for e in entradas],
            "Detalle": [e.get("detalle", "") for e in entradas],
        },
        use_container_width=True,
    )
    st.caption("El campo 'Sesión' es un hash SHA-256[:8] — no identifica al usuario (GDPR Art. 25).")
