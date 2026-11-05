# ============================================================
# Stage 1: builder
# ============================================================
FROM python:3.12-slim AS builder

WORKDIR /build

# Simulator hanya pakai stdlib Python, tidak ada package eksternal
# requirements.txt sengaja dibuat kosong untuk konsistensi pola
COPY requirements.txt* ./

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip \
    && if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi


# ============================================================
# Stage 2: runtime
# ============================================================
FROM python:3.12-slim AS runtime

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy seluruh isi folder simulator
COPY . .

# Buat folder data untuk CSV fallback
RUN mkdir -p /app/data

CMD ["python", "main.py"]
