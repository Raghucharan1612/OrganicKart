from fastapi import APIRouter

from app.api.v1.cart import router as cart_router
from app.api.v1.orders import router as orders_router

api_router = APIRouter()
api_router.include_router(cart_router, prefix="")
api_router.include_router(orders_router, prefix="")

router = api_router
