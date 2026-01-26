from pydantic import BaseModel, ConfigDict


class ProductListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category_id: int
    name: str
    price: float | None = None


class ProductDetailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category_id: int
    name: str
    price: float | None = None
    # additional info
    description: str | None = None
    sku: str | None = None
