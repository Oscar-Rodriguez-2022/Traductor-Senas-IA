"""
Fase 18 — Consolida todos los reportes (CSV/PNG) en un PDF y un HTML
listos para anexar a la tesis / sustentación.

Uso:  python qa/generar_reportes.py
"""
import os
import sys
import csv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from qa._utils import REPORTES, banner


def leer_csv(nombre):
    ruta = os.path.join(REPORTES, nombre)
    if not os.path.exists(ruta):
        return None
    with open(ruta, encoding="utf-8") as f:
        return list(csv.reader(f))


TABLAS = [
    ("1. Rendimiento por etapa (ms)", "benchmark.csv"),
    ("2. FPS sostenidos", "fps.csv"),
    ("3. Métricas globales del modelo", "metricas_resumen.csv"),
    ("4. Métricas por letra", "metricas_por_clase.csv"),
    ("5. Validación cruzada K-Fold", "cross_validation.csv"),
    ("6. Test de estrés", "stress.csv"),
    ("7. Consumo de RAM y CPU", "recursos.csv"),
    ("8. Robustez ante condiciones adversas", "robustez.csv"),
]


def generar_html():
    partes = [
        "<html><head><meta charset='utf-8'><title>Reporte QA — Traductor LSP</title>",
        "<style>body{font-family:Arial;margin:30px;color:#222}"
        "h1{color:#E30613}h2{color:#b00410;border-bottom:2px solid #E30613;padding-bottom:4px}"
        "table{border-collapse:collapse;margin:10px 0 24px}td,th{border:1px solid #ccc;padding:6px 12px;font-size:14px}"
        "th{background:#E30613;color:#fff}tr:nth-child(even){background:#fbf3f3}img{max-width:560px}</style></head><body>",
        "<h1>🤟 Reporte de Calidad de Software — Traductor LSP</h1>",
        "<p>Universidad Privada del Norte (UPN) — Capstone Project Sistemas</p>",
    ]
    for titulo, archivo in TABLAS:
        datos = leer_csv(archivo)
        if not datos:
            continue
        partes.append(f"<h2>{titulo}</h2><table>")
        for i, fila in enumerate(datos):
            tag = "th" if i == 0 else "td"
            partes.append("<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in fila) + "</tr>")
        partes.append("</table>")
    if os.path.exists(os.path.join(REPORTES, "matriz_confusion.png")):
        partes.append("<h2>9. Matriz de confusión</h2><img src='matriz_confusion.png'>")
    partes.append("</body></html>")
    ruta = os.path.join(REPORTES, "REPORTE_QA.html")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(partes))
    return ruta


def generar_pdf():
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_pdf import PdfPages
    except Exception as e:
        print(f"  (PDF omitido: {e})")
        return None

    ruta = os.path.join(REPORTES, "REPORTE_QA.pdf")
    with PdfPages(ruta) as pdf:
        # Portada
        fig = plt.figure(figsize=(8.27, 11.69))
        fig.text(0.5, 0.7, "Reporte de Calidad de Software", ha="center", fontsize=20, color="#E30613", weight="bold")
        fig.text(0.5, 0.64, "Traductor de Lengua de Señas Peruana (LSP)", ha="center", fontsize=13)
        fig.text(0.5, 0.60, "Universidad Privada del Norte — Capstone Project", ha="center", fontsize=11)
        meta = leer_csv("metricas_resumen.csv")
        if meta and len(meta) > 1:
            fig.text(0.5, 0.45, "Resumen de métricas", ha="center", fontsize=13, weight="bold")
            for i, (k, v) in enumerate(zip(meta[0], meta[1])):
                fig.text(0.5, 0.40 - i * 0.03, f"{k}: {v}", ha="center", fontsize=11)
        plt.axis("off")
        pdf.savefig(fig)
        plt.close(fig)

        # Una página por tabla
        for titulo, archivo in TABLAS:
            datos = leer_csv(archivo)
            if not datos:
                continue
            fig, ax = plt.subplots(figsize=(8.27, 11.69))
            ax.axis("off")
            ax.set_title(titulo, fontsize=14, color="#E30613", weight="bold", pad=20)
            tabla = ax.table(cellText=datos[1:], colLabels=datos[0], loc="upper center", cellLoc="center")
            tabla.auto_set_font_size(False)
            tabla.set_fontsize(8)
            tabla.scale(1, 1.5)
            for (r, c), celda in tabla.get_celld().items():
                if r == 0:
                    celda.set_facecolor("#E30613")
                    celda.set_text_props(color="white", weight="bold")
            pdf.savefig(fig)
            plt.close(fig)

        # Matriz de confusión
        png = os.path.join(REPORTES, "matriz_confusion.png")
        if os.path.exists(png):
            import matplotlib.image as mpimg
            fig, ax = plt.subplots(figsize=(8.27, 11.69))
            ax.imshow(mpimg.imread(png))
            ax.axis("off")
            ax.set_title("Matriz de Confusión", fontsize=14, color="#E30613", weight="bold")
            pdf.savefig(fig)
            plt.close(fig)
    return ruta


def main():
    banner("FASE 18 — REPORTE CONSOLIDADO (PDF + HTML)")
    html = generar_html()
    print(f"  [OK] HTML: {html}")
    pdf = generar_pdf()
    if pdf:
        print(f"  [OK] PDF : {pdf}")
    print("\nLos CSV y PNG individuales también están en la carpeta reportes/.")


if __name__ == "__main__":
    main()
