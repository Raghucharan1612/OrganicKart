from typing import Any
import logging

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials

from app.agents.customer_agent import CustomerAgent
from app.core.security import require_customer, security
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()
customer_agent = CustomerAgent()
logger = logging.getLogger(__name__)


@router.post("/chat", response_model=ChatResponse, response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def chat_with_customer_assistant(
    payload: ChatRequest,
    current_actor: dict[str, Any] = Depends(require_customer),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Any:
    """
    Customer AI Assistant endpoint.
    Requires authenticated CUSTOMER role via JWT.
    """
    user_id = current_actor["user_id"]
    token = credentials.credentials
    logger.warning(
        "AI_CHAT_TRACE step=authenticated user_id=%s authorization_present=%s",
        user_id,
        bool(token),
    )
    try:
        response = await customer_agent.handle_query(
            query=payload.message,
            user_id=user_id,
            token=token,
        )
        logger.warning("AI_CHAT_TRACE step=response user_id=%s status=200", user_id)
        return response
    except Exception:
        # Keep FastAPI's existing 500 behavior while recording the actual
        # exception. Tokens and request bodies are intentionally not logged.
        logger.exception("AI_CHAT_TRACE step=unhandled_exception user_id=%s", user_id)
        raise
