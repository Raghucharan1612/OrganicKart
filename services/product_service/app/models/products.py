from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column,relationship

from app.database.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    seller_id: Mapped[int] = mapped_column(
        nullable=False,
        index=True
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False,
        index=True
    )

    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="products"
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    stock_quantity: Mapped[int] = mapped_column(
        nullable=False,
        default=0
    )

    unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    certification: Mapped[str] = mapped_column(
        String(100),
        default="PENDING",
        nullable=False
    )

    image_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )