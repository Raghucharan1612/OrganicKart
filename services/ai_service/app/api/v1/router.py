from fastapi import APIRouter

from app.api.v1.chat import router as chat_router
from app.api.v1.admin_chat import router as admin_chat_router
from app.api.v1.vendor_chat import router as vendor_chat_router

api_router = APIRouter()
api_router.include_router(chat_router, prefix="/ai", tags=["ai"])
api_router.include_router(admin_chat_router, prefix="/ai", tags=["admin-ai"])
api_router.include_router(vendor_chat_router, prefix="/ai", tags=["vendor-ai"])
