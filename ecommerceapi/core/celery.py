from time import sleep
from celery import Celery
from ecommerceapi.db.database import SessionLocal
from ecommerceapi.models.order import Order
from ecommerceapi.core.exceptions import ResourceNotFoundException
from ecommerceapi.core.config import settings

celery_app = Celery(
    "ecommerceapi",
    broker=settings.celery_broker_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

celery_app.autodiscover_tasks(["ecommerceapi.core"])


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
