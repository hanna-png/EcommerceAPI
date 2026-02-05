from celery import Celery
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
