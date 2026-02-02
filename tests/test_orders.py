from fastapi.testclient import TestClient
from tests.factories.category_factory import CategoryFactory
from tests.factories.product_factory import ProductFactory
from tests.factories.user_factory import UserFactory


def test_create_and_list_orders(
    test_client: TestClient,
    user_factory: UserFactory,
    product_factory: ProductFactory,
    category_factory: CategoryFactory,
):
    u = user_factory.create()

    p = product_factory.create(price=100)

    headers = auth_header(test_client, u.email, "password123")

    payload = {
        "payment_method": "card",
        "delivery_method": "courier",
        "billing": {
            "full_name": "Jidsguf shdgf",
            "city": "Warsaw",
            "postal_code": "00-001",
            "country": "PL",
        },
        "items": [{"product_id": p.id, "quantity": 2}],
    }

    create = test_client.post("/orders", json=payload, headers=headers)
    assert create.status_code == 201
    created = create.json()

    assert created["status"] == "submitted"
    assert created["payment_method"] == "card"
    assert created["delivery_method"] == "courier"
    assert created["purchase_price"] == 200

    lst = test_client.get("/orders", headers=headers)
    assert lst.status_code == 200


def test_invalid_payment_method_rejected(
    test_client: TestClient,
    user_factory: UserFactory,
    product_factory: ProductFactory,
    category_factory: CategoryFactory,
):
    u = user_factory.create()
    p = product_factory.create(price=100)
    headers = auth_header(test_client, u.email, "password123")
    # invalid enum - no "papypal" available
    payload = {
        "payment_method": "paypal",
        "delivery_method": "courier",
        "billing": {
            "full_name": "Jan Kowalski",
            "city": "Warsaw",
            "postal_code": "00-001",
            "country": "PL",
        },
        "items": [{"product_id": p.id, "quantity": 1}],
    }

    resp = test_client.post("/orders", json=payload, headers=headers)
    assert resp.status_code == 422


def auth_header(test_client: TestClient, email: str, password: str) -> dict[str, str]:
    resp = test_client.post(
        "/auth/login", data={"username": email, "password": password}
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
