from pydantic import BaseModel, ConfigDict, Field

from ecommerceapi.models.enums import PaymentMethod, DeliveryMethod, OrderStatus


class BillingIn(BaseModel):
    full_name: str
    city: str
    postal_code: str
    country: str


class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = Field(ge=1, le=999)


class OrderCreateIn(BaseModel):
    payment_method: PaymentMethod
    delivery_method: DeliveryMethod
    billing: BillingIn
    items: list[OrderItemIn] = Field(min_length=1)


class BillingOut(BaseModel):
    full_name: str
    city: str
    postal_code: str
    country: str

    model_config = ConfigDict(from_attributes=True)


class OrderItemOut(BaseModel):
    product_id: int
    quantity: int
    total_price: int

    model_config = ConfigDict(from_attributes=True)


class OrderOut(BaseModel):
    id: int
    status: OrderStatus
    payment_method: PaymentMethod
    delivery_method: DeliveryMethod
    purchase_price: int
    billing: BillingOut
    items: list[OrderItemOut]

    model_config = ConfigDict(from_attributes=True)
