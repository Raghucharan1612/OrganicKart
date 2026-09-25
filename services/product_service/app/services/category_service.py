from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.categories import CategoryCreate, CategoryUpdate


class CategoryService:

    @staticmethod
    def create_category(db: Session, category_data: CategoryCreate) -> Category:
        existing = CategoryRepository.get_by_name(db, category_data.name)
        if existing is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists")

        category = Category(
            name=category_data.name,
            description=category_data.description,
            image_url=category_data.image_url,
            is_active=category_data.is_active,
        )
        return CategoryRepository.create(db, category)

    @staticmethod
    def get_categories(db: Session) -> list[Category]:
        return CategoryRepository.get_all(db)

    @staticmethod
    def get_category(db: Session, category_id: int) -> Category:
        category = CategoryRepository.get_by_id(db, category_id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        return category

    @staticmethod
    def update_category(db: Session, category_id: int, category_data: CategoryUpdate) -> Category:
        category = CategoryRepository.get_by_id(db, category_id, include_inactive=True)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        update_data = category_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)

        return CategoryRepository.update(db, category)

    @staticmethod
    def delete_category(db: Session, category_id: int) -> Category:
        category = CategoryRepository.get_by_id(db, category_id, include_inactive=True)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        return CategoryRepository.delete(db, category)
