from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from db import Base


class Category(Base):
    """
    Database model representing  product category.
    """

    __tablename__ = "category"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, Index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
