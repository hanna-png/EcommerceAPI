from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from ecommerceapi.models.product import Product


class ProductRepository:
    @staticmethod
    def get_by_category(db: Session, category_id: int) -> list[Product]:
        """
        Retrieve all products by category.
        """
        stmt = (
            select(Product)
            .where(Product.category_id == category_id)
            .order_by(Product.name)
        )
        return db.execute(stmt).scalars().all()

    @staticmethod
    def search(db: Session, query: str) -> list[Product]:
        """Retrieve all products that match the query."""
        pattern = f"%{query}%"
        stmt = (
            select(Product)
            .where(
                or_(
                    Product.name.ilike(pattern),
                    Product.description.ilike(pattern),
                )
            )
            .order_by(Product.name)
        )
        return db.execute(stmt).scalars().all()

    @staticmethod
    def get_by_id(db: Session, product_id: int) -> Product | None:
        """Retrieve product by id."""
        stmt = (
            select(Product)
            .options(joinedload(Product.category))
            .where(Product.id == product_id)
        )
        return db.execute(stmt).scalars().first()
