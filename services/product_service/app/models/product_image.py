from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

# Discriminator constants
IMAGE_TYPE_UPLOAD = "UPLOAD"
IMAGE_TYPE_URL = "URL"


class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Discriminator: "UPLOAD" or "URL"
    image_type: Mapped[str] = mapped_column(String(10), nullable=False, default=IMAGE_TYPE_UPLOAD)

    # --- Fields for uploaded files (image_type == "UPLOAD") ---
    filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    original_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # --- Fields for external URLs (image_type == "URL") ---
    external_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    # Display label shown to the vendor instead of a filename
    url_label: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    product: Mapped["Product"] = relationship("Product", back_populates="images")

    @property
    def url(self) -> str:
        if self.image_type == IMAGE_TYPE_URL and self.external_url:
            return self.external_url
        return f"/api/v1/products/images/{self.id}"
