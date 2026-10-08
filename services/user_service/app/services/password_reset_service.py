from datetime import UTC, datetime, timedelta
from email.message import EmailMessage
from hashlib import sha256
from secrets import token_urlsafe
from smtplib import SMTP, SMTPException
from ssl import create_default_context
from urllib.parse import quote

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User


class PasswordResetService:
    def __init__(self, db: Session):
        self.db = db

    def request_reset(self, email: str) -> str | None:
        is_development = settings.APP_ENV.lower() == "development"
        if not is_development and (not settings.SMTP_HOST or not settings.SMTP_FROM_EMAIL):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Password recovery is not configured. Contact support.",
            )

        user = self.db.query(User).filter(User.email == email).first()
        if user is None:
            return None

        now = datetime.now(UTC).replace(tzinfo=None)
        raw_token = token_urlsafe(32)
        token_record = PasswordResetToken(
            user_id=user.id,
            token_hash=sha256(raw_token.encode()).hexdigest(),
            expires_at=now + timedelta(minutes=30),
        )
        self.db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
        ).update({PasswordResetToken.used_at: now}, synchronize_session=False)
        self.db.add(token_record)
        self.db.commit()

        if is_development:
            return raw_token

        reset_url = f"{settings.FRONTEND_BASE_URL.rstrip('/')}/reset-password?token={quote(raw_token)}"
        message = EmailMessage()
        message["Subject"] = "Reset your OrganicKart password"
        message["From"] = settings.SMTP_FROM_EMAIL
        message["To"] = user.email
        message.set_content(
            "We received a request to reset your OrganicKart password. "
            f"Use this link within 30 minutes: {reset_url}\n\n"
            "If you did not request a reset, you can ignore this email."
        )

        try:
            with SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                if settings.SMTP_USE_TLS:
                    server.starttls(context=create_default_context())
                if settings.SMTP_USERNAME:
                    server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(message)
        except (OSError, SMTPException) as error:
            token_record.used_at = now
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Could not send the password reset email. Please try again later.",
            ) from error

        return None

    def reset_password(self, raw_token: str, new_password: str) -> None:
        now = datetime.now(UTC).replace(tzinfo=None)
        token_hash = sha256(raw_token.encode()).hexdigest()
        token_record = (
            self.db.query(PasswordResetToken)
            .filter(
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.expires_at > now,
            )
            .first()
        )
        if token_record is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This password reset link is invalid or expired.")

        user = self.db.query(User).filter(User.id == token_record.user_id).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This password reset link is invalid or expired.")

        user.password_hash = hash_password(new_password)
        self.db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
        ).update({PasswordResetToken.used_at: now}, synchronize_session=False)
        self.db.commit()