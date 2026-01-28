from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ecommerceapi.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)
from ecommerceapi.repositories.address import AddressRepository
from ecommerceapi.repositories.refresh_token import RefreshTokenRepository
from ecommerceapi.repositories.user import UserRepository
from ecommerceapi.schemas.security import RegisterIn, TokenPair, MessageOut


class SecurityService:
    @staticmethod
    def register(db: Session, payload: RegisterIn):
        if UserRepository.get_by_email(db, payload.email):
            raise HTTPException(status_code=400, detail="Email already registered")

        try:
            user = UserRepository.create(
                db,
                email=payload.email,
                hashed_password=hash_password(payload.password),
                first_name=payload.first_name,
                last_name=payload.last_name,
            )

            address = AddressRepository.create(
                db,
                user_id=user.id,
                city=payload.address.city,
                region=payload.address.region,
                postal_code=payload.address.postal_code,
                country=payload.address.country,
            )

            user.address = address
            return user

        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Email already registered",
            )

    @staticmethod
    def login(db: Session, *, email: str, password: str) -> TokenPair:
        user = UserRepository.get_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
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

    @staticmethod
    def logout(db: Session, refresh_token: str) -> MessageOut:
        try:
            payload = decode_token(refresh_token)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        jti = payload.get("jti")
        if not jti:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid payload",
            )

        RefreshTokenRepository.revoke(db, jti=jti)
        return MessageOut(message="ok")

    @staticmethod
    def refresh_tokens(db: Session, refresh_token: str) -> TokenPair:
        try:
            payload = decode_token(refresh_token)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Wrong token type",
            )

        sub = payload.get("sub")
        jti = payload.get("jti")
        if not sub or not jti:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid payload",
            )

        user_id = int(sub)

        rt = RefreshTokenRepository.get_valid_by_jti(db, jti)
        if not rt:
            RefreshTokenRepository.revoke_all_for_user(db, user_id=user_id)
            # commit in service because we want to revoke AND raise an exception
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token revoked or expired",
            )

        if rt.token_hash != hash_token(refresh_token):
            RefreshTokenRepository.revoke_all_for_user(db, user_id=user_id)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is not correct.",
            )

        RefreshTokenRepository.revoke(db, jti=jti)

        new_access = create_access_token(user_id=str(user_id))
        new_refresh, new_exp, new_jti = create_refresh_token(user_id=str(user_id))

        RefreshTokenRepository.create(
            db,
            user_id=user_id,
            jti=new_jti,
            token_hash=hash_token(new_refresh),
            expires_at=new_exp,
        )

        return TokenPair(access_token=new_access, refresh_token=new_refresh)
