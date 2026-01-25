from sqlalchemy import select
from sqlalchemy.orm import Session

from ecommerceapi.models.category import Category


class CategoryRepository:
    """
    Retrieve all product categories from database.
    """

    @staticmethod
    def get_all(db: Session) -> list[Category]:
        stmt = select(Category).order_by(Category.name)
        return db.execute(stmt).scalars().all()
