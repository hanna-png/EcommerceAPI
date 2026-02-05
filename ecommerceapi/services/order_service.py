from sqlalchemy.orm import Session

from ecommerceapi.core.exceptions import ValidationException
from ecommerceapi.models.order import Order
from ecommerceapi.models.order_billings import OrderBilling
from ecommerceapi.models.order_items import OrderItem
from ecommerceapi.models.enums import OrderStatus
from ecommerceapi.repositories.order import OrderRepository
from ecommerceapi.repositories.product import ProductRepository
from ecommerceapi.schemas.order import OrderCreateIn


class OrderService:
    @staticmethod
    def create_order(db: Session, *, user_id: int, payload: OrderCreateIn) -> Order:
        if not payload.items:
            raise ValidationException("Order must contain at least one item")
        items: list[OrderItem] = []
        total_price_for_order = 0

        for it in payload.items:
            product = ProductRepository.get_by_id(db, it.product_id)

            price = int(product.price)
            total_price_for_product = price * int(it.quantity)

            items.append(
                OrderItem(
                    product_id=it.product_id,
                    quantity=int(it.quantity),
                    total_price=total_price_for_product,
                )
            )
            total_price_for_order += total_price_for_product

        order = Order(
            user_id=user_id,
            status=OrderStatus.submitted.value,
            payment_method=payload.payment_method.value,
            delivery_method=payload.delivery_method.value,
            purchase_price=total_price_for_order,
        )

        order.billing = OrderBilling(
            full_name=payload.billing.full_name,
            city=payload.billing.city,
            postal_code=payload.billing.postal_code,
            country=payload.billing.country,
        )

        order.items = items

        return OrderRepository.create(db, order)

    @staticmethod
    def get_order(db: Session, *, order_id: int, user_id: int) -> Order:
        return OrderRepository.get_by_id_for_user(
            db, order_id=order_id, user_id=user_id
        )

    @staticmethod
    def list_orders(db: Session, *, user_id: int) -> list[Order]:
        return OrderRepository.get_all_for_user(db, user_id=user_id)
