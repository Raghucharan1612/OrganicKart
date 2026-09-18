from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.database.base import Base
from app.database.session import engine

import app.models.notification  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OrganicKart Notification Service",
    description="In-app notification service for OrganicKart",
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
    return {"service": "notification-service", "status": "running"}


@app.get("/health")
def health() -> dict:
    return {"service": "notification-service", "status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=settings.SERVICE_PORT, reload=False)
