from app.services.ollama_service import OllamaService


class LLMService:
    """
    Abstraction layer for LLM generation. Uses OllamaService locally.
    """

    def __init__(self, ollama_service: OllamaService | None = None):
        self.ollama_service = ollama_service or OllamaService()

    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        return await self.ollama_service.generate_response(prompt, system_prompt=system_prompt)
