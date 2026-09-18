from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AddressCreate(BaseModel):
    label: str = Field(default="Home", min_length=1, max_length=80)
    recipient_name: str = Field(min_length=2, max_length=150)
    phone: str = Field(min_length=3, max_length=20)
    address_line1: str = Field(min_length=2, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str = Field(min_length=2, max_length=120)
    state: str = Field(min_length=2, max_length=120)
    postal_code: str = Field(min_length=3, max_length=20)
    country: str = Field(default="India", min_length=2, max_length=100)
    latitude: Decimal | None = Field(default=None, ge=-90, le=90)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180)
    is_default: bool = False


class AddressUpdate(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=80)
    recipient_name: str | None = Field(default=None, min_length=2, max_length=150)
    phone: str | None = Field(default=None, min_length=3, max_length=20)
    address_line1: str | None = Field(default=None, min_length=2, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, min_length=2, max_length=120)
    state: str | None = Field(default=None, min_length=2, max_length=120)
    postal_code: str | None = Field(default=None, min_length=3, max_length=20)
    country: str | None = Field(default=None, min_length=2, max_length=100)
    latitude: Decimal | None = Field(default=None, ge=-90, le=90)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180)
    is_default: bool | None = None


class AddressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    label: str
    recipient_name: str
    phone: str
    address_line1: str
    address_line2: str | None = None
    city: str
    state: str
    postal_code: str
    country: str
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    is_default: bool
    created_at: datetime
    updated_at: datetime
