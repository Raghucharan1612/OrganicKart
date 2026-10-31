from __future__ import annotations

import os
import ipaddress
from pathlib import Path
from typing import Any
import uuid
import urllib.parse

import httpx
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.product_image import ProductImage, IMAGE_TYPE_UPLOAD, IMAGE_TYPE_URL
from app.models.category import Category
from app.models.products import Product
from app.repositories.product_repository import ProductRepository

# Schemes that are allowed for external image URLs
_ALLOWED_URL_SCHEMES = {"http", "https"}
# Maximum label length stored with URL images
_MAX_URL_LABEL_LEN = 200
# Maximum external URL length
_MAX_URL_LEN = 2048


def get_upload_dir() -> Path:
    base_dir = Path(__file__).resolve().parent.parent.parent
    upload_path = Path(settings.UPLOAD_DIR)
    if not upload_path.is_absolute():
        upload_path = base_dir / upload_path
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


def detect_and_validate_image_signature(content: bytes, declared_mime: str | None = None) -> tuple[str, str]:
    """
    Validates magic bytes of the image file.
    Supports JPEG, PNG, WebP, AVIF.
    Returns (detected_mime_type, file_extension).
    """
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded file is empty.",
        )

    if len(content) > settings.MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image size exceeds maximum limit of {settings.MAX_IMAGE_SIZE_BYTES // (1024 * 1024)}MB.",
        )

    # 1. JPEG
    if content.startswith(b"\xff\xd8\xff"):
        return "image/jpeg", ".jpg"

    # 2. PNG
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png", ".png"

    # 3. WebP
    if len(content) >= 12 and content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return "image/webp", ".webp"

    # 4. AVIF / HEIF
    if len(content) >= 12 and content[4:8] == b"ftyp" and content[8:12] in (b"avif", b"avis", b"mif1"):
        return "image/avif", ".avif"

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Unsupported image format or invalid file signature. Supported formats: JPEG, PNG, WebP, AVIF.",
    )


