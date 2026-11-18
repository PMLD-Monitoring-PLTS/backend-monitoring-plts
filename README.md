# PLTS Monitoring System — Backend & Ingestion API

Sistem backend berbasis **FastAPI** dan **TimescaleDB** untuk monitoring kondisi kelistrikan Pembangkit Listrik Tenaga Surya (PLTS) secara *real-time*. Sistem ini menyediakan API terotentikasi untuk kebutuhan **Web Dashboard** dan **Telegram Bot**, dilengkapi dengan modul **IoT Simulator / Dummy Data Generator** yang mereplikasi perilaku mikrokontroler (ESP8266) dengan mekanisme *fallback* ke CSV lokal.

Proyek ini dikembangkan sebagai bagian dari **Proyek Mandiri Lintas Disiplin Ilmu (PMLD)**.

---

## 🏗️ Arsitektur Sistem

```text
┌─────────────────────────────────┐
│     ESP8266 / IoT Simulator    │
│  (Mengirim data tiap 60 detik)  │
└────────────────┬────────────────┘
                 │ HTTP POST (X-Device-API-Key)
                 ▼
┌────────────────────────────────────────────────────────┐
│               FastAPI Ingestion Engine                 │
│                 (Port 3000 /api/v1)                    │
└───────┬──────────────────────────────┬─────────────────┘
        │                              │
        │ Tulis Data (Hypertable)      │ Baca Data (JWT Protected)
        ▼                              ▼
┌─────────────────────────┐    ┌─────────────────────────────────┐
│   TimescaleDB (PG 17)   │    │     Web Dashboard & Telegram    │
│ (Time-Series Partition) │    │      (/latest & /history)       │
└─────────────────────────┘    └─────────────────────────────────┘
        ▲
        │ (Koneksi DBeaver via Port 5433)
```

---

## 🚀 Tech Stack

