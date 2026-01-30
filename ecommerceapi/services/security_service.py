from sqlalchemy.orm import Session

from datetime import datetime, timezone
from ecommerceapi.models.refresh_token import RefreshToken
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
    ResourceNotFoundException,
)
from ecommerceapi.core.logging import logger


class SecurityService:
    @staticmethod
    def get_valid_by_jti(db: Session, jti: str) -> RefreshToken | None:
        try:
            rt = RefreshTokenRepository.get_by_jti(db, jti)
        except ResourceNotFoundException:
            return None

        if rt.revoked_at is not None:
            return None
        if rt.expires_at <= datetime.now(timezone.utc):
            return None
        return rt

    @staticmethod
    def _validate_refresh_token(db, refresh_token: str):
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

        rt = SecurityService.get_valid_by_jti(db, jti)
        user_id = int(sub)
        if not rt:
            RefreshTokenRepository.revoke_all_for_user(db, user_id=user_id)
            db.commit()
            raise UnauthorizedException("Refresh token revoked or expired")

        if rt.token_hash != hash_token(refresh_token):
            RefreshTokenRepository.revoke_all_for_user(db, user_id=user_id)
            db.commit()
            raise UnauthorizedException("Refresh token is not correct.")

        return payload

    @staticmethod
    def register(db: Session, payload: RegisterIn):
        try:
            u = UserRepository.get_by_email(db, payload.email)
            if u:
                raise ValidationException("Email already registered")
        except ResourceNotFoundException:
            pass

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
            logger.info(f"User {user.id} registered successfully")
            return user

        except Exception:
            db.rollback()
            raise BaseAppException("Unexpected error occurred")

    @staticmethod
    def login(db: Session, *, email: str, password: str) -> TokenPair:
        try:
            user = UserRepository.get_by_email(db, email)
        except ResourceNotFoundException:
            raise UnauthorizedException("User not found")

        if not verify_password(password, user.hashed_password):
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
        logger.info(f"User {email} logged in successfully")

        return TokenPair(access_token=access, refresh_token=refresh)

    @staticmethod
    def logout(db: Session, refresh_token: str) -> MessageOut:
        payload = SecurityService._validate_refresh_token(db, refresh_token)

        RefreshTokenRepository.revoke(db, jti=payload["jti"])
        logger.info(f"User {payload.get('sub')} logged out successfully")
        return MessageOut(message="ok")

    @staticmethod
    def refresh_tokens(db: Session, refresh_token: str) -> TokenPair:
        payload = SecurityService._validate_refresh_token(db, refresh_token)

        user_id = int(payload["sub"])
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
        logger.info(f"User {user_id} refreshed token successfully")

        return TokenPair(access_token=new_access, refresh_token=new_refresh)
