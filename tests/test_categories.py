from fastapi.testclient import TestClient

from tests.factories.category_factory import CategoryFactory


def test_categories_returns_all(
    test_client: TestClient, category_factory: CategoryFactory
) -> None:
    """Checks if /categories returns all categories from the database."""
    CategoryFactory.create_batch(5)

    response = test_client.get("/categories")
    returned_categories = response.json()
    assert response.status_code == 200
    assert isinstance(returned_categories, list)
    assert len(returned_categories) == 5

    for category in returned_categories:
        assert "id" in category
        assert "name" in category
