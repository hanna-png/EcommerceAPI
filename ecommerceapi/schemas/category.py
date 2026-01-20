from pydantic import BaseModel

class CategoryOut(BaseModel):
    """
    API schema representing a product category returned in response.
    """
    id: int
    name: str
    model_config = {"from_attributes": True}
