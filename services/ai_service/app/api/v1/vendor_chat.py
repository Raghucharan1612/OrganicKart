import logging
from typing import Any

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials

from app.agents.vendor_agent import VendorAgent
from app.core.security import require_vendor_or_farmer, security
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()
vendor_agent = VendorAgent()
logger = logging.getLogger(__name__)


@router.post("/vendor/chat", response_model=ChatResponse, response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def chat_with_vendor_assistant(
    payload: ChatRequest,
    current_actor: dict[str, Any] = Depends(require_vendor_or_farmer),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Any:
    """
    Vendor / Farmer AI Assistant endpoint.
    Requires authenticated VENDOR or FARMER role via JWT.
    """
    user_id = current_actor["user_id"]
    token = credentials.credentials
    logger.warning(
        "AI_VENDOR_CHAT_TRACE step=authenticated user_id=%s role=%s authorization_present=%s",
        user_id,
        current_actor.get("role"),
        bool(token),
    )
    try:
        response = await vendor_agent.handle_query(
            query=payload.message,
            user_id=user_id,
            token=token,
        )
        logger.warning("AI_VENDOR_CHAT_TRACE step=response user_id=%s status=200", user_id)
        return response
    except Exception:
        logger.exception("AI_VENDOR_CHAT_TRACE step=unhandled_exception user_id=%s", user_id)
        raise
