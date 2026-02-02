from fastapi.testclient import TestClient
from tests.factories.category_factory import CategoryFactory
from tests.factories.product_factory import ProductFactory
from tests.factories.user_factory import UserFactory


def get_payload(
    test_client: TestClient,
    user_factory: UserFactory,
    product_factory: ProductFactory,
    category_factory: CategoryFactory,
):
    p = product_factory.create(price=100)
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
    return payload


def test_create_and_list_orders(
    test_client: TestClient,
    user_factory: UserFactory,
    product_factory: ProductFactory,
    category_factory: CategoryFactory,
    test_access_token,
):
    payload = get_payload(test_client, user_factory, product_factory, category_factory)
    create = test_client.post("/orders", json=payload, headers=test_access_token)
    assert create.status_code == 201
    created = create.json()

    assert created["status"] == "submitted"
    assert created["payment_method"] == "card"
    assert created["delivery_method"] == "courier"
    assert created["purchase_price"] == 200

    lst = test_client.get("/orders", headers=test_access_token)
    assert lst.status_code == 200


def test_invalid_payment_method_rejected(
    test_client: TestClient,
    user_factory: UserFactory,
    product_factory: ProductFactory,
    category_factory: CategoryFactory,
    test_access_token,
):
    # invalid enum - no "paypal" available
    payload = get_payload(test_client, user_factory, product_factory, category_factory)
    payload["payment_method"] = "paypal"

    resp = test_client.post("/orders", json=payload, headers=test_access_token)
    assert resp.status_code == 422
