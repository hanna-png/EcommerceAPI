from fastapi.testclient import TestClient
from tests.factories.category_factory import CategoryFactory
from tests.factories.product_factory import ProductFactory


def test_products_search_returns_correct_products(
    test_client: TestClient,
    category_factory: CategoryFactory,
    product_factory: ProductFactory,
):
    product_factory.create(name="Book1")
    product_factory.create(name="Phone1")
    product_factory.create(description="This is a book")

    resp = test_client.get("/products/search?search_text=book")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 2
    for p in items:
        assert "id" in p
        assert "category_id" in p
        assert "name" in p
        assert "price" in p


def test_products_details_returns_correct_product(
    test_client: TestClient,
    category_factory: CategoryFactory,
    product_factory: ProductFactory,
):
    product_factory.create(id=1)
    product2 = product_factory.create(id=2)

    resp = test_client.get("/products/2/details")
    assert resp.status_code == 200
    item = resp.json()

    assert item["id"] == 2
    assert item["category_id"] == product2.category_id
    assert item["name"] == product2.name
    assert item["price"] == product2.price
    assert item["description"] == product2.description
    assert item["sku"] == product2.sku
