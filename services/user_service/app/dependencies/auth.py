from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database.session import get_db
from app.models.roles import RoleEnum
from app.models.user import User
from app.repositories.user_repository import UserRepository

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(credentials.credentials)
    if payload is None or "sub" not in payload:
        raise credentials_error

    user = UserRepository(db).get_by_id(int(payload["sub"]))
    if user is None:
        raise credentials_error
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated. Contact support.",
        )
    return user


def require_roles(*allowed_roles: RoleEnum):
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return current_user

    return dependency


require_admin = require_roles(RoleEnum.ADMIN, RoleEnum.SUPER_ADMIN)
require_super_admin = require_roles(RoleEnum.SUPER_ADMIN)
require_customer = require_roles(RoleEnum.CUSTOMER)
