from datetime import datetime, timezone
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from ecommerceapi.models.refresh_token import RefreshToken
from ecommerceapi.core.exceptions import ResourceNotFoundException


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
    def get_by_jti(db: Session, jti: str) -> RefreshToken:
        stmt = select(RefreshToken).where(RefreshToken.jti == jti)
        t = db.execute(stmt).scalars().first()
        if not t:
            raise ResourceNotFoundException(f"Refresh token not found for {jti}")
        return t

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
