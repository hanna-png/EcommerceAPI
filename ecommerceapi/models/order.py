from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ecommerceapi.db.base import BaseModel


class Order(BaseModel):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(String(30), nullable=False, default="submitted")

    payment_method: Mapped[str] = mapped_column(String(50), nullable=False)
    delivery_method: Mapped[str] = mapped_column(String(50), nullable=False)

    purchase_price: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    billing = relationship(
        "OrderBilling",
        back_populates="order",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    user = relationship("User", lazy="joined")
