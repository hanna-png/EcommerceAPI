from __future__ import annotations
from uuid import uuid4
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any
from jose import JWTError, jwt
from passlib.context import CryptContext

from ecommerceapi.core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_access_token(*, user_id: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload: dict[str, Any] = {
        "sub": user_id,
        "type": "access",
        "exp": exp,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")


def create_refresh_token(*, user_id: str) -> tuple[str, datetime, str]:
    exp = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    jti = uuid4().hex
    payload: dict[str, Any] = {
        "sub": user_id,
        "type": "refresh",
        "jti": jti,
        "exp": exp,
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")
    return token, exp, jti


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
    except JWTError as e:
        raise ValueError("Invalid token") from e
