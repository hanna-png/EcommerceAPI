from sqlalchemy import select
from sqlalchemy.orm import Session

from ecommerceapi.models.address import Address


class AddressRepository:
    @staticmethod
    def create(
        db: Session,
        *,
        user_id: int,
        city: str,
        region: str | None,
        postal_code: str,
        country: str,
    ) -> Address:
        addr = Address(
            user_id=user_id,
            city=city,
            region=region,
            postal_code=postal_code,
            country=country,
        )
        db.add(addr)
        db.commit()
        db.refresh(addr)
        return addr

    @staticmethod
    def get_by_user_id(db: Session, user_id: int) -> Address | None:
        stmt = select(Address).where(Address.user_id == user_id)
        return db.execute(stmt).scalars().first()
