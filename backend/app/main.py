import sys
from pathlib import Path

# Memastikan folder 'backend/' masuk ke sys.path agar 'import app...' selalu terbaca
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import engine
from app.routers.telemetry import router as telemetry_router

app = FastAPI(
    title="PLTS Monitoring API",
    description="API Monitoring PLTS untuk Web Dashboard dan Telegram Bot",
    version="1.1.0",
)

# Registrasi Router
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
