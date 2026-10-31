from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.categories import CategoryCreate, CategoryUpdate
from app.models.product_image import IMAGE_TYPE_URL


class CategoryService:

    @staticmethod
    def create_category(db: Session, category_data: CategoryCreate) -> Category:
        existing = CategoryRepository.get_by_name(db, category_data.name)
        if existing is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists")

        image_url = category_data.image_url
        if image_url:
            # Legacy JSON creation remains supported, but gets the same URL
            # safety validation and persisted source metadata as the new UI.
            from app.services.image_service import ImageService
            image_url = ImageService._validate_external_url(image_url)
        category = Category(
            name=category_data.name,
            description=category_data.description,
            image_url=image_url,
            image_source=IMAGE_TYPE_URL if image_url else None,
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
        if "image_url" in update_data:
            image_url = update_data["image_url"]
            if image_url:
                from app.services.image_service import ImageService
                update_data["image_url"] = ImageService._validate_external_url(image_url)
                # Replacing an upload through the legacy field must not leave
                # stale file metadata behind.
                ImageService._remove_category_upload(category)
                update_data.update(image_source=IMAGE_TYPE_URL, image_filename=None, image_mime_type=None, image_size=None)
            else:
                from app.services.image_service import ImageService
                ImageService._remove_category_upload(category)
                update_data.update(image_source=None, image_filename=None, image_mime_type=None, image_size=None)
        for field, value in update_data.items():
            setattr(category, field, value)

        return CategoryRepository.update(db, category)

    @staticmethod
    def delete_category(db: Session, category_id: int) -> Category:
        category = CategoryRepository.get_by_id(db, category_id, include_inactive=True)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        return CategoryRepository.delete(db, category)
