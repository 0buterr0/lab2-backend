from fastapi.testclient import TestClient
from .conftest import auth


def test_login_admin(client: TestClient) -> None:
    r = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert r.status_code == 200
    data = r.json()
    assert data["token_type"] == "bearer"
    assert data["user"]["role"] == "admin"


def test_login_wrong_password(client: TestClient) -> None:
    r = client.post("/api/auth/login", json={"username": "admin", "password": "wrong!"})
    assert r.status_code == 401


def test_me_requires_auth(client: TestClient) -> None:
    assert client.get("/api/auth/me").status_code == 401


def test_me_returns_user(client: TestClient, client_token: str) -> None:
    r = client.get("/api/auth/me", headers=auth(client_token))
    assert r.status_code == 200
    assert r.json()["username"] == "client"


def test_register_then_login(client: TestClient) -> None:
    r = client.post("/api/auth/register",
                    json={"username": "newbie", "password": "secret1", "full_name": "Newbie"})
    assert r.status_code == 201, r.text
    assert r.json()["user"]["username"] == "newbie"
    r2 = client.post("/api/auth/login", json={"username": "newbie", "password": "secret1"})
    assert r2.status_code == 200
