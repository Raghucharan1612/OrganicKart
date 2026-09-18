from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import router as api_router
from app.database.session import Base, engine
from sqlalchemy import inspect, text

Base.metadata.create_all(bind=engine)

# `create_all` creates new tables but does not add fields to an existing one.
# Use SQLAlchemy's database-agnostic inspector so both MySQL and SQLite receive
# the nullable cart metadata fields introduced by the cart response contract.
cart_item_columns = {column["name"] for column in inspect(engine).get_columns("cart_items")}
order_columns = {column["name"] for column in inspect(engine).get_columns("orders")}
order_item_columns = {column["name"] for column in inspect(engine).get_columns("order_items")}
with engine.begin() as conn:
    if "image_url" not in cart_item_columns:
        conn.execute(text("ALTER TABLE cart_items ADD COLUMN image_url VARCHAR(500)"))
    if "unit" not in cart_item_columns:
        conn.execute(text("ALTER TABLE cart_items ADD COLUMN unit VARCHAR(50)"))
    if "payment_status" not in order_columns:
        conn.execute(text("ALTER TABLE orders ADD COLUMN payment_status VARCHAR(30) NOT NULL DEFAULT 'PAYMENT_PENDING'"))
    if "confirmed_at" not in order_columns:
        conn.execute(text("ALTER TABLE orders ADD COLUMN confirmed_at DATETIME"))
    if "image_url" not in order_item_columns:
        conn.execute(text("ALTER TABLE order_items ADD COLUMN image_url VARCHAR(500)"))
    if "unit" not in order_item_columns:
        conn.execute(text("ALTER TABLE order_items ADD COLUMN unit VARCHAR(50)"))

app = FastAPI(
    title="OrganicKart Order Service",
    description="Order and cart service for OrganicKart",
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
    return {"service": "order-service", "status": "running"}


@app.get("/health")
def health() -> dict:
    return {"service": "order-service", "status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=settings.SERVICE_PORT, reload=False)
