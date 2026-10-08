from typing import Any

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials

from app.agents.admin_agent import AdminAgent
from app.core.security import require_admin, security
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()
admin_agent = AdminAgent()


@router.post("/admin/chat", response_model=ChatResponse, response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def chat_with_admin_assistant(
    payload: ChatRequest,
    _: dict[str, Any] = Depends(require_admin),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Any:
    """ADMIN-only read-only catalog/RAG endpoint."""
    return await admin_agent.handle_query(payload.message, token=credentials.credentials)
