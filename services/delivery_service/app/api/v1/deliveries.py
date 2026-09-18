from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_access_token
from app.database.session import get_db
from app.schemas.delivery import DeliveryCreate, DeliveryResponse, DeliveryStatusUpdate, DeliveryUpdate
from app.services.delivery_service import DeliveryService

router = APIRouter(prefix="/deliveries", tags=["deliveries"])
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(credentials.credentials)
    if payload is None or "sub" not in payload:
        raise credentials_error

    return {"user_id": int(payload["sub"]), "role": payload.get("role", "CUSTOMER")}


def require_roles(*allowed_roles: str):
    def dependency(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return current_user

    return dependency


@router.get("/partner/available", response_model=list[DeliveryResponse])
def get_available_deliveries(
    db: Session = Depends(get_db),
    partner_user: dict = Depends(require_roles("DELIVERY_PARTNER")),
):
    return [
        DeliveryResponse.model_validate(delivery)
        for delivery in DeliveryService(db).list_available_for_partner()
    ]


@router.get("/partner/assigned", response_model=list[DeliveryResponse])
def get_assigned_deliveries(
    db: Session = Depends(get_db),
    partner_user: dict = Depends(require_roles("DELIVERY_PARTNER")),
):
    return [
        DeliveryResponse.model_validate(delivery)
        for delivery in DeliveryService(db).list_assigned_to_partner(partner_user["user_id"])
    ]


@router.post("/{delivery_id}/accept", response_model=DeliveryResponse)
def accept_delivery(
    delivery_id: int,
    db: Session = Depends(get_db),
    partner_user: dict = Depends(require_roles("DELIVERY_PARTNER")),
):
    delivery = DeliveryService(db).accept_delivery(delivery_id, partner_user["user_id"])
    return DeliveryResponse.model_validate(delivery)


@router.get("", response_model=list[DeliveryResponse])
def list_deliveries(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    role = current_user.get("role")
    if role in {"ADMIN", "SUPER_ADMIN"}:
        deliveries = DeliveryService(db).list_all()
    elif role == "DELIVERY_PARTNER":
        deliveries = DeliveryService(db).list_assigned_to_partner(user_id)
    else:
        deliveries = DeliveryService(db).list_for_user(user_id)
    return [DeliveryResponse.model_validate(delivery) for delivery in deliveries]


@router.get("/{delivery_id}", response_model=DeliveryResponse)
def get_delivery(delivery_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return DeliveryResponse.model_validate(
        DeliveryService(db).get_for_user(current_user["user_id"], delivery_id)
    )


from pydantic import BaseModel

class InternalDeliveryAssign(BaseModel):
    order_id: int
    user_id: int
    shipping_address: str | None = None


@router.post("/internal/assign", response_model=DeliveryResponse, status_code=status.HTTP_201_CREATED)
def create_internal_delivery(
    payload: InternalDeliveryAssign,
    db: Session = Depends(get_db),
    internal_service_key: str | None = Header(default=None, alias="X-Internal-Service-Key"),
):
    if internal_service_key != settings.INTERNAL_SERVICE_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid internal service credentials")
    delivery = DeliveryService(db).create_delivery_for_order(
        user_id=payload.user_id,
        order_id=payload.order_id,
        shipping_address=payload.shipping_address,
    )
    return DeliveryResponse.model_validate(delivery)


@router.post("", response_model=DeliveryResponse, status_code=status.HTTP_201_CREATED)
def create_delivery(payload: DeliveryCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    delivery = DeliveryService(db).create_delivery(current_user["user_id"], payload)
    return DeliveryResponse.model_validate(delivery)


@router.put("/{delivery_id}", response_model=DeliveryResponse)
def update_delivery(delivery_id: int, payload: DeliveryUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    delivery = DeliveryService(db).update_delivery(current_user["user_id"], delivery_id, payload)
    return DeliveryResponse.model_validate(delivery)


@router.patch("/{delivery_id}/status", response_model=DeliveryResponse)
def update_status(delivery_id: int, payload: DeliveryStatusUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    delivery = DeliveryService(db).update_status(
        user_id=current_user["user_id"],
        delivery_id=delivery_id,
        payload=payload,
        role=current_user.get("role", "CUSTOMER"),
    )
    return DeliveryResponse.model_validate(delivery)
