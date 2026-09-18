from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, order: Order) -> Order:
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def add_item(self, order: Order, product_id: int, product_name: str, unit_price: Decimal, quantity: int, subtotal: Decimal) -> OrderItem:
        item = OrderItem(
            order_id=order.id,
            product_id=product_id,
            product_name=product_name,
            unit_price=unit_price,
            quantity=quantity,
            subtotal=subtotal,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get_by_id(self, order_id: int) -> Order | None:
        return self.db.query(Order).filter(Order.id == order_id).first()

    def get_by_user(self, user_id: int) -> list[Order]:
        return self.db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).all()

    def cancel(self, order: Order) -> Order:
        order.status = "CANCELLED"
        self.db.commit()
        self.db.refresh(order)
        return order
