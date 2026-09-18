import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class NotificationType(str, enum.Enum):
    WELCOME = "WELCOME"
    ORDER_CREATED = "ORDER_CREATED"
    ORDER_CONFIRMED = "ORDER_CONFIRMED"
    ORDER_CANCELLED = "ORDER_CANCELLED"
    PAYMENT_SUCCESS = "PAYMENT_SUCCESS"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    DELIVERY_CONFIRMED = "DELIVERY_CONFIRMED"
    DELIVERY_SHIPPED = "DELIVERY_SHIPPED"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"


class NotificationChannel(str, enum.Enum):
    IN_APP = "IN_APP"
    EMAIL = "EMAIL"


class NotificationStatus(str, enum.Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    READ = "READ"
    FAILED = "FAILED"


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "type",
            "reference_type",
            "reference_id",
            name="uq_notification_event",
        ),
        Index("ix_notifications_user_status", "user_id", "status"),
        Index("ix_notifications_reference", "reference_type", "reference_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType, native_enum=False, length=40), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[NotificationChannel] = mapped_column(
        Enum(NotificationChannel, native_enum=False, length=20), nullable=False, default=NotificationChannel.IN_APP
    )
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus, native_enum=False, length=20), nullable=False, default=NotificationStatus.PENDING, index=True
    )
    reference_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    reference_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False, index=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
