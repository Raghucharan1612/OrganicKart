from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import require_catalog_manager
from app.database.database import get_db
from app.schemas.categories import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services.category_service import CategoryService

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_catalog_manager),
):
    return CategoryService.create_category(db, category)


@router.get("/", response_model=list[CategoryResponse])
def get_categories(
    db: Session = Depends(get_db)
):
    return CategoryService.get_categories(db)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    return CategoryService.get_category(db, category_id)


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_catalog_manager),
):
    return CategoryService.update_category(db, category_id, category)


@router.delete("/{category_id}", response_model=CategoryResponse)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_catalog_manager),
):
    return CategoryService.delete_category(db, category_id)