class ImageService:
    @staticmethod
    def _remove_category_upload(category: Category) -> None:
        if category.image_source != IMAGE_TYPE_UPLOAD or not category.image_filename:
            return
        upload_dir = get_upload_dir().resolve()
        file_path = (upload_dir / category.image_filename).resolve()
        if file_path.is_file() and str(file_path).startswith(str(upload_dir)):
            try:
                file_path.unlink()
            except OSError:
                pass

    @staticmethod
    def upload_category_image(db: Session, category: Category, file: UploadFile) -> Category:
        content = file.file.read()
        detected_mime, ext = detect_and_validate_image_signature(content, file.content_type)
        ImageService._remove_category_upload(category)
        filename = f"category_{uuid.uuid4().hex}{ext}"
        with open(get_upload_dir() / filename, "wb") as output:
            output.write(content)
        category.image_source = IMAGE_TYPE_UPLOAD
        category.image_filename = filename
        category.image_mime_type = detected_mime
        category.image_size = len(content)
        category.image_url = f"/api/v1/categories/images/{category.id}"
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def set_category_image_url(db: Session, category: Category, external_url: str) -> Category:
        ImageService._remove_category_upload(category)
        category.image_source = IMAGE_TYPE_URL
        category.image_filename = None
        category.image_mime_type = None
        category.image_size = None
        category.image_url = ImageService._validate_external_url(external_url)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def remove_category_image(db: Session, category: Category) -> Category:
        ImageService._remove_category_upload(category)
        category.image_source = None
        category.image_filename = None
        category.image_mime_type = None
        category.image_size = None
        category.image_url = None
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def get_category_image_file(category: Category) -> tuple[Path, str, str]:
        if category.image_source != IMAGE_TYPE_UPLOAD or not category.image_filename:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category image not found")
        upload_dir = get_upload_dir().resolve()
        file_path = (upload_dir / category.image_filename).resolve()
        if not str(file_path).startswith(str(upload_dir)) or not file_path.is_file():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category image file not found")
        return file_path, category.image_mime_type or "application/octet-stream", category.image_filename

    @staticmethod
    def _verify_product_ownership(product: Product, current_actor: dict[str, Any]) -> None:
        user_id = current_actor.get("user_id")
        if product.seller_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only manage images for products that you own.",
            )

    @staticmethod
    def upload_images(
        db: Session,
        product_id: int,
        files: list[UploadFile],
        current_actor: dict[str, Any],
    ) -> list[ProductImage]:
        product = ProductRepository.get_by_id(db, product_id, include_inactive=True)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        ImageService._verify_product_ownership(product, current_actor)

        if not files:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No files provided for upload.",
            )

        existing_images = (
            db.query(ProductImage)
            .filter(ProductImage.product_id == product_id)
            .order_by(ProductImage.id)
            .all()
        )

        if len(existing_images) + len(files) > settings.MAX_IMAGES_PER_PRODUCT:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Cannot exceed {settings.MAX_IMAGES_PER_PRODUCT} images per product. Product currently has {len(existing_images)} images.",
            )

        upload_dir = get_upload_dir()
        has_primary = any(img.is_primary for img in existing_images)
        saved_records: list[ProductImage] = []

        for idx, file in enumerate(files):
            # Read content
            content = file.file.read()
            detected_mime, ext = detect_and_validate_image_signature(content, file.content_type)

            safe_filename = f"{uuid.uuid4().hex}{ext}"
            file_path = upload_dir / safe_filename

            with open(file_path, "wb") as f:
                f.write(content)

            is_primary = False
            if not has_primary and idx == 0:
                is_primary = True
                has_primary = True

            image_record = ProductImage(
                product_id=product_id,
                filename=safe_filename,
                original_filename=file.filename or safe_filename,
                mime_type=detected_mime,
                file_size=len(content),
                is_primary=is_primary,
            )
            db.add(image_record)
            saved_records.append(image_record)

        db.commit()

        for rec in saved_records:
            db.refresh(rec)
            if rec.is_primary:
                product.image_url = rec.url

        db.commit()
        db.refresh(product)
        return saved_records

    @staticmethod
    def get_product_images(db: Session, product_id: int) -> list[ProductImage]:
        product = ProductRepository.get_by_id(db, product_id, include_inactive=True)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        return (
            db.query(ProductImage)
            .filter(ProductImage.product_id == product_id)
            .order_by(ProductImage.is_primary.desc(), ProductImage.id.asc())
            .all()
        )

    @staticmethod
    def get_image_file(db: Session, image_id: int) -> tuple[Path, str, str]:
        image_record = db.query(ProductImage).filter(ProductImage.id == image_id).first()
        if image_record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

        if image_record.image_type == IMAGE_TYPE_URL:
            # URL-type images don't have a local file — clients should use the external_url directly.
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This image is stored as an external URL and has no local file.",
            )

        if not image_record.filename:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image file not found")

        upload_dir = get_upload_dir()
        file_path = (upload_dir / image_record.filename).resolve()

        # Prevent directory traversal
        if not str(file_path).startswith(str(upload_dir.resolve())):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid file path")

        if not file_path.is_file():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image file not found on disk")

        return file_path, image_record.mime_type, image_record.original_filename

    # ------------------------------------------------------------------
    # URL-based image support
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_external_url(url: str) -> str:
        """
        Validates that *url* is a safe, reachable external image URL.
        Returns the normalised URL on success.
        Raises HTTPException on any validation failure.
        """
        stripped = (url or "").strip()
        if not stripped:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Image URL must not be empty.",
            )

        if len(stripped) > _MAX_URL_LEN:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Image URL exceeds the maximum length of {_MAX_URL_LEN} characters.",
            )

        try:
            parsed = urllib.parse.urlparse(stripped)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid image URL.",
            )

        if parsed.scheme.lower() not in _ALLOWED_URL_SCHEMES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Unsafe URL scheme '{parsed.scheme}'. "
                    "Only HTTP and HTTPS URLs are accepted."
                ),
            )

        if not parsed.netloc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Image URL must include a valid hostname.",
            )

        # Block private/loopback addresses (basic SSRF guard)
        hostname = parsed.hostname or ""
        _BLOCKED_HOSTS = {
            "localhost", "127.0.0.1", "0.0.0.0", "::1",
            "169.254.169.254",   # AWS metadata
            "metadata.google.internal",
        }
        try:
            host_ip = ipaddress.ip_address(hostname.strip("[]"))
            is_private_target = host_ip.is_private or host_ip.is_loopback or host_ip.is_link_local or host_ip.is_reserved or host_ip.is_unspecified
        except ValueError:
            # The service never resolves or fetches the host.  Browser image
            # loading is responsible for reachability, avoiding server-side
            # request forgery through a DNS lookup.
            is_private_target = False
        if hostname.lower().rstrip(".") in _BLOCKED_HOSTS or is_private_target:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="URL points to a private or reserved address and is not allowed.",
            )

        return stripped

    @staticmethod
    def add_image_url(
        db: Session,
        product_id: int,
        external_url: str,
        url_label: str | None,
        current_actor: dict[str, Any],
    ) -> ProductImage:
        """
        Validates and stores an external image URL for a product.
        Does NOT make any request to the external URL at creation time (the
        frontend verifies reachability via the browser's native image loading).
        """
        product = ProductRepository.get_by_id(db, product_id, include_inactive=True)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        ImageService._verify_product_ownership(product, current_actor)

        validated_url = ImageService._validate_external_url(external_url)

        existing_images = (
            db.query(ProductImage)
            .filter(ProductImage.product_id == product_id)
            .all()
        )

        if len(existing_images) >= settings.MAX_IMAGES_PER_PRODUCT:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Cannot exceed {settings.MAX_IMAGES_PER_PRODUCT} images per product.",
            )

        has_primary = any(img.is_primary for img in existing_images)
        label = (url_label or "").strip()[:_MAX_URL_LABEL_LEN] or None

        image_record = ProductImage(
            product_id=product_id,
            image_type=IMAGE_TYPE_URL,
            external_url=validated_url,
            url_label=label,
            is_primary=not has_primary,  # first image becomes primary
        )
        db.add(image_record)
        db.commit()
        db.refresh(image_record)

        if image_record.is_primary:
            product.image_url = image_record.url
            db.commit()
            db.refresh(product)

        return image_record

    @staticmethod
    def delete_image(
        db: Session,
        product_id: int,
        image_id: int,
        current_actor: dict[str, Any],
    ) -> dict[str, str]:
        product = ProductRepository.get_by_id(db, product_id, include_inactive=True)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        ImageService._verify_product_ownership(product, current_actor)

        image_record = (
            db.query(ProductImage)
            .filter(ProductImage.id == image_id, ProductImage.product_id == product_id)
            .first()
        )
        if image_record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found on product")

        was_primary = image_record.is_primary
        image_type = image_record.image_type
        filename = image_record.filename

        # Remove from db
        db.delete(image_record)
        db.commit()

        # Remove file from disk only for uploaded files
        if image_type == IMAGE_TYPE_UPLOAD and filename:
            upload_dir = get_upload_dir()
            file_path = (upload_dir / filename).resolve()
            if file_path.is_file() and str(file_path).startswith(str(upload_dir.resolve())):
                try:
                    file_path.unlink(missing_ok=True)
                except OSError:
                    pass

        # If deleted was primary, assign next primary if available
        if was_primary:
            remaining = (
                db.query(ProductImage)
                .filter(ProductImage.product_id == product_id)
                .order_by(ProductImage.id.asc())
                .first()
            )
            if remaining:
                remaining.is_primary = True
                product.image_url = remaining.url
            else:
                product.image_url = None
            db.commit()
            db.refresh(product)

        return {"message": "Image deleted successfully"}

    @staticmethod
    def replace_image(
        db: Session,
        product_id: int,
        image_id: int,
        file: UploadFile,
        current_actor: dict[str, Any],
    ) -> ProductImage:
        product = ProductRepository.get_by_id(db, product_id, include_inactive=True)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        ImageService._verify_product_ownership(product, current_actor)

        image_record = (
            db.query(ProductImage)
            .filter(ProductImage.id == image_id, ProductImage.product_id == product_id)
            .first()
        )
        if image_record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found on product")

        content = file.file.read()
        detected_mime, ext = detect_and_validate_image_signature(content, file.content_type)

        upload_dir = get_upload_dir()
        old_filename = image_record.filename

        new_filename = f"{uuid.uuid4().hex}{ext}"
        new_file_path = upload_dir / new_filename

        with open(new_file_path, "wb") as f:
            f.write(content)

        # Remove old file
        old_file_path = (upload_dir / old_filename).resolve() if old_filename else None
        if old_file_path and old_file_path.is_file() and str(old_file_path).startswith(str(upload_dir.resolve())):
            try:
                old_file_path.unlink(missing_ok=True)
            except OSError:
                pass

        image_record.filename = new_filename
        image_record.image_type = IMAGE_TYPE_UPLOAD
        image_record.external_url = None
        image_record.url_label = None
        image_record.original_filename = file.filename or new_filename
        image_record.mime_type = detected_mime
        image_record.file_size = len(content)

        db.commit()
        db.refresh(image_record)

        if image_record.is_primary:
            product.image_url = image_record.url
            db.commit()

        return image_record

    @staticmethod
    def set_primary_image(
        db: Session,
        product_id: int,
        image_id: int,
        current_actor: dict[str, Any],
    ) -> ProductImage:
        product = ProductRepository.get_by_id(db, product_id, include_inactive=True)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        ImageService._verify_product_ownership(product, current_actor)

        target_image = (
            db.query(ProductImage)
            .filter(ProductImage.id == image_id, ProductImage.product_id == product_id)
            .first()
        )
        if target_image is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found on product")

        # Set all others to false
        db.query(ProductImage).filter(ProductImage.product_id == product_id).update({"is_primary": False})
        target_image.is_primary = True
        product.image_url = target_image.url

        db.commit()
        db.refresh(target_image)
        db.refresh(product)
        return target_image
