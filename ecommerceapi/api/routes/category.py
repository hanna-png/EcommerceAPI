from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ecommerceapi.db.database import get_db
from ecommerceapi.schemas.category import CategoryOut
from ecommerceapi.repositories.category import CategoryRepository

category_router = APIRouter(prefix="/categories", tags=["categories"])


@category_router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)) -> list[CategoryOut]:
    """
    Retrieve a list of all product categories.
    """
    return CategoryRepository.get_all(db)
