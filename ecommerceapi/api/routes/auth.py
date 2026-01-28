from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ecommerceapi.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)
from ecommerceapi.db.database import get_db
from ecommerceapi.repositories.address import AddressRepository
from ecommerceapi.repositories.refresh_token import RefreshTokenRepository
from ecommerceapi.repositories.user import UserRepository
from ecommerceapi.schemas.security import RegisterIn, TokenPair

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    if UserRepository.get_by_email(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered. log in",
        )

    user = UserRepository.create(
        db,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
    )
    AddressRepository.create(
        db,
        user_id=user.id,
        city=payload.address.city,
        region=payload.address.region,
        postal_code=payload.address.postal_code,
        country=payload.address.country,
    )

    return {"id": user.id, "email": user.email}


@auth_router.post("/refresh", response_model=TokenPair)
def refresh_tokens(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = decode_token(refresh_token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong token type"
        )

    sub = payload.get("sub")
    jti = payload.get("jti")
    if not sub or not jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid payload"
        )

    user_id = int(sub)
    rt = RefreshTokenRepository.get_valid_by_jti(db, jti)
    if not rt:
        RefreshTokenRepository.revoke_all_for_user(db, user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token revoked or expired",
        )

    if rt.token_hash != hash_token(refresh_token):
        RefreshTokenRepository.revoke_all_for_user(db, user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is not correct.",
        )

    RefreshTokenRepository.revoke(db, jti=jti)

    new_access = create_access_token(user_id=str(user_id))
    new_refresh, new_exp, jti = create_refresh_token(user_id=str(user_id))
    RefreshTokenRepository.create(
        db,
        user_id=user_id,
        jti=jti,
        token_hash=hash_token(new_refresh),
        expires_at=new_exp,
    )

    return TokenPair(access_token=new_access, refresh_token=new_refresh)


@auth_router.post("/logout")
def logout(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = decode_token(refresh_token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    RefreshTokenRepository.revoke(db, jti=payload["jti"])
    return {"status": "ok"}


@auth_router.post("/login", response_model=TokenPair)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    if len(form.password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=400, detail="Password too long. max is 72 bytes"
        )

    user = UserRepository.get_by_email(db, form.username)
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    access = create_access_token(user_id=str(user.id))
    refresh, refresh_exp, jti = create_refresh_token(user_id=str(user.id))
    RefreshTokenRepository.create(
        db,
        user_id=user.id,
        jti=jti,
        token_hash=hash_token(refresh),
        expires_at=refresh_exp,
    )

    return TokenPair(access_token=access, refresh_token=refresh)
