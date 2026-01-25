from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class ProductListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category_id: int
    name: str
    price: Decimal | None = None
    sku: str | None = None


class ProductDetailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category_id: int
    name: str
    description: str | None = None
    price: Decimal | None = None
    sku: str | None = None
