from decimal import Decimal

import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.cart import Cart, CartItem
from app.repositories.cart_repository import CartRepository
from app.schemas.cart import CartItemCreate, CartItemUpdate


class CartService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CartRepository(db)

    def get_cart(self, user_id: int) -> Cart:
        cart = self.repo.get_by_user(user_id)
        if cart is None:
            cart = self.repo.get_or_create(user_id)
        return cart

    def add_item(self, user_id: int, payload: CartItemCreate) -> CartItem:
        cart = self.get_cart(user_id)
        product = self._validate_product(payload.product_id)
        item = self.repo.add_item(
            cart,
            product["id"],
            product["name"],
            Decimal(str(product["price"])),
            payload.quantity,
            image_url=product.get("image_url"),
            unit=product.get("unit"),
        )
        return item

    def update_item(self, user_id: int, item_id: int, payload: CartItemUpdate) -> CartItem:
        cart = self.get_cart(user_id)
        item = self.repo.update_item(cart, item_id, payload.quantity)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
        return item

    def remove_item(self, user_id: int, item_id: int) -> None:
        cart = self.get_cart(user_id)
        removed = self.repo.remove_item(cart, item_id)
        if not removed:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

    def clear_cart(self, user_id: int) -> None:
        cart = self.get_cart(user_id)
        self.repo.clear(cart)

    def _validate_product(self, product_id: int) -> dict:
        try:
            response = httpx.get(f"{settings.PRODUCT_SERVICE_URL}/api/v1/products/{product_id}", timeout=10)
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Product catalog unavailable") from exc

        if response.status_code == 404:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        if response.status_code != 200:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid product reference")

        product = response.json()
        if product.get("is_active") is not True:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product is unavailable for purchase")
        if product.get("certification") != "APPROVED":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product certification must be APPROVED before purchase")
        stock_quantity = product.get("stock_quantity", 0)
        if int(stock_quantity) <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product is out of stock")

        return product
