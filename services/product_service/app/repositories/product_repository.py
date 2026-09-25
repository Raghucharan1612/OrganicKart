from decimal import Decimal

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.products import Product


class ProductRepository:

    @staticmethod
    def create(db: Session, product: Product) -> Product:
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def get_all(
        db: Session,
        *,
        include_inactive: bool = False,
        search: str | None = None,
        category_id: int | None = None,
        seller_id: int | None = None,
        certification: str | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Product], int]:
        query = db.query(Product)
        if not include_inactive:
            query = query.filter(Product.is_active.is_(True))

        if search:
            keyword = search.strip()
            if keyword:
                words = [w for w in keyword.split() if w]
                word_filters = []
                for w in words:
                    pattern = f"%{w}%"
                    word_filters.append(
                        or_(
                            Product.name.ilike(pattern),
                            Product.description.ilike(pattern),
                        )
                    )
                if word_filters:
                    query = query.filter(and_(*word_filters))

        if category_id is not None:
            query = query.filter(Product.category_id == category_id)

        if seller_id is not None:
            query = query.filter(Product.seller_id == seller_id)

        if certification is not None:
            normalized = certification.strip().upper()
            if normalized in {"PENDING", "APPROVED", "REJECTED"}:
                query = query.filter(Product.certification == normalized)

        if min_price is not None:
            query = query.filter(Product.price >= min_price)

        if max_price is not None:
            query = query.filter(Product.price <= max_price)

        allowed_sort_fields = {"name": Product.name, "price": Product.price, "created_at": Product.created_at}
        if sort_by in allowed_sort_fields:
            order_field = allowed_sort_fields[sort_by]
            query = query.order_by(order_field.asc() if sort_order == "asc" else order_field.desc())
        else:
            raise ValueError("Invalid sort_by value")

        total = query.count()
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()
        return items, total

    @staticmethod
    def get_by_id(
        db: Session,
        product_id: int,
        *,
        include_inactive: bool = False,
        certification: str | None = None,
    ) -> Product | None:
        query = db.query(Product).filter(Product.id == product_id)
        if not include_inactive:
            query = query.filter(Product.is_active.is_(True))
        if certification is not None:
            query = query.filter(Product.certification == certification)
        return query.first()

    @staticmethod
    def update(db: Session, product: Product) -> Product:
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def delete(db: Session, product: Product) -> Product:
        product.is_active = False
        db.commit()
        db.refresh(product)
        return product
