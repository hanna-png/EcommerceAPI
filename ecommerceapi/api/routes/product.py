from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ecommerceapi.db.database import get_db
from ecommerceapi.schemas.product import ProductListOut
from ecommerceapi.repositories.product import ProductRepository

product_router = APIRouter(prefix="/products", tags=["products"])


@product_router.get("/search", response_model=list[ProductListOut])
def search_products(
    search_text: str, db: Session = Depends(get_db)
) -> list[ProductListOut]:
    """
    Retrieve a product that contains given search text.
    """
    return ProductRepository().search(db, search_text)
