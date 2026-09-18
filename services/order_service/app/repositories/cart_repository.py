from sqlalchemy.orm import Session

from app.models.cart import Cart, CartItem


class CartRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create(self, user_id: int) -> Cart:
        cart = self.db.query(Cart).filter(Cart.user_id == user_id, Cart.is_active.is_(True)).first()
        if cart is None:
            cart = Cart(user_id=user_id, is_active=True)
            self.db.add(cart)
            self.db.commit()
            self.db.refresh(cart)
        return cart

    def get_by_user(self, user_id: int) -> Cart | None:
        return self.db.query(Cart).filter(Cart.user_id == user_id, Cart.is_active.is_(True)).first()

    def add_item(self, cart: Cart, product_id: int, product_name: str, unit_price: float, quantity: int, image_url: str | None = None, unit: str | None = None) -> CartItem:
        item = self.db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.product_id == product_id).first()
        if item:
            item.quantity += quantity
            item.unit_price = unit_price
            item.product_name = product_name
            if image_url:
                item.image_url = image_url
            if unit:
                item.unit = unit
            self.db.commit()
            self.db.refresh(item)
            return item

        item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            product_name=product_name,
            unit_price=unit_price,
            quantity=quantity,
            image_url=image_url,
            unit=unit,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update_item(self, cart: Cart, item_id: int, quantity: int) -> CartItem | None:
        item = self.db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
        if item is None:
            return None
        item.quantity = quantity
        self.db.commit()
        self.db.refresh(item)
        return item

    def remove_item(self, cart: Cart, item_id: int) -> bool:
        item = self.db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
        if item is None:
            return False
        self.db.delete(item)
        self.db.commit()
        return True

    def clear(self, cart: Cart) -> None:
        self.db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        self.db.commit()
