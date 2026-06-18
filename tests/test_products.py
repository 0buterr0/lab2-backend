from fastapi.testclient import TestClient
from .conftest import auth


def test_anonymous_cannot_list_products(client: TestClient) -> None:
    assert client.get("/api/products").status_code == 401


def test_client_can_list_products(client: TestClient, client_token: str) -> None:
    r = client.get("/api/products", headers=auth(client_token))
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_client_cannot_create_product(client: TestClient, client_token: str) -> None:
    r = client.post("/api/products",
                    headers=auth(client_token),
                    json={"name": "X", "price": "1.00", "stock": 1})
    assert r.status_code == 403


def test_admin_full_crud(client: TestClient, admin_token: str) -> None:
    payload = {"name": "Test gadget", "description": "d", "price": "12.50", "stock": 5}
    r = client.post("/api/products", headers=auth(admin_token), json=payload)
    assert r.status_code == 201, r.text
    pid = r.json()["id"]

    r = client.put(f"/api/products/{pid}", headers=auth(admin_token),
                   json={"price": "15.00", "stock": 7})
    assert r.status_code == 200
    assert r.json()["stock"] == 7

    r = client.get(f"/api/products/{pid}", headers=auth(admin_token))
    assert r.status_code == 200
    assert r.json()["price"] == "15.00"

    r = client.delete(f"/api/products/{pid}", headers=auth(admin_token))
    assert r.status_code == 204
    assert client.get(f"/api/products/{pid}", headers=auth(admin_token)).status_code == 404
