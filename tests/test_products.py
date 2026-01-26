from fastapi.testclient import TestClient
from tests.factories.category_factory import CategoryFactory
from tests.factories.product_factory import ProductFactory


def test_products_search_returns_correct_products(
    test_client: TestClient,
    category_factory: CategoryFactory,
    product_factory: ProductFactory,
):
    product_factory(name="Book1")
    product_factory(name="Phone1")
    product_factory(description="This is a book")

    resp = test_client.get("/products/search?search_text=book")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 2
    for p in items:
        assert "id" in p
        assert "category_id" in p
        assert "name" in p
        assert "price" in p
