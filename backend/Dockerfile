# ============================================================
# Stage 1: builder
# Install semua dependensi ke dalam virtual environment
# ============================================================
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build tools yang dibutuhkan psycopg (C extension)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# ============================================================
# Stage 2: runtime
# Copy hanya venv + kode, tanpa gcc / build tools
# Hasilnya image jauh lebih kecil
# ============================================================
FROM python:3.12-slim AS runtime

WORKDIR /app

# Hanya runtime library, bukan dev tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Ambil venv yang sudah diisi dari stage builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy source code backend
COPY app/ ./app/

EXPOSE 3000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]
