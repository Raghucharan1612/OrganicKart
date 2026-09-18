import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class PaymentStatus(str, enum.Enum):
    PAYMENT_PENDING = "PAYMENT_PENDING"
    PAID = "PAID"
    FAILED = "FAILED"


class PaymentAttempt(Base):
    __tablename__ = "payment_attempts"
    __table_args__ = (
        UniqueConstraint("provider_order_id", name="uq_payment_attempt_provider_order_id"),
        UniqueConstraint("provider_payment_id", name="uq_payment_attempt_provider_payment_id"),
        UniqueConstraint("idempotency_key", name="uq_payment_attempt_idempotency_key"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(30), nullable=False)
    provider_order_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    provider_payment_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default=PaymentStatus.PAYMENT_PENDING.value)
    amount_paise: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    signature: Mapped[str | None] = mapped_column(String(512), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(64), nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
