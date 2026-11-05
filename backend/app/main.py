import sys
from contextlib import asynccontextmanager
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

import app.models  # Import semua model agar terdaftar di Base
from app.core.database import Base, SessionLocal, engine
from app.core.seeder import seed_superadmin
from app.routers.auth import router as auth_router
from app.routers.telemetry import router as telemetry_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    1. Membuat tabel di database jika belum ada (penting untuk container baru).
    2. Auto-seed superadmin saat server pertama kali start.
    """
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_superadmin(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="PLTS Monitoring API",
    description="API Monitoring PLTS untuk Web Dashboard dan Telegram Bot",
    version="1.1.0",
    lifespan=lifespan,
)

# Registrasi Router
app.include_router(auth_router)
app.include_router(telemetry_router)


@app.get("/health/db", tags=["System"])
def check_database():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"database": "connected"}
    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed",
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=3000, reload=True)
