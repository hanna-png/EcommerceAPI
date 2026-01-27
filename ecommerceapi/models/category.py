from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ecommerceapi.db.base import BaseModel


class Category(BaseModel):
    """
    Database model representing  product category.
    """

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    products = relationship(
        "Product", back_populates="category", cascade="all,delete-orphan"
    )
