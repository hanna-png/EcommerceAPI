from pydantic import BaseModel


class ErrorOut(BaseModel):
    detail: str


class MessageOut(BaseModel):
    message: str
