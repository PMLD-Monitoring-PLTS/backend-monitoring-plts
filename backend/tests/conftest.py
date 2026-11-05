import os
import sys
from pathlib import Path

# Pastikan folder backend masuk ke sys.path saat pytest dijalankan
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import pytest
from fastapi.testclient import TestClient

import app.models  # Register semua model ke Base
from app.main import app as fastapi_app
from app.core.database import Base, engine, SessionLocal
from app.core.seeder import seed_superadmin


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Inisialisasi tabel dan superadmin sebelum seluruh test berjalan."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_superadmin(db)
    finally:
        db.close()
    yield


@pytest.fixture
def client():
    """Test client FastAPI berbasis httpx."""
    return TestClient(fastapi_app)


@pytest.fixture
def superadmin_credentials():
    return {
        "email": os.getenv("SUPERADMIN_EMAIL", "admin@plts.com"),
        "password": os.getenv("SUPERADMIN_PASSWORD", "Admin@PLTS2026!"),
    }


@pytest.fixture
def auth_headers(client, superadmin_credentials):
    """Menghasilkan HTTP Bearer Authorization header yang valid."""
    resp = client.post("/api/v1/auth/login", json=superadmin_credentials)
    assert resp.status_code == 200, f"Gagal login superadmin: {resp.text}"
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def device_headers():
    """Header otentikasi X-Device-API-Key untuk simulator/IoT."""
    key = os.getenv("DEVICE_API_KEY", "ESP8266_PLTS_SECRET_KEY")
    return {"X-Device-API-Key": key}
