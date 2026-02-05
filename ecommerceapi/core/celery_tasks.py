from time import sleep

from ecommerceapi.core.celery import celery_app
from ecommerceapi.core.exceptions import ResourceNotFoundException
from ecommerceapi.db.database import SessionLocal
from ecommerceapi.models import Order


@celery_app.task(name="orders.verify_and_approve")
def verify_and_approve_order(order_id: int):
    """
    Background verification to approve an order.
    """
    db = SessionLocal()
    try:
        order = db.get(Order, order_id)
        if not order:
            raise ResourceNotFoundException("Order not found")

        sleep(10)
        order.status = "approved"
        db.add(order)
        db.commit()
    finally:
        db.close()
