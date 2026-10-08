import logging
import httpx
from fastapi import HTTPException, status

from app.config import settings

logger = logging.getLogger(__name__)


class OllamaService:
    """
    Client for interacting with local Ollama API service running gpt-oss:20b model.
    """

    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL

    async def generate_response(self, prompt: str, system_prompt: str | None = None) -> str:
        """
        Sends prompt to local Ollama generate API and returns response text.
        """
        if settings.MOCK_LLM:
            return f"[MOCK AI RESPONSE] Based on OrganicKart knowledge: {prompt[:100]}"

        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt or "You are OrganicKart's AI assistant.",
            "stream": False,
            "options": {"num_predict": settings.OLLAMA_NUM_PREDICT},
        }

        try:
            async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT_SECONDS) as client:
                response = await client.post(url, json=payload)
        except httpx.ConnectError as exc:
            logger.warning("Ollama connection failed base_url=%s error=%s", self.base_url, exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"AI engine service is currently offline. Ensure Ollama is running at {self.base_url}.",
            ) from exc
        except httpx.TimeoutException as exc:
            logger.warning("Ollama request timed out model=%s", self.model)
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="AI service request timed out while generating response.",
            ) from exc
        except httpx.HTTPError as exc:
            logger.warning("Ollama HTTP transport error: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to communicate with local Ollama LLM provider.",
            ) from exc

        if response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Configured Ollama model '{self.model}' was not found. Please pull the model using: ollama pull {self.model}",
            )

        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Ollama provider returned error status {response.status_code}.",
            )

        try:
            data = response.json()
            answer = data.get("response", "").strip()
            if not answer:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="LLM engine returned an empty response.",
                )
            return answer
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Invalid JSON response received from LLM engine.",
            ) from exc
