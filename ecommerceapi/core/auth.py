from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ecommerceapi.core.security import decode_token
from ecommerceapi.core.exceptions import (
    UnauthorizedException,
    ResourceNotFoundException,
)
from ecommerceapi.db.database import get_db
from ecommerceapi.repositories.user import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    try:
        payload = decode_token(token)
    except ValueError:
        raise UnauthorizedException("Invalid access token")

    if payload.get("type") != "access":
        raise UnauthorizedException("Invalid access token")

    sub = payload.get("sub")
    if not sub:
        raise UnauthorizedException("Invalid access token")

    try:
        u = UserRepository.get_by_id(db, int(sub))
        if not u:
            raise UnauthorizedException("Invalid access token")
        return u
    except ResourceNotFoundException:
        pass
