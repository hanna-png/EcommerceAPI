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
    product = ProductFactory()

    resp = test_client.get(f"/products/{product.id}/details")
    assert resp.status_code == 200
    item = resp.json()

    assert item["id"] == product.id
    assert item["name"] == product.name
    assert item["price"] == product.price
    assert item["description"] == product.description
    assert item["sku"] == product.sku

    category = item["category"]
    assert set(category.keys()) == {"id", "name"}
    assert category["id"] == product.category.id
    assert category["name"] == product.category.name
