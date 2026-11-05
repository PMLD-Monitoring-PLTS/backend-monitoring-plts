from datetime import datetime, timezone, timedelta

WIB = timezone(timedelta(hours=7))

SAMPLE_TELEMETRY = {
    "device_id": "ESP8266_PLTS_01",
    "timestamp": datetime.now(WIB).strftime("%Y-%m-%dT%H:%M:%S+07:00"),
    "metrics": {
        "panel": {"voltage": 18.5, "current": 2500.0, "power": 46.25},
        "beban": {"voltage": 12.0, "current": 1200.0, "power": 14.4},
        "baterai": {"voltage": 12.6, "current": -800.0, "power": -10.08},
    },
}


def test_health_database(client):
    """Test health check database."""
    resp = client.get("/health/db")
    assert resp.status_code == 200
    assert resp.json() == {"database": "connected"}


def test_ingest_telemetry_success(client, device_headers):
    """Test ingest telemetry berhasil dengan API Key yang valid."""
    resp = client.post(
        "/api/v1/telemetry/ingest",
        headers=device_headers,
        json=SAMPLE_TELEMETRY,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "successfully recorded" in data["message"]


def test_ingest_telemetry_wrong_api_key(client):
    """Test ingest telemetry ditolak saat API Key salah."""
    resp = client.post(
        "/api/v1/telemetry/ingest",
        headers={"X-Device-API-Key": "WRONG_KEY"},
        json=SAMPLE_TELEMETRY,
    )
    assert resp.status_code == 401


def test_ingest_telemetry_missing_api_key(client):
    """Test ingest telemetry gagal validasi header jika X-Device-API-Key tidak dikirim."""
    resp = client.post("/api/v1/telemetry/ingest", json=SAMPLE_TELEMETRY)
    assert resp.status_code == 422


def test_get_latest_unauthorized(client):
    """Test endpoint /latest ditolak jika tidak ada JWT token."""
    resp = client.get("/api/v1/telemetry/latest")
    assert resp.status_code in (401, 403)


def test_get_latest_authorized(client, auth_headers, device_headers):
    """Test endpoint /latest berhasil diakses dengan JWT token."""
    # Pastikan ada minimal 1 data di database
    client.post(
        "/api/v1/telemetry/ingest",
        headers=device_headers,
        json=SAMPLE_TELEMETRY,
    )

    resp = client.get("/api/v1/telemetry/latest", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "panel" in data["data"]
    assert "beban" in data["data"]
    assert "baterai" in data["data"]
    assert "system_status" in data["data"]
    assert "last_updated" in data["data"]


def test_get_history_unauthorized(client):
    """Test endpoint /history ditolak tanpa JWT token."""
    resp = client.get("/api/v1/telemetry/history")
    assert resp.status_code in (401, 403)


def test_get_history_authorized(client, auth_headers):
    """Test endpoint /history berhasil dengan token valid."""
    resp = client.get(
        "/api/v1/telemetry/history?interval=raw&limit=10",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "points" in data["data"]
    assert "from" in data["data"]
    assert "to" in data["data"]
