<<<<<<< HEAD
# ─── Dockerfile optimizado para CPU (Ryzen 5, sin NVIDIA) ────────────────────

# ── Etapa 1: builder ──────────────────────────────────────────────────────────
=======
# ─── SSPA VSO — Dockerfile (CPU, Enterprise Edition) ─────────────────────────

# ── Stage 1: builder ──────────────────────────────────────────────────────────
>>>>>>> master
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

<<<<<<< HEAD
# torch CPU-only primero (evita runtime CUDA ~2 GB)
=======
# torch CPU-only first (avoids ~2 GB CUDA runtime)
>>>>>>> master
RUN pip install --upgrade pip && \
    pip install \
        torch==2.3.1+cpu \
        torchvision==0.18.1+cpu \
        torchaudio==2.3.1+cpu \
        --index-url https://download.pytorch.org/whl/cpu

COPY app/requirements.txt .
RUN pip install -r requirements.txt


<<<<<<< HEAD
# ── Etapa 2: imagen final ─────────────────────────────────────────────────────
=======
# ── Stage 2: runtime image ────────────────────────────────────────────────────
>>>>>>> master
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TOKENIZERS_PARALLELISM=false \
    OMP_NUM_THREADS=6 \
    MKL_NUM_THREADS=6

RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app
COPY app/ .

<<<<<<< HEAD
RUN useradd -m -u 1000 vsobot \
    && mkdir -p /app/vector_db \
=======
# Create required directories and non-root user
RUN useradd -m -u 1000 vsobot \
    && mkdir -p /app/vector_db /app/prompts \
>>>>>>> master
    && chown -R vsobot:vsobot /app

USER vsobot

<<<<<<< HEAD
# Bot Telegram — health indirecto: el proceso está vivo si no hay exit
# La API de Telegram detecta bots desconectados via long-polling timeout
# Verificamos que el proceso Python está activo y el módulo SSPAIntelligence inicializado
HEALTHCHECK --interval=60s --timeout=10s --start-period=120s --retries=3 \
    CMD python -c \
        "import os, sys; \
         pid_file = '/tmp/vso_running'; \
         sys.exit(0 if os.path.exists(pid_file) else 1)" || \
    python -c "import asyncio, aiomqtt; print('vso alive')" 2>/dev/null || exit 1
=======
# HEALTHCHECK: bot writes /tmp/vso_running on successful startup
# If the file is absent, the container is unhealthy
HEALTHCHECK --interval=60s --timeout=10s --start-period=180s --retries=3 \
    CMD test -f /tmp/vso_running || exit 1
>>>>>>> master

CMD ["python", "main.py"]
