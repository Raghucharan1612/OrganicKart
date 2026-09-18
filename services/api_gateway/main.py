from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.proxy import router as gateway_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="OrganicKart API Gateway",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(gateway_router)


@app.get("/")
def root() -> dict:
    return {"service": "api-gateway", "status": "running"}


@app.get("/health")
def health() -> dict:
    return {
        "service": "api-gateway",
        "status": "healthy",
        "dependencies": {
            "auth": settings.AUTH_SERVICE_URL,
            "products": settings.PRODUCT_SERVICE_URL,
            "orders": settings.ORDER_SERVICE_URL,
            "deliveries": settings.DELIVERY_SERVICE_URL,
            "notifications": settings.NOTIFICATION_SERVICE_URL,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=settings.SERVICE_PORT, reload=False)
