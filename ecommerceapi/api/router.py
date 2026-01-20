from fastapi import APIRouter
from ecommerceapi.api.routes.category import category_router

api_router = APIRouter()
api_router.include_router(category_router)
