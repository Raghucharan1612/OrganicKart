from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.database.base import Base
from app.database.session import engine

from sqlalchemy import inspect, text

Base.metadata.create_all(bind=engine)

delivery_columns = {column["name"] for column in inspect(engine).get_columns("deliveries")}
with engine.begin() as conn:
    if "assigned_partner_id" not in delivery_columns:
        conn.execute(text("ALTER TABLE deliveries ADD COLUMN assigned_partner_id INTEGER"))
    if "accepted_at" not in delivery_columns:
        conn.execute(text("ALTER TABLE deliveries ADD COLUMN accepted_at DATETIME"))

app = FastAPI(
    title="OrganicKart Delivery Service",
    description="Delivery and shipment tracking service for OrganicKart",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root() -> dict:
    return {"service": "delivery-service", "status": "running"}


@app.get("/health")
def health() -> dict:
    return {"service": "delivery-service", "status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=settings.SERVICE_PORT, reload=False)
