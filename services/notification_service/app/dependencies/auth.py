from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.core.security import decode_access_token

security = HTTPBearer(auto_error=False)


def current_actor(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    internal_key: Annotated[str | None, Header(alias="X-Internal-Service-Key")] = None,
) -> dict:
    if internal_key and internal_key == settings.INTERNAL_SERVICE_KEY:
        return {"internal": True, "role": "INTERNAL"}
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(credentials.credentials)
    if payload and "sub" in payload:
        return {"user_id": int(payload["sub"]), "role": payload.get("role", "CUSTOMER")}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def customer_actor(actor: Annotated[dict, Depends(current_actor)]) -> dict:
    if actor.get("internal"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Customer authentication required")
    return actor


def notification_creator(actor: Annotated[dict, Depends(current_actor)]) -> dict:
    if actor.get("internal") or actor.get("role") in {"ADMIN", "SUPER_ADMIN"}:
        return actor
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator permission required")
