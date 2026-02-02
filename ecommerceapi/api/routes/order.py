from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ecommerceapi.core.auth import get_current_user
from ecommerceapi.db.database import get_db
from ecommerceapi.schemas.order import OrderCreateIn, OrderOut
from ecommerceapi.services.order_service import OrderService

order_router = APIRouter(prefix="/orders", tags=["orders"])


@order_router.post("", response_model=OrderOut, status_code=201)
def create_order(
    payload: OrderCreateIn,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> OrderOut:
    return OrderService.create_order(db, user_id=current_user.id, payload=payload)


@order_router.get("", response_model=list[OrderOut])
def list_my_orders(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list[OrderOut]:
    return OrderService.list_orders(db, user_id=current_user.id)


@order_router.get("/{order_id}", response_model=OrderOut)
def get_my_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> OrderOut:
    return OrderService.get_order(db, order_id=order_id, user_id=current_user.id)
