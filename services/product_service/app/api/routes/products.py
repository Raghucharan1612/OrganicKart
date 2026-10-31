from decimal import Decimal

from fastapi import APIRouter, Body, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.security import get_optional_actor, require_admin, require_catalog_manager
from app.database.database import get_db
from app.schemas.products import (
    LowStockProductsResponse,
    ProductCreate,
    ProductImageResponse,
    ProductImageUrlRequest,
    ProductResponse,
    ProductUpdate,
)
from app.services.image_service import ImageService
from app.services.product_service import ProductService

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


def _require_product_mutation_owner(product, current_actor: dict) -> None:
    """Allow product changes only from the JWT subject that owns the product.

    ``seller_id`` is the existing ownership field for both vendor listings and
    administrator-created listings.  Administrative certification decisions
    intentionally use their own endpoints below and are not covered by this
    check.
    """
    if product.seller_id != current_actor["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only manage products that you own.",
        )


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_actor: dict = Depends(require_catalog_manager),
):
    return ProductService.create_product(db, product, seller_id=current_actor["user_id"])


@router.get("/", response_model=None)
def get_products(
    db: Session = Depends(get_db),
    search: str | None = Query(default=None),
    category_id: int | None = Query(default=None),
    seller_id: int | None = Query(default=None),
    certification: str | None = Query(default=None),
    min_price: Decimal | None = Query(default=None, ge=0),
    max_price: Decimal | None = Query(default=None, ge=0),
    sort_by: str = Query(default="created_at", pattern="^(name|price|created_at)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_actor: dict | None = Depends(get_optional_actor),
):
    can_view_certification_queue = (
        current_actor is not None
        and current_actor["role"] in {"ADMIN", "SUPER_ADMIN"}
        and certification is not None
    )
    items, total = ProductService.get_products(
        db,
        search=search,
        category_id=category_id,
        seller_id=seller_id if can_view_certification_queue or (current_actor and current_actor["role"] in {"ADMIN", "SUPER_ADMIN"}) else seller_id,
        certification=certification if can_view_certification_queue else None,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
        customer_visible=not can_view_certification_queue,
    )
    serialized_items = [ProductResponse.model_validate(p) for p in items]
    if search is not None or category_id is not None or seller_id is not None or certification is not None or min_price is not None or max_price is not None or page != 1 or page_size != 20 or sort_by != "created_at" or sort_order != "desc":
        return {"items": serialized_items, "total": total, "page": page, "page_size": page_size}
    return serialized_items


@router.get("/mine", response_model=list[ProductResponse])
def get_my_products(
    db: Session = Depends(get_db),
    current_actor: dict = Depends(require_catalog_manager),
):
    items, _ = ProductService.get_products(
        db,
        seller_id=current_actor["user_id"],
        sort_by="created_at",
        sort_order="desc",
        page=1,
        page_size=1000,
        customer_visible=False,
    )
    return items


@router.get("/admin/low-stock", response_model=LowStockProductsResponse)
def get_low_stock_products(
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    return LowStockProductsResponse(
        threshold=ProductService.LOW_STOCK_THRESHOLD,
        items=ProductService.get_low_stock_active_products(db),
    )


@router.get("/images/{image_id}")
def get_product_image_file(
    image_id: int,
    db: Session = Depends(get_db),
):
    file_path, mime_type, original_filename = ImageService.get_image_file(db, image_id)
    return FileResponse(
        path=file_path,
        media_type=mime_type,
        filename=original_filename,
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_actor: dict | None = Depends(get_optional_actor),
):
    if current_actor and current_actor["role"] in {"ADMIN", "SUPER_ADMIN"}:
        return ProductService.get_product(db, product_id, customer_visible=False)

    if current_actor and current_actor["role"] in {"VENDOR", "FARMER"}:
        product = ProductService.get_product(db, product_id, customer_visible=False)
        if product.seller_id == current_actor["user_id"]:
            return product

    return ProductService.get_product(db, product_id)


@router.post("/{product_id}/images", response_model=list[ProductImageResponse], status_code=status.HTTP_201_CREATED)
def upload_product_images(
    product_id: int,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_actor: dict = Depends(require_catalog_manager),
):
    return ImageService.upload_images(db, product_id, files, current_actor)


@router.post("/{product_id}/images/url", response_model=ProductImageResponse, status_code=status.HTTP_201_CREATED)
def add_product_image_url(
    product_id: int,
    body: ProductImageUrlRequest,
    db: Session = Depends(get_db),
    current_actor: dict = Depends(require_catalog_manager),
):
    """Add an external image URL to a product. Only HTTP/HTTPS URLs are accepted."""
    return ImageService.add_image_url(db, product_id, body.external_url, body.url_label, current_actor)


@router.get("/{product_id}/images", response_model=list[ProductImageResponse])
def get_product_images(
    product_id: int,
    db: Session = Depends(get_db),
):
    return ImageService.get_product_images(db, product_id)


@router.delete("/{product_id}/images/{image_id}")
def delete_product_image(
    product_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    current_actor: dict = Depends(require_catalog_manager),
):
    return ImageService.delete_image(db, product_id, image_id, current_actor)


@router.put("/{product_id}/images/{image_id}", response_model=ProductImageResponse)
def replace_product_image(
    product_id: int,
    image_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_actor: dict = Depends(require_catalog_manager),
):
    return ImageService.replace_image(db, product_id, image_id, file, current_actor)


@router.patch("/{product_id}/images/{image_id}/primary", response_model=ProductImageResponse)
def set_primary_product_image(
    product_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    current_actor: dict = Depends(require_catalog_manager),
):
    return ImageService.set_primary_image(db, product_id, image_id, current_actor)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_actor: dict = Depends(require_catalog_manager),
):
    existing = ProductService.get_product(db, product_id, customer_visible=False)
    _require_product_mutation_owner(existing, current_actor)
    reset_approval = current_actor["role"] not in {"ADMIN", "SUPER_ADMIN"}
    return ProductService.update_product(db, product_id, product, reset_approval=reset_approval)


@router.post("/{product_id}/approve", response_model=ProductResponse)
def approve_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    return ProductService.approve_product(db, product_id)


@router.post("/{product_id}/reject", response_model=ProductResponse)
def reject_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    return ProductService.reject_product(db, product_id)


@router.delete("/{product_id}", response_model=ProductResponse)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_actor: dict = Depends(require_catalog_manager),
):
    existing = ProductService.get_product(db, product_id, customer_visible=False)
    _require_product_mutation_owner(existing, current_actor)
    return ProductService.delete_product(db, product_id)
