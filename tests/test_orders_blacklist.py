from fastapi.testclient import TestClient
from .conftest import auth


def _create_product(client: TestClient, admin_token: str, *, stock: int = 5, price: str = "10.00") -> int:
    r = client.post("/api/products", headers=auth(admin_token),
                    json={"name": "Widget", "price": price, "stock": stock})
    assert r.status_code == 201
    return r.json()["id"]


def test_client_creates_and_pays_order(client: TestClient, admin_token: str, client_token: str) -> None:
    pid = _create_product(client, admin_token, stock=10, price="5.00")
    r = client.post("/api/orders", headers=auth(client_token),
                    json={"items": [{"product_id": pid, "quantity": 3}]})
    assert r.status_code == 201, r.text
    order = r.json()
    assert order["status"] == "pending"
    assert order["total"] == "15.00"

    r2 = client.post(f"/api/orders/{order['id']}/pay", headers=auth(client_token))
    assert r2.status_code == 200
    assert r2.json()["status"] == "paid"


def test_order_rejected_when_stock_insufficient(client: TestClient, admin_token: str, client_token: str) -> None:
    pid = _create_product(client, admin_token, stock=1)
    r = client.post("/api/orders", headers=auth(client_token),
                    json={"items": [{"product_id": pid, "quantity": 99}]})
    assert r.status_code == 409


def test_blacklist_workflow(client: TestClient, admin_token: str) -> None:
    # Create a fresh user to blacklist.
    r = client.post("/api/auth/register",
                    json={"username": "deadbeat", "password": "secret1"})
    assert r.status_code == 201
    deadbeat_token = r.json()["access_token"]
    user_id = r.json()["user"]["id"]

    # Admin blacklists.
    r = client.post("/api/admin/blacklist", headers=auth(admin_token),
                    json={"user_id": user_id, "reason": "non-payment"})
    assert r.status_code == 201

    listing = client.get("/api/admin/blacklist", headers=auth(admin_token)).json()
    assert any(e["user_id"] == user_id for e in listing)

    # Blacklisted client cannot place orders.
    pid = _create_product(client, admin_token, stock=5)
    r = client.post("/api/orders", headers=auth(deadbeat_token),
                    json={"items": [{"product_id": pid, "quantity": 1}]})
    assert r.status_code == 403

    # Admin removes from blacklist.
    r = client.delete(f"/api/admin/blacklist/{user_id}", headers=auth(admin_token))
    assert r.status_code == 204

    # Now the user can order.
    r = client.post("/api/orders", headers=auth(deadbeat_token),
                    json={"items": [{"product_id": pid, "quantity": 1}]})
    assert r.status_code == 201


def test_client_cannot_view_others_order(client: TestClient, admin_token: str, client_token: str) -> None:
    pid = _create_product(client, admin_token, stock=2)
    # Order from default client
    r = client.post("/api/orders", headers=auth(client_token),
                    json={"items": [{"product_id": pid, "quantity": 1}]})
    order_id = r.json()["id"]

    # Different client
    r = client.post("/api/auth/register", json={"username": "spy", "password": "secret1"})
    spy_token = r.json()["access_token"]

    r = client.get(f"/api/orders/{order_id}", headers=auth(spy_token))
    assert r.status_code == 403


def test_payment_strategy_polymorphism() -> None:
    from app.services.payment import MockPaymentProcessor, AlwaysFailingProcessor, PaymentProcessor
    from decimal import Decimal

    ok: PaymentProcessor = MockPaymentProcessor()
    fail: PaymentProcessor = AlwaysFailingProcessor()
    assert ok.charge(order_id=1, amount=Decimal("10")) is True
    assert fail.charge(order_id=1, amount=Decimal("10")) is False
