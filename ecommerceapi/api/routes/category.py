from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ecommerceapi.db.database import get_db
from ecommerceapi.schemas.category import CategoryOut
from ecommerceapi.schemas.product import ProductListOut
from ecommerceapi.repositories.category import CategoryRepository
from ecommerceapi.repositories.product import ProductRepository

category_router = APIRouter(prefix="/categories", tags=["categories"])


@category_router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)) -> list[CategoryOut]:
    """
    Retrieve a list of all product categories.
    """
    return CategoryRepository.get_all(db)


@category_router.get("/{category_id}/products", response_model=list[ProductListOut])
def category_products(
    category_id: int, db: Session = Depends(get_db)
) -> list[ProductListOut]:
    """
    Retrieve a list of all available products in a specific category.
    """
    return ProductRepository.get_by_category(db, category_id)
