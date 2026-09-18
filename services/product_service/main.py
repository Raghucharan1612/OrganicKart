from fastapi import FastAPI

from app.api.routes.categories import router as category_router
from app.api.routes.products import router as product_router
from app.database.base import Base
from app.database.database import engine


app = FastAPI(
    title="OrganicKart Product Service",
    description="Product catalog microservice for OrganicKart",
    version="1.0.0",
)


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)


app.include_router(
    category_router,
    prefix="/api/v1",
)

app.include_router(
    product_router,
    prefix="/api/v1",
)


@app.get("/")
def root():
    return {
        "service": "product-service",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "service": "product-service",
        "status": "healthy",
    }