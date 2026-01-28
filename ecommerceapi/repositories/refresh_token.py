from datetime import datetime, timezone
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from ecommerceapi.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    @staticmethod
    def create(
        db: Session, *, user_id: int, jti: str, token_hash: str, expires_at: datetime
    ) -> RefreshToken:
        rt = RefreshToken(
            user_id=user_id,
            jti=jti,
            token_hash=token_hash,
            expires_at=expires_at,
            revoked_at=None,
        )
        db.add(rt)
        db.flush()
        db.refresh(rt)
        return rt

    @staticmethod
    def get_by_jti(db: Session, jti: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.jti == jti)
        return db.execute(stmt).scalars().first()

    @staticmethod
    def get_valid_by_jti(db: Session, jti: str) -> RefreshToken | None:
        rt = RefreshTokenRepository.get_by_jti(db, jti)
        if not rt:
            return None
        if rt.revoked_at is not None:
            return None
        if rt.expires_at <= datetime.now(timezone.utc):
            return None
        return rt

    @staticmethod
    def revoke(db: Session, *, jti: str) -> None:
        db.execute(
            update(RefreshToken)
            .where(RefreshToken.jti == jti)
            .values(revoked_at=datetime.now(timezone.utc))
        )

    @staticmethod
    def revoke_all_for_user(db: Session, *, user_id: int) -> None:
        db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=datetime.now(timezone.utc))
        )
