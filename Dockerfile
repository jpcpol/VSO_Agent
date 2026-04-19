# ─── SSPA VSO — Dockerfile (CPU, Enterprise Edition) ─────────────────────────

# ── Stage 1: builder ──────────────────────────────────────────────────────────
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

# torch CPU-only first (avoids ~2 GB CUDA runtime)
RUN pip install --upgrade pip && \
    pip install \
        torch==2.3.1+cpu \
        torchvision==0.18.1+cpu \
        torchaudio==2.3.1+cpu \
        --index-url https://download.pytorch.org/whl/cpu

COPY app/requirements.txt .
RUN pip install -r requirements.txt


# ── Stage 2: runtime image ────────────────────────────────────────────────────
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

# Create required directories and non-root user
RUN useradd -m -u 1000 vsobot \
    && mkdir -p /app/vector_db /app/prompts \
    && chown -R vsobot:vsobot /app

USER vsobot

# HEALTHCHECK: bot writes /tmp/vso_running on successful startup
# If the file is absent, the container is unhealthy
HEALTHCHECK --interval=60s --timeout=10s --start-period=180s --retries=3 \
    CMD test -f /tmp/vso_running || exit 1

CMD ["python", "main.py"]
