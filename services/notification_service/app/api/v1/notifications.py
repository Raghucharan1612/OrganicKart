from typing import Annotated

from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import customer_actor, notification_creator
from app.schemas.notification import NotificationCreate, NotificationResponse
from app.services.notification_service import NotificationService


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationResponse])
def list_notifications(
    actor: Annotated[dict, Depends(customer_actor)],
    db: Session = Depends(get_db),
):
    return NotificationService(db).list_for_user(actor["user_id"])


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: int,
    actor: Annotated[dict, Depends(customer_actor)],
    db: Session = Depends(get_db),
):
    return NotificationService(db).get_for_user(actor["user_id"], notification_id)


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: int,
    actor: Annotated[dict, Depends(customer_actor)],
    db: Session = Depends(get_db),
):
    return NotificationService(db).mark_read(actor["user_id"], notification_id)


@router.patch("/read-all")
def mark_all_notifications_read(
    actor: Annotated[dict, Depends(customer_actor)],
    db: Session = Depends(get_db),
):
    return {"updated": NotificationService(db).mark_all_read(actor["user_id"])}


@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(
    payload: NotificationCreate,
    actor: Annotated[dict, Depends(notification_creator)],
    db: Session = Depends(get_db),
    internal_service_key: Annotated[str | None, Header(alias="X-Internal-Service-Key")] = None,
):
    return NotificationService(db).create(payload)
