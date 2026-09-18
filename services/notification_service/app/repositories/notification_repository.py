from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.notification import Notification, NotificationStatus, NotificationType


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_for_user(self, user_id: int) -> list[Notification]:
        return list(
            self.db.scalars(
                select(Notification)
                .where(Notification.user_id == user_id)
                .order_by(Notification.created_at.desc())
            )
        )

    def get_for_user(self, user_id: int, notification_id: int) -> Notification | None:
        return self.db.scalar(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
        )

    def get_event(self, user_id: int, notification_type: NotificationType, reference_type: str | None, reference_id: int | None) -> Notification | None:
        return self.db.scalar(
            select(Notification).where(
                Notification.user_id == user_id,
                Notification.type == notification_type,
                Notification.reference_type == reference_type,
                Notification.reference_id == reference_id,
            )
        )

    def create(self, notification: Notification) -> Notification:
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def mark_read(self, notification: Notification) -> Notification:
        notification.status = NotificationStatus.READ
        notification.read_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def mark_all_read(self, user_id: int) -> int:
        result = self.db.execute(
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.status.in_([NotificationStatus.PENDING, NotificationStatus.SENT]),
            )
            .values(status=NotificationStatus.READ, read_at=datetime.now(UTC))
        )
        self.db.commit()
        return result.rowcount
