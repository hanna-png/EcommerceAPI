from sqlalchemy import select
from sqlalchemy.orm import Session

from ecommerceapi.models.category import Category


def get_categories(db: Session) -> list[Category]:
    """
    Retrieve all product categories from database.
    """
    stmt = select(Category).order_by(Category.name)
    return db.execute(stmt).scalars().all()
