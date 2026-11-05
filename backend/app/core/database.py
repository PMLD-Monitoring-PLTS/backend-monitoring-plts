import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Lokasi folder backend/
BACKEND_DIR = Path(__file__).resolve().parents[2]

# Membaca backend/.env
load_dotenv(BACKEND_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL belum dikonfigurasi")

engine = create_engine(
    DATABASE_URL,
    connect_args={"options": "-c timezone=Asia/Jakarta"},
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

Base = declarative_base()


def get_db():
    """Generator session database untuk Dependency Injection FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
