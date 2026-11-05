def test_login_success(client, superadmin_credentials):
    """Test login berhasil dengan kredensial superadmin yang valid."""
    resp = client.post("/api/v1/auth/login", json=superadmin_credentials)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client, superadmin_credentials):
    """Test login gagal dengan password salah."""
    payload = {
        "email": superadmin_credentials["email"],
        "password": "WrongPassword123!",
    }
    resp = client.post("/api/v1/auth/login", json=payload)
    assert resp.status_code == 401
    assert "detail" in resp.json()


def test_login_invalid_email(client):
    """Test login gagal dengan email yang tidak terdaftar."""
    payload = {
        "email": "notfound@example.com",
        "password": "AnyPassword123!",
    }
    resp = client.post("/api/v1/auth/login", json=payload)
    assert resp.status_code == 401


def test_logout_success(client, auth_headers):
    """Test logout berhasil dengan JWT token yang valid."""
    resp = client.post("/api/v1/auth/logout", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["message"] == "Logout berhasil."


def test_logout_without_token(client):
    """Test logout gagal saat request tanpa header Authorization."""
    resp = client.post("/api/v1/auth/logout")
    # FastAPI HTTPBearer returns 403 when authorization header is missing
    assert resp.status_code in (401, 403)


def test_logout_invalid_token(client):
    """Test logout gagal dengan token ngawur."""
    resp = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": "Bearer invalid.jwt.token"},
    )
    assert resp.status_code == 401
