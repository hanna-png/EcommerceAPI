from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ecommerceapi.core.exceptions import ResourceNotFoundException
from ecommerceapi.models.order import Order
from ecommerceapi.core.celery import verify_and_approve_order


class OrderRepository:
    @staticmethod
    def create(db: Session, order: Order) -> Order:
        db.add(order)
        db.flush()
        db.refresh(order)
        db.commit()
        verify_and_approve_order.delay(order.id)
        return order

    @staticmethod
    def get_by_id_for_user(db: Session, *, order_id: int, user_id: int) -> Order:
        stmt = (
            select(Order)
            .where(Order.id == order_id, Order.user_id == user_id)
            .options(
                selectinload(Order.items),
                selectinload(Order.billing),
            )
        )
        o = db.execute(stmt).scalars().first()
        if not o:
            raise ResourceNotFoundException("Order not found")
        return o

    @staticmethod
    def get_all_for_user(db: Session, *, user_id: int) -> list[Order]:
        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .options(
                selectinload(Order.items),
                selectinload(Order.billing),
            )
        )
        return db.execute(stmt).scalars().all()
