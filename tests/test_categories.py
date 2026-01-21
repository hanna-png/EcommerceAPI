from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from tests.factories.category_factory import CategoryFactory


def test_categories_returns_all(
    test_client: TestClient, db_test_session: Session
) -> None:
    """Checks if /categories returns all categories from the database."""
    categories = CategoryFactory.create_batch(5)
    db_test_session.add_all(categories)
    db_test_session.flush()

    response = test_client.get("/categories")
    returned_categories = response.json()
    assert response.status_code == 200
    assert isinstance(returned_categories, list)
    assert len(returned_categories) == 5

    for category in returned_categories:
        assert "id" in category
        assert "name" in category
