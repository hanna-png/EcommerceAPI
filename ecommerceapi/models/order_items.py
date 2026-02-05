from __future__ import annotations

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ecommerceapi.db.base import BaseModel


class OrderItem(BaseModel):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    total_price: Mapped[int] = mapped_column(Integer, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", lazy="joined")
