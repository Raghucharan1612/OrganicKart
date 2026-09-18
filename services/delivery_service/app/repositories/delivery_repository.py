from sqlalchemy.orm import Session

from app.models.delivery import Delivery


class DeliveryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, delivery: Delivery) -> Delivery:
        self.db.add(delivery)
        self.db.commit()
        self.db.refresh(delivery)
        return delivery

    def get_by_id(self, delivery_id: int) -> Delivery | None:
        return self.db.query(Delivery).filter(Delivery.id == delivery_id).first()

    def get_by_user(self, user_id: int) -> list[Delivery]:
        return self.db.query(Delivery).filter(Delivery.user_id == user_id).order_by(Delivery.created_at.desc()).all()

    def get_by_order_id(self, order_id: int) -> Delivery | None:
        return self.db.query(Delivery).filter(Delivery.order_id == order_id).first()

    def get_all(self) -> list[Delivery]:
        return self.db.query(Delivery).order_by(Delivery.created_at.desc()).all()

    def get_by_tracking_number(self, tracking_number: str) -> Delivery | None:
        return self.db.query(Delivery).filter(Delivery.tracking_number == tracking_number).first()

    def get_available_for_partner(self) -> list[Delivery]:
        return (
            self.db.query(Delivery)
            .filter(
                Delivery.assigned_partner_id.is_(None),
                Delivery.status.not_in(["CANCELLED", "FAILED"]),
            )
            .order_by(Delivery.created_at.desc())
            .all()
        )

    def get_assigned_to_partner(self, partner_id: int) -> list[Delivery]:
        return (
            self.db.query(Delivery)
            .filter(Delivery.assigned_partner_id == partner_id)
            .order_by(Delivery.created_at.desc())
            .all()
        )

    def atomic_accept(self, delivery_id: int, partner_id: int) -> Delivery | None:
        from datetime import UTC, datetime

        now = datetime.now(UTC)
        updated_count = (
            self.db.query(Delivery)
            .filter(
                Delivery.id == delivery_id,
                Delivery.assigned_partner_id.is_(None),
                Delivery.status.not_in(["CANCELLED", "FAILED"]),
            )
            .update(
                {
                    "assigned_partner_id": partner_id,
                    "accepted_at": now,
                    "status": "ACCEPTED",
                },
                synchronize_session=False,
            )
        )
        self.db.commit()
        if updated_count == 0:
            return None
        return self.get_by_id(delivery_id)

    def update(self, delivery: Delivery) -> Delivery:
        self.db.commit()
        self.db.refresh(delivery)
        return delivery

    def delete(self, delivery: Delivery) -> None:
        self.db.delete(delivery)
        self.db.commit()
