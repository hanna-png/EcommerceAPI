from sqlalchemy import select
from sqlalchemy.orm import Session

from ecommerceapi.models.address import Address
from ecommerceapi.core.exceptions import ResourceNotFoundException


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
        db.flush()
        db.refresh(addr)
        return addr

    @staticmethod
    def get_by_user_id(db: Session, user_id: int) -> Address:
        stmt = select(Address).where(Address.user_id == user_id)
        address = db.execute(stmt).scalars().first()
        if not address:
            raise ResourceNotFoundException(f"Address for user_id={user_id} not found")
        return address
