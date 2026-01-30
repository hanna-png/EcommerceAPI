from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ecommerceapi.db.database import get_db
from ecommerceapi.schemas.product import (
    ProductListOut,
    ProductDetailOut,
    ProductSerializedOut,
)
from ecommerceapi.repositories.product import ProductRepository
from ecommerceapi.serializers.product_serializer import serialize_product


product_router = APIRouter(prefix="/products", tags=["products"])


@product_router.get("/search", response_model=list[ProductListOut])
def search_products(
    search_text: str, db: Session = Depends(get_db)
) -> list[ProductListOut]:
    """
    Retrieve a product that contains given search text.
    """
    return ProductRepository().search(db, search_text)


@product_router.get("/{product_id}/details", response_model=ProductDetailOut)
def get_product_details(
    product_id: int, db: Session = Depends(get_db)
) -> ProductDetailOut:
    """
    Retrieve a detailed description of a product.
    """
    return ProductRepository().get_by_id(db, product_id)


@product_router.get("/{product_id}/serialized", response_model=ProductSerializedOut)
def get_product_serialized(
    product_id: int, db: Session = Depends(get_db)
) -> ProductSerializedOut:
    """Endpoint for testing serialization"""
    product = ProductRepository.get_by_id(db, product_id)
    return serialize_product(product)
