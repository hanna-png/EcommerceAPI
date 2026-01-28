from sqlalchemy import select
from sqlalchemy.orm import Session

from ecommerceapi.models.user import User


class UserRepository:
    @staticmethod
    def get_by_email(db: Session, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return db.execute(stmt).scalars().first()

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        return db.execute(stmt).scalars().first()

    @staticmethod
    def create(
        db: Session,
        *,
        email: str,
        hashed_password: str,
        first_name: str,
        last_name: str,
    ) -> User:
        user = User(
            email=email,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
        )
        db.add(user)
        db.flush()
        db.refresh(user)
        return user
