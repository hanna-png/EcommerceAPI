from __future__ import annotations

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
from ecommerceapi.schemas.security import RegisterIn, TokenPair
from ecommerceapi.schemas.general import MessageOut
from ecommerceapi.core.exceptions import (
    ValidationException,
    UnauthorizedException,
    BaseAppException,
)


class SecurityService:
    @staticmethod
    def _validate_refresh_token(refresh_token: str):
        try:
            payload = decode_token(refresh_token)
        except ValueError:
            raise UnauthorizedException("Invalid refresh token")

        if payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid refresh token")

        jti = payload.get("jti")
        sub = payload.get("sub")
        if not jti or not sub:
            raise UnauthorizedException("Invalid refresh token ")

        return payload

    @staticmethod
    def register(db: Session, payload: RegisterIn):
        if UserRepository.get_by_email(db, payload.email):
            raise ValidationException("Email already registered")

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
            raise BaseAppException("Unexpected error occurred")

    @staticmethod
    def login(db: Session, *, email: str, password: str) -> TokenPair:
        user = UserRepository.get_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Invalid credentials")

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
        payload = SecurityService._validate_refresh_token(refresh_token)

        RefreshTokenRepository.revoke(db, jti=payload["jti"])
        return MessageOut(message="ok")

    @staticmethod
    def refresh_tokens(db: Session, refresh_token: str) -> TokenPair:
        payload = SecurityService._validate_refresh_token(refresh_token)

        user_id = int(payload["sub"])

        rt = RefreshTokenRepository.get_valid_by_jti(db, payload["jti"])
        if not rt:
            RefreshTokenRepository.revoke_all_for_user(db, user_id=user_id)
            # commit in service because we want to revoke AND raise an exception
            db.commit()
            raise UnauthorizedException("Refresh token revoked or expired")

        if rt.token_hash != hash_token(refresh_token):
            RefreshTokenRepository.revoke_all_for_user(db, user_id=user_id)
            db.commit()
            raise UnauthorizedException("Refresh token is not correct.")

        RefreshTokenRepository.revoke(db, jti=payload["jti"])

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
