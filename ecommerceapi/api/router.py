from fastapi import APIRouter
from ecommerceapi.api.routes.category import category_router
from ecommerceapi.api.routes.product import product_router

api_router = APIRouter()
api_router.include_router(category_router)
api_router.include_router(product_router)
