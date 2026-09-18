from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DeliveryAddress(BaseModel):
    recipient_name: str = Field(..., min_length=2, max_length=200)
    recipient_phone: str | None = Field(default=None, max_length=30)
    address_line1: str = Field(..., min_length=2, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str = Field(..., min_length=2, max_length=120)
    state: str | None = Field(default=None, max_length=120)
    postal_code: str = Field(..., min_length=3, max_length=20)
    country: str = Field(..., min_length=2, max_length=100)


class DeliveryCreate(BaseModel):
    order_id: int = Field(..., gt=0)
    address: DeliveryAddress


class DeliveryUpdate(BaseModel):
    recipient_name: str | None = Field(default=None, min_length=2, max_length=200)
    recipient_phone: str | None = Field(default=None, max_length=30)
    address_line1: str | None = Field(default=None, min_length=2, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, min_length=2, max_length=120)
    state: str | None = Field(default=None, max_length=120)
    postal_code: str | None = Field(default=None, min_length=3, max_length=20)
    country: str | None = Field(default=None, min_length=2, max_length=100)
    estimated_delivery_date: datetime | None = None


class DeliveryStatusUpdate(BaseModel):
    status: str = Field(..., min_length=2, max_length=30)


class DeliveryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    user_id: int
    assigned_partner_id: int | None = None
    tracking_number: str
    status: str
    recipient_name: str
    recipient_phone: str | None = None
    address_line1: str
    address_line2: str | None = None
    city: str
    state: str | None = None
    postal_code: str
    country: str
    estimated_delivery_date: datetime | None = None
    accepted_at: datetime | None = None
    shipped_at: datetime | None = None
    delivered_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
