from pydantic import BaseModel, ConfigDict
from ecommerceapi.schemas.category import CategoryOut


class ProductListOut(BaseModel):
    """
    API schema representing a product category returned in response without the description and sku.
    """

    model_config = ConfigDict(from_attributes=True)
    id: int
    category_id: int
    name: str
    price: float | None = None


class ProductDetailOut(BaseModel):
    """
    API schema representing a product category returned in response with description and sku.
    """

    model_config = ConfigDict(from_attributes=True)
    id: int
    category_id: int
    name: str
    price: float | None = None
    # additional info
    description: str | None = None
    sku: str | None = None
    category: CategoryOut
