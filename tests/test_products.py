from fastapi.testclient import TestClient
from tests.factories.category_factory import CategoryFactory
from tests.factories.product_factory import ProductFactory


def test_category_products_returns_only_that_category(
    test_client: TestClient,
    category_factory: CategoryFactory,
    product_factory: ProductFactory,
):
    cat = CategoryFactory()
    ProductFactory.create_batch(3, category=cat)

    resp = test_client.get(f"/categories/{cat.id}/products")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 3
    for p in items:
        assert "id" in p
        assert "category_id" in p
        assert p["category_id"] == cat.id
        assert "name" in p
        assert "price" in p
        assert "sku" in p
