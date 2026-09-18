from fastapi import HTTPException, status
import httpx
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.core.config import settings
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def register(self, payload: RegisterRequest) -> User:
        if self.users.get_by_email(payload.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists.",
            )

        user = User(
            full_name=payload.full_name,
            email=str(payload.email),
            password_hash=hash_password(payload.password),
            phone=payload.phone,
            role=payload.role,
        )
        user = self.users.create(user)
        try:
            httpx.post(
                f"{settings.NOTIFICATION_SERVICE_URL}/api/v1/notifications",
                json={
                    "user_id": user.id,
                    "type": "WELCOME",
                    "title": "Welcome to OrganicKart",
                    "message": "Your OrganicKart account is ready.",
                    "channel": "IN_APP",
                    "reference_type": "USER",
                    "reference_id": user.id,
                },
                headers={"X-Internal-Service-Key": settings.INTERNAL_SERVICE_KEY},
                timeout=settings.NOTIFICATION_REQUEST_TIMEOUT,
            )
        except httpx.HTTPError:
            pass
        return user

    def authenticate(self, payload: LoginRequest) -> User:
        user = self.users.get_by_email(str(payload.email))
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated. Contact support.",
            )
        return user

    @staticmethod
    def issue_token(user: User) -> str:
        return create_access_token(
            subject=str(user.id),
            extra_claims={"role": user.role.value, "email": user.email},
        )
