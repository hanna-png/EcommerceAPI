from pydantic import BaseModel, ConfigDict, EmailStr
from ecommerceapi.schemas.address import AddressOut


class UserOut(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    address: AddressOut

    model_config = ConfigDict(from_attributes=True)
