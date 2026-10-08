from decimal import Decimal

from fastapi import HTTPException, Query, status
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.products import Product
from app.repositories.category_repository import CategoryRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.products import ProductCreate, ProductUpdate


class ProductService:
    LOW_STOCK_THRESHOLD = 10

    @staticmethod
    def create_product(db: Session, product_data: ProductCreate, seller_id: int) -> Product:
        category = CategoryRepository.get_by_id(db, product_data.category_id, include_inactive=False)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        product = Product(
            seller_id=seller_id,
            category_id=product_data.category_id,
            name=product_data.name,
            description=product_data.description,
            price=product_data.price,
            stock_quantity=product_data.stock_quantity,
            unit=product_data.unit,
            certification="PENDING",
            image_url=product_data.image_url,
            is_active=product_data.is_active,
        )

        return ProductRepository.create(db, product)

    @staticmethod
    def get_products(
        db: Session,
        *,
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
        customer_visible: bool = True,
    ) -> tuple[list[Product], int]:
        if min_price is not None and max_price is not None and min_price > max_price:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="min_price cannot be greater than max_price")
        if page < 1:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="page must be >= 1")
        if page_size < 1:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="page_size must be >= 1")
        if customer_visible:
            certification = "APPROVED"

        try:
            return ProductRepository.get_all(
                db,
                search=search,
                category_id=category_id,
                seller_id=seller_id,
                certification=certification,
                min_price=min_price,
                max_price=max_price,
                sort_by=sort_by,
                sort_order=sort_order,
                page=page,
                page_size=page_size,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    @staticmethod
    def get_product(db: Session, product_id: int, *, customer_visible: bool = True) -> Product:
        product = ProductRepository.get_by_id(
            db,
            product_id,
            include_inactive=not customer_visible,
            certification="APPROVED" if customer_visible else None,
        )
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product

    @staticmethod
    def get_low_stock_active_products(db: Session) -> list[Product]:
        return ProductRepository.get_low_stock_active(db, ProductService.LOW_STOCK_THRESHOLD)

    @staticmethod
    def update_product(db: Session, product_id: int, product_data: ProductUpdate) -> Product:
        product = ProductRepository.get_by_id(db, product_id, include_inactive=True)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        update_data = product_data.model_dump(exclude_unset=True)
        update_data.pop("seller_id", None)
        if "category_id" in update_data:
            category = CategoryRepository.get_by_id(db, update_data["category_id"], include_inactive=False)
            if category is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        update_data.pop("certification", None)

        for field, value in update_data.items():
            setattr(product, field, value)

        return ProductRepository.update(db, product)

    @staticmethod
    def approve_product(db: Session, product_id: int) -> Product:
        product = ProductRepository.get_by_id(db, product_id, include_inactive=True)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        if product.certification != "PENDING":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending products can be approved")
        product.certification = "APPROVED"
        return ProductRepository.update(db, product)

    @staticmethod
    def reject_product(db: Session, product_id: int) -> Product:
        product = ProductRepository.get_by_id(db, product_id, include_inactive=True)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        if product.certification != "PENDING":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending products can be rejected")
        product.certification = "REJECTED"
        return ProductRepository.update(db, product)

    @staticmethod
    def delete_product(db: Session, product_id: int) -> Product:
        product = ProductRepository.get_by_id(db, product_id, include_inactive=True)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return ProductRepository.delete(db, product)

    @staticmethod
    def get_categories(db: Session) -> list[Category]:
        return CategoryRepository.get_all(db)
