from fastapi import APIRouter

from app.api.v1.deliveries import router as delivery_router

api_router = APIRouter()
api_router.include_router(delivery_router, prefix="")

router = api_router
