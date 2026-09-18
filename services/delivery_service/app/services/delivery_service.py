import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.delivery import Delivery
from app.repositories.delivery_repository import DeliveryRepository
from app.schemas.delivery import DeliveryCreate, DeliveryStatusUpdate, DeliveryUpdate

VALID_STATUS_FLOW = {
    "PENDING": {"CONFIRMED", "ACCEPTED", "ASSIGNED"},
    "CONFIRMED": {"ACCEPTED", "ASSIGNED", "PICKED_UP"},
    "ACCEPTED": {"PICKED_UP"},
    "ASSIGNED": {"PICKED_UP"},
    "PICKED_UP": {"IN_TRANSIT", "OUT_FOR_DELIVERY"},
    "IN_TRANSIT": {"OUT_FOR_DELIVERY"},
    "OUT_FOR_DELIVERY": {"DELIVERED"},
    "DELIVERED": set(),
    "FAILED": set(),
    "CANCELLED": set(),
}


class DeliveryService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = DeliveryRepository(db)

    def list_for_user(self, user_id: int) -> list[Delivery]:
        return self.repo.get_by_user(user_id)

    def get_for_user(self, user_id: int, delivery_id: int) -> Delivery:
        delivery = self.repo.get_by_id(delivery_id)
        if delivery is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")
        if delivery.user_id != user_id and delivery.assigned_partner_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")
        return delivery

    def list_all(self) -> list[Delivery]:
        return self.repo.get_all()

    def list_available_for_partner(self) -> list[Delivery]:
        return self.repo.get_available_for_partner()

    def list_assigned_to_partner(self, partner_id: int) -> list[Delivery]:
        return self.repo.get_assigned_to_partner(partner_id)

    def accept_delivery(self, delivery_id: int, partner_id: int) -> Delivery:
        delivery = self.repo.get_by_id(delivery_id)
        if delivery is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")
        if delivery.assigned_partner_id is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Delivery has already been assigned to another partner",
            )
        if delivery.status in {"CANCELLED", "FAILED"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Delivery cannot be accepted in its current state",
            )

        updated = self.repo.atomic_accept(delivery_id, partner_id)
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Delivery has already been assigned to another partner",
            )
        return updated

    def create_delivery(self, user_id: int, payload: DeliveryCreate) -> Delivery:
        self._validate_order_exists(payload.order_id, user_id)
        if self.repo.get_by_tracking_number(self._generate_tracking_number()) is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tracking number already exists")

        tracking_number = self._generate_tracking_number()
        estimated_delivery = datetime.now(UTC) + timedelta(days=3)
        delivery = Delivery(
            order_id=payload.order_id,
            user_id=user_id,
            tracking_number=tracking_number,
            status="PENDING",
            recipient_name=payload.address.recipient_name,
            recipient_phone=payload.address.recipient_phone,
            address_line1=payload.address.address_line1,
            address_line2=payload.address.address_line2,
            city=payload.address.city,
            state=payload.address.state,
            postal_code=payload.address.postal_code,
            country=payload.address.country,
            estimated_delivery_date=estimated_delivery,
        )
        return self.repo.create(delivery)

    def create_delivery_for_order(self, user_id: int, order_id: int, shipping_address: str | None = None) -> Delivery:
        existing = self.repo.get_by_order_id(order_id)
        if existing:
            return existing

        tracking_number = self._generate_tracking_number()
        while self.repo.get_by_tracking_number(tracking_number) is not None:
            tracking_number = self._generate_tracking_number()

        estimated_delivery = datetime.now(UTC) + timedelta(days=1)
        addr_line = (shipping_address or "Customer Shipping Address").strip()

        delivery = Delivery(
            order_id=order_id,
            user_id=user_id,
            tracking_number=tracking_number,
            status="PENDING",
            recipient_name=f"Customer #{user_id}",
            recipient_phone=None,
            address_line1=addr_line[:250],
            address_line2=None,
            city="Bengaluru",
            state="Karnataka",
            postal_code="560001",
            country="India",
            estimated_delivery_date=estimated_delivery,
        )
        return self.repo.create(delivery)

    def update_delivery(self, user_id: int, delivery_id: int, payload: DeliveryUpdate) -> Delivery:
        delivery = self.get_for_user(user_id, delivery_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(delivery, field, value)
        return self.repo.update(delivery)

    def update_status(
        self,
        user_id: int,
        delivery_id: int,
        payload: DeliveryStatusUpdate,
        role: str = "CUSTOMER",
    ) -> Delivery:
        delivery = self.repo.get_by_id(delivery_id)
        if delivery is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")

        if role == "DELIVERY_PARTNER":
            if delivery.assigned_partner_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only update deliveries assigned to you.",
                )
        elif role in {"ADMIN", "SUPER_ADMIN"}:
            pass
        elif delivery.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")

        self._validate_status_transition(delivery.status, payload.status)
        delivery.status = payload.status
        if payload.status == "DELIVERED":
            delivery.delivered_at = datetime.now(UTC)
        if payload.status in {"PICKED_UP", "IN_TRANSIT", "OUT_FOR_DELIVERY"} and delivery.shipped_at is None:
            delivery.shipped_at = datetime.now(UTC)
        delivery = self.repo.update(delivery)
        notification_type = {
            "CONFIRMED": "DELIVERY_CONFIRMED",
            "ACCEPTED": "DELIVERY_CONFIRMED",
            "ASSIGNED": "DELIVERY_CONFIRMED",
            "PICKED_UP": "DELIVERY_SHIPPED",
            "IN_TRANSIT": "DELIVERY_SHIPPED",
            "OUT_FOR_DELIVERY": "OUT_FOR_DELIVERY",
            "DELIVERED": "DELIVERED",
        }.get(payload.status)
        if notification_type:
            try:
                httpx.post(
                    f"{settings.NOTIFICATION_SERVICE_URL}/api/v1/notifications",
                    json={
                        "user_id": delivery.user_id,
                        "type": notification_type,
                        "title": f"Delivery #{delivery.id}: {payload.status}",
                        "message": f"Your delivery status is now {payload.status}.",
                        "channel": "IN_APP",
                        "reference_type": "DELIVERY",
                        "reference_id": delivery.id,
                    },
                    headers={"X-Internal-Service-Key": settings.INTERNAL_SERVICE_KEY},
                    timeout=settings.NOTIFICATION_REQUEST_TIMEOUT,
                )
            except httpx.HTTPError:
                pass
        return delivery

    def _validate_order_exists(self, order_id: int, user_id: int) -> None:
        try:
            response = httpx.get(
                f"{settings.ORDER_SERVICE_URL}/api/v1/orders/{order_id}",
                timeout=settings.SERVICE_REQUEST_TIMEOUT,
            )
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Order service unavailable") from exc

        if response.status_code == 404:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        if response.status_code != 200:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid order reference")

        order = response.json()
        if int(order.get("user_id")) != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Order does not belong to this user")

    def _validate_status_transition(self, current: str, next_status: str) -> None:
        allowed = VALID_STATUS_FLOW.get(current, set())
        if next_status not in allowed:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status transition from {current} to {next_status}")

    def _generate_tracking_number(self) -> str:
        return f"OK-{uuid.uuid4().hex[:12].upper()}"
