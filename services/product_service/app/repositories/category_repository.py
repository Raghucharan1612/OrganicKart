from sqlalchemy.orm import Session

from app.models.category import Category


class CategoryRepository:

    @staticmethod
    def create(db: Session, category: Category) -> Category:
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def get_all(db: Session, *, include_inactive: bool = False) -> list[Category]:
        query = db.query(Category)
        if not include_inactive:
            query = query.filter(Category.is_active.is_(True))
        return query.order_by(Category.created_at.desc()).all()

    @staticmethod
    def get_by_id(db: Session, category_id: int, *, include_inactive: bool = False) -> Category | None:
        query = db.query(Category).filter(Category.id == category_id)
        if not include_inactive:
            query = query.filter(Category.is_active.is_(True))
        return query.first()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Category | None:
        return db.query(Category).filter(Category.name == name).first()

    @staticmethod
    def update(db: Session, category: Category) -> Category:
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def delete(db: Session, category: Category) -> Category:
        category.is_active = False
        db.commit()
        db.refresh(category)
        return category
