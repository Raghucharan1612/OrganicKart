from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: str | None = None
    image_url: str | None = None
    is_active: bool = True


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    description: str | None = None
    image_url: str | None = None
    is_active: bool | None = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    image_url: str | None = None
    image_source: str | None = None
    image_filename: str | None = None
    image_mime_type: str | None = None
    image_size: int | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoryImageUrlRequest(BaseModel):
    external_url: str = Field(..., min_length=1, max_length=2048)
