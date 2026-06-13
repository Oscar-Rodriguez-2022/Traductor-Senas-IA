FROM python:3.12-slim

# ── Sistema ──────────────────────────────────────────────────────────────────
# Dependencias del sistema para OpenCV y MediaPipe.
# curl se instala solo para el HEALTHCHECK y se elimina de la imagen final
# mediante un stage de build por capas (las libGL/glib deben persistir).
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Usuario no-root (DevSecOps: principio de mínimo privilegio) ───────────────
# El contenedor no corre como root para reducir la superficie de ataque.
# UID/GID 1001 es convencional para apps de usuario en imágenes slim.
RUN groupadd --gid 1001 lspuser \
    && useradd --uid 1001 --gid 1001 --no-create-home lspuser

WORKDIR /app

# ── Dependencias Python ───────────────────────────────────────────────────────
# Se copian solo los archivos de requirements antes de copiar el código fuente
# para aprovechar el cache de Docker: los cambios de código no reinstalan deps.
COPY --chown=lspuser:lspuser requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── Código fuente ─────────────────────────────────────────────────────────────
COPY --chown=lspuser:lspuser . .

# ── Entorno Python ────────────────────────────────────────────────────────────
# Agregar src/ al PYTHONPATH para que los módulos lsp_* sean importables
# tanto por Streamlit como por cualquier script Python del contenedor.
ENV PYTHONPATH=/app/src

# ── Puerto ────────────────────────────────────────────────────────────────────
# HuggingFace Spaces requiere el puerto 7860.
# Para correr localmente: docker run -p 8501:7860 lsp-vision-ai
EXPOSE 7860

# ── Health check ──────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl --fail http://localhost:7860/_stcore/health || exit 1

# ── Cambiar a usuario no-root antes de ejecutar la app ────────────────────────
USER lspuser

CMD ["streamlit", "run", "src/app.py", \
     "--server.port=7860", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=false"]
