from __future__ import annotations

from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import settings

security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None


def get_current_actor(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict[str, Any]:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None or not credentials.credentials:
        raise credentials_error

    payload = decode_access_token(credentials.credentials)
    if payload is None or "sub" not in payload:
        raise credentials_error

    role = payload.get("role", "CUSTOMER")
    return {"user_id": int(payload["sub"]), "role": str(role)}


def require_roles(*allowed_roles: str):
    allowed = set(allowed_roles)

    def dependency(current_actor: dict[str, Any] = Depends(get_current_actor)) -> dict[str, Any]:
        if current_actor.get("role") not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return current_actor

    return dependency


require_customer = require_roles("CUSTOMER")
require_vendor_or_farmer = require_roles("VENDOR", "FARMER")
require_admin = require_roles("ADMIN")
