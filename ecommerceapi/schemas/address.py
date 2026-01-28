from pydantic import BaseModel


class AddressCreate(BaseModel):
    city: str
    region: str | None = None
    postal_code: str
    country: str
