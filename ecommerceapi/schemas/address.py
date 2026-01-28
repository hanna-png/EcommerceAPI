from pydantic import BaseModel, ConfigDict


class AddressCreate(BaseModel):
    city: str
    region: str | None = None
    postal_code: str
    country: str


class AddressOut(BaseModel):
    id: int
    city: str
    region: str | None = None
    postal_code: str
    country: str

    model_config = ConfigDict(from_attributes=True)
