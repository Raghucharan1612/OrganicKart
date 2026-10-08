from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.categories import CategoryResponse


class ProductCreate(BaseModel):
    category_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1)
    description: str | None = None
    price: Decimal = Field(..., gt=0)
    stock_quantity: int = Field(default=0, ge=0)
    unit: str = Field(..., min_length=1)
    image_url: str | None = None
    is_active: bool = True


class ProductUpdate(BaseModel):
    seller_id: int | None = Field(default=None, gt=0)
    category_id: int | None = Field(default=None, gt=0)
    name: str | None = Field(default=None, min_length=1)
    description: str | None = None
    price: Decimal | None = Field(default=None, gt=0)
    stock_quantity: int | None = Field(default=None, ge=0)
    unit: str | None = Field(default=None, min_length=1)
    image_url: str | None = None
    is_active: bool | None = None


class ProductResponse(BaseModel):
    id: int
    seller_id: int
    category_id: int
    category: CategoryResponse | None = None
    name: str
    description: str | None = None
    price: Decimal
    stock_quantity: int
    unit: str
    certification: str | None = None
    image_url: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LowStockProductsResponse(BaseModel):
    threshold: int
    items: list[ProductResponse]