| Kategori | Teknologi | Deskripsi |
| :--- | :--- | :--- |
| **Framework** | [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12) | REST API performa tinggi, async-ready, dokumentasi otomatis OpenAPI/Swagger. |
| **Server ASGI** | [Uvicorn](https://www.uvicorn.org/) | Server ASGI standar industri untuk menjalankan aplikasi FastAPI. |
| **Database** | [TimescaleDB](https://www.timescale.com/) (PostgreSQL 17) | Database relasional time-series dengan fitur *Hypertables* dan partisi otomatis. |
| **ORM & Driver** | SQLAlchemy 2.0 & Psycopg 3 | Database toolkit modern dengan driver PostgreSQL generasi terbaru berbasis C/binary. |
| **Autentikasi** | JWT (python-jose) & Bcrypt | Keamanan ganda: API Key untuk mikrokontroler/simulator, JWT Bearer untuk user dashboard. |
| **Validasi Data** | Pydantic v2 | Validasi skema request/response dan penanganan zona waktu ISO 8601 (WIB / UTC+7). |
| **Container** | Docker & Docker Compose | Orkestrasi multi-container dengan *Multi-Stage Builds* untuk efisiensi ukuran image. |
| **Testing** | Pytest & HTTPX | Pengujian otomatis end-to-end (Auth, Ingestion, Realtime, & History). |
| **CI/CD** | GitHub Actions | Pipeline otomatis untuk Unit Testing & Build Docker Image pada branch `dev` dan `main`. |

---

## 📋 Prasyarat (Pre-requisites)

Sebelum memulai instalasi, pastikan perangkat Anda telah terpasang:

1. **Docker & Docker Desktop** *(Sangat Direkomendasikan)*
   * [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
   * Cukup gunakan Docker untuk menjalankan seluruh sistem (Database, Backend, dan Simulator) sekaligus tanpa perlu menginstal dependensi manual.
2. **Git**
   * [Download Git](https://git-scm.com/)
3. **DBeaver** *(Opsional, untuk melihat isi database visual)*
   * [Download DBeaver Community](https://dbeaver.io/)
4. **Python 3.12+** *(Hanya jika ingin menjalankan lokal tanpa Docker)*

---

## ⚙️ Instalasi dan Setup

### 1. Clone Repository
```bash
git clone https://github.com/username/monitoring-plts-backend.git
cd monitoring-plts-backend
```

### 2. Konfigurasi Environment Variables (`.env`)
Salin file template `.env.example` menjadi `.env` pada root project:

```bash
# Windows PowerShell
copy .env.example .env

# Linux / macOS
cp .env.example .env
```

Sesuaikan konfigurasi pada file [`.env`](.env):

```env
# ============================================================
# Environment Variables - PLTS Monitoring
# ============================================================

# Database Configuration (TimescaleDB Lokal via Docker Compose)
POSTGRES_DB=plts_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DATABASE_URL=postgresql+psycopg://postgres:postgres@db:5432/plts_db

# Port host laptop untuk DBeaver/koneksi luar (Default: 5433 agar tidak bentrok)
DB_HOST_PORT=5433

# Device Ingestion API Key (Digunakan oleh Simulator & Backend)
DEVICE_API_KEY=ESP8266_PLTS_SECRET_KEY

# Superadmin Credentials (Otomatis dibuat saat pertama kali server start)
SUPERADMIN_EMAIL=admin@plts.com
SUPERADMIN_PASSWORD=Admin@PLTS2026!

# JWT Authentication
JWT_SECRET_KEY=plts_jwt_secret_key_super_secure_2026_antigravity
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=480

# Simulator Configuration
INTERVAL_SECONDS=60
SCENARIO=NORMAL
```

---

## 💻 Penggunaan (Usage)

### Opsi 1: Menjalankan dengan Docker Compose *(Rekomendasi Utama)*

Cukup jalankan satu perintah berikut di root folder project:

```bash
docker compose up -d --build
```

Perintah ini akan secara otomatis:
1. Menyalakan container **TimescaleDB** di background.
2. Mem-build dan menyalakan **Backend FastAPI** di port `3000`.
3. Menginisialisasi tabel skema dan mengonversi tabel `telemetry` menjadi **Hypertable** TimescaleDB.
4. Melakukan *auto-seeding* akun Superadmin.
5. Menyalakan **Simulator IoT** yang langsung mengirim data telemetri berkala ke Backend.

#### Perintah Docker Compose Penting Lainnya:
```bash
# Melihat log aktivitas sistem secara live
docker compose logs -f

# Melihat log khusus simulator saja
docker compose logs -f simulator

# Menghentikan seluruh container
docker compose down

# Menghentikan container sekaligus menghapus database volume (reset bersih)
docker compose down -v
```

---

### Opsi 2: Menjalankan Manual di Host (Local Development)

Jika ingin mengembangkan tanpa Docker (pastikan PostgreSQL/TimescaleDB lokal sudah berjalan):

```bash
# 1. Buat dan aktifkan Virtual Environment
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

# 2. Install Dependencies
pip install -r backend/requirements.txt

# 3. Jalankan Backend
cd backend
uvicorn app.main:app --port 3000 --reload

# 4. Jalankan Simulator (Buka terminal baru)
python simulator/main.py
```

---

## 📡 Dokumentasi Endpoint API

Setelah backend aktif, dokumentasi interaktif OpenAPI dapat diakses langsung melalui browser di:
* **Swagger UI:** [http://localhost:3000/docs](http://localhost:3000/docs)
* **ReDoc:** [http://localhost:3000/redoc](http://localhost:3000/redoc)

### Ringkasan Endpoint Utama:

| Method | Endpoint | Auth | Deskripsi |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/login` | Publik | Login Superadmin menggunakan email & password, mengembalikan Bearer JWT Token. |
| `POST` | `/api/v1/auth/logout` | JWT Bearer | Logout sesi aktif. |
| `POST` | `/api/v1/telemetry/ingest` | `X-Device-API-Key` | Endpoint penerimaan data telemetri dari mikrokontroler ESP8266 / Simulator. |
| `GET` | `/api/v1/telemetry/latest` | JWT Bearer | Mengambil pembacaan 9 metrik sensor terakhir dan status sistem (*normal/warning/critical*). |
| `GET` | `/api/v1/telemetry/history` | JWT Bearer | Mengambil riwayat data historis/grafik tren dengan interval agregasi (`raw`, `5m`, `10m`, `1h`, `1d`). |
| `GET` | `/health/db` | Publik | Health-check konektivitas engine database. |

---

## 📊 Akses Database via DBeaver

Untuk memantau tabel dan data time-series secara langsung:
* **Host:** `127.0.0.1` (atau `localhost`)
* **Port:** `5433` *(sesuai nilai `DB_HOST_PORT`)*
* **Database:** `plts_db`
* **Username:** `postgres`
* **Password:** `postgres` *(sesuai file `.env`)*

> 💡 **Verifikasi TimescaleDB Hypertable di DBeaver:**  
> Jalankan query berikut di SQL Editor DBeaver untuk memastikan status hypertable:
> ```sql
> SELECT * FROM timescaledb_information.hypertables;
> ```

---

## 🧪 Menjalankan Unit Testing

Proyek ini dilengkapi dengan 14 skenario pengujian komprehensif mencakup autentikasi dan ingestion data.

**Menjalankan test secara cepat dan steril via Docker:**
```bash
docker run --rm -v "${PWD}/backend:/app" -w /app --env-file backend/.env python:3.12-slim sh -c "pip install --no-cache-dir -r requirements.txt pytest httpx && pytest tests/ -v"
```

**Atau jalankan langsung di terminal lokal (jika venv terpasang):**
```bash
cd backend
pytest tests/ -v
```

---

## 📁 Struktur Direktori Proyek

```text
monitoring-plts-backend/
├── .github/
│   └── workflows/
│       └── ci.yml               # Pipeline CI GitHub Actions (Test & Docker Build)
│
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── database.py      # SQLAlchemy engine, session maker, timezone config
│   │   │   ├── dependencies.py  # Dependency injection (JWT User Verification)
│   │   │   ├── jwt.py           # Pembuatan & verifikasi token JWT
│   │   │   ├── security.py      # Hashing & verifikasi password via bcrypt
│   │   │   └── seeder.py        # Idempotent seeder untuk akun Superadmin
│   │   ├── models/
│   │   │   ├── telemetry.py     # Model Telemetry TimescaleDB Hypertable
│   │   │   ├── users.py         # Model User & Auth
│   │   │   └── ...              # Model Thresholds, AlertLog, TelegramUser
│   │   ├── routers/
│   │   │   ├── auth.py          # Handler route /login & /logout
│   │   │   └── telemetry.py     # Handler route /ingest, /latest, /history
│   │   ├── schemas/
│   │   │   ├── auth.py          # Pydantic schema request/response auth
│   │   │   └── telemetry.py     # Pydantic schema metrik telemetri & agregasi
│   │   └── main.py              # Entrypoint FastAPI, router inclusion, lifespan hypertable
│   ├── tests/
│   │   ├── conftest.py          # Pytest fixtures, test database setup, mock client
│   │   ├── test_auth.py         # Unit tests login, logout, & security tokens
│   │   └── test_telemetry.py    # Unit tests ingest, auth guard, latest, & history
│   ├── Dockerfile               # Multi-stage production Dockerfile untuk backend
│   └── requirements.txt         # Daftar dependensi Python backend
│
├── simulator/
│   ├── main.py                  # Client HTTP ingestion loop (mengirim data ke API)
│   ├── generate.py              # Generator 9 metrik sensor berbasis skenario (WIB +07:00)
│   ├── scenario.py              # Definisi skenario (NORMAL, LOW_BATTERY, HIGH_LOAD, dll)
│   ├── csv_writer.py            # Local backup CSV writer (fallback jika API unreachable)
│   └── Dockerfile               # Multi-stage production Dockerfile untuk simulator
│
├── data/
│   └── plts_telemetry.csv       # File backup CSV lokal simulator (di-ignore dari git)
│
├── .dockerignore                # Mencegah file rahasia/cache masuk ke Docker image
├── .gitignore                   # Proteksi git dari credentials, venv, & cache
├── docker-compose.yml           # Orkestrasi container Database, Backend, & Simulator
├── .env.example                 # Template environment variables
└── README.md                    # Dokumentasi utama proyek
```

---

## 🌿 Alur Kerja Git & Branching Strategy

Proyek ini menerapkan aturan branch protection: branch `main` dan `dev` **hanya dapat digabungkan melalui Pull Request**.

| Branch | Tujuan | Aturan Akses |
| :--- | :--- | :--- |
| `feature/<nama-fitur>` | Tempat pengerjaan fitur baru atau perbaikan oleh developer. | Bebas push langsung oleh developer. |
| `dev` | Tempat integrasi seluruh fitur dan target testing. | Dilindungi; merge via Pull Request dari `feature/*`. |
| `main` | Source code versi stabil yang siap rilis/produksi. | Dilindungi; merge via Pull Request dari `dev`. |

### Format Standar Pesan Commit
Gunakan konvensi commit standar industri berikut:
* `feat:` Fitur baru (contoh: `feat: add date_bin aggregation for history endpoint`)
* `fix:` Perbaikan bug (contoh: `fix: handle timezone mismatch on ingest`)
* `test:` Menambah atau mengubah unit test (contoh: `test: add unit tests for jwt logout`)
* `ci:` Konfigurasi pipeline CI/CD (contoh: `ci: configure timescaledb service in test job`)
* `docs:` Pembaruan dokumentasi (contoh: `docs: update setup and usage instructions`)
* `refactor:` Restrukturisasi kode tanpa mengubah fungsionalitas (contoh: `refactor: extract to_wib timezone converter`)

---

## 👥 Pengembang

Dikembangkan oleh Tim PMLD — Sistem Monitoring PLTS Berbasis Web Dashboard dan Telegram Bot.
