from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.database.database import get_db
from app.schemas.categories import CategoryCreate, CategoryImageUrlRequest, CategoryResponse, CategoryUpdate
from app.services.category_service import CategoryService
from app.services.image_service import ImageService

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    return CategoryService.create_category(db, category)


@router.get("/", response_model=list[CategoryResponse])
def get_categories(
    db: Session = Depends(get_db)
):
    return CategoryService.get_categories(db)


@router.get("/images/{category_id}")
def get_category_image(category_id: int, db: Session = Depends(get_db)):
    category = CategoryService.get_category(db, category_id)
    file_path, mime_type, filename = ImageService.get_category_image_file(category)
    return FileResponse(file_path, media_type=mime_type, filename=filename, headers={"Cache-Control": "public, max-age=86400"})


@router.post("/{category_id}/image", response_model=CategoryResponse)
def upload_category_image(
    category_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    category = CategoryService.get_category(db, category_id)
    return ImageService.upload_category_image(db, category, file)


@router.put("/{category_id}/image/url", response_model=CategoryResponse)
def set_category_image_url(
    category_id: int,
    body: CategoryImageUrlRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    category = CategoryService.get_category(db, category_id)
    return ImageService.set_category_image_url(db, category, body.external_url)


@router.delete("/{category_id}/image", response_model=CategoryResponse)
def remove_category_image(
    category_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    category = CategoryService.get_category(db, category_id)
    return ImageService.remove_category_image(db, category)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    return CategoryService.get_category(db, category_id)


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    return CategoryService.update_category(db, category_id, category)


@router.delete("/{category_id}", response_model=CategoryResponse)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    return CategoryService.delete_category(db, category_id)
