from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.notification import Notification, NotificationChannel, NotificationStatus
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import NotificationCreate
from app.services.email_sender import EmailSender, MockEmailSender


class NotificationService:
    def __init__(self, db: Session, email_sender: EmailSender | None = None):
        self.repo = NotificationRepository(db)
        self.email_sender = email_sender or MockEmailSender()

    def create(self, payload: NotificationCreate) -> Notification:
        existing = self.repo.get_event(
            payload.user_id, payload.type, payload.reference_type, payload.reference_id
        )
        if existing:
            return existing

        notification = Notification(**payload.model_dump())
        if payload.channel == NotificationChannel.EMAIL:
            sent = self.email_sender.send(payload.user_id, payload.title, payload.message)
            notification.status = NotificationStatus.SENT if sent else NotificationStatus.FAILED
            notification.sent_at = datetime.now(UTC) if sent else None
        try:
            return self.repo.create(notification)
        except IntegrityError as exc:
            self.repo.db.rollback()
            existing = self.repo.get_event(
                payload.user_id, payload.type, payload.reference_type, payload.reference_id
            )
            if existing:
                return existing
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate notification event") from exc

    def list_for_user(self, user_id: int) -> list[Notification]:
        return self.repo.list_for_user(user_id)

    def get_for_user(self, user_id: int, notification_id: int) -> Notification:
        notification = self.repo.get_for_user(user_id, notification_id)
        if notification is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
        return notification

    def mark_read(self, user_id: int, notification_id: int) -> Notification:
        return self.repo.mark_read(self.get_for_user(user_id, notification_id))

    def mark_all_read(self, user_id: int) -> int:
        return self.repo.mark_all_read(user_id)
