from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.notification import NotificationChannel, NotificationStatus, NotificationType


class NotificationCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    type: NotificationType
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1)
    channel: NotificationChannel = NotificationChannel.IN_APP
    reference_type: str | None = Field(default=None, max_length=80)
    reference_id: int | None = Field(default=None, gt=0)


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    type: NotificationType
    title: str
    message: str
    channel: NotificationChannel
    status: NotificationStatus
    reference_type: str | None
    reference_id: int | None
    created_at: datetime
    sent_at: datetime | None
    read_at: datetime | None
    updated_at: datetime
