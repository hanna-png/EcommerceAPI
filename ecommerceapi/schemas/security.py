from pydantic import BaseModel, EmailStr, Field
from ecommerceapi.schemas.address import AddressCreate


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    first_name: str
    last_name: str
    address: AddressCreate


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
