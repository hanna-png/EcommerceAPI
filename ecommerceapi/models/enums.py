from enum import Enum


class PaymentMethod(str, Enum):
    card = "card"
    blik = "blik"
    bank_transfer = "bank_transfer"
    cash_on_delivery = "cash_on_delivery"


class DeliveryMethod(str, Enum):
    courier = "courier"
    parcel_locker = "parcel_locker"
    pickup_point = "pickup_point"


class OrderStatus(str, Enum):
    submitted = "submitted"
    paid = "paid"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"
