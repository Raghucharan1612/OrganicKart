from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SERVICE_NAME: str = "ai-service"
    SERVICE_PORT: int = 8002
    API_V1_PREFIX: str = "/api/v1"

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gpt-oss:20b"
    OLLAMA_TIMEOUT_SECONDS: int = 300
    OLLAMA_NUM_PREDICT: int = 250
    MOCK_LLM: bool = False

    ORDER_SERVICE_URL: str = "http://localhost:8004"
    ORDER_SERVICE_TIMEOUT_SECONDS: float = 10.0

    PRODUCT_SERVICE_URL: str = "http://localhost:8003"
    PRODUCT_SERVICE_TIMEOUT_SECONDS: float = 10.0

    DELIVERY_SERVICE_URL: str = "http://localhost:8005"
    DELIVERY_SERVICE_TIMEOUT_SECONDS: float = 10.0

    NOTIFICATION_SERVICE_URL: str = "http://localhost:8006"
    NOTIFICATION_SERVICE_TIMEOUT_SECONDS: float = 10.0

    WEB_SEARCH_ENABLED: bool = False
    WEB_SEARCH_PROVIDER: str = "brave"
    WEB_SEARCH_API_KEY: str = ""
    WEB_SEARCH_TIMEOUT_SECONDS: float = 5.0
    WEB_SEARCH_MAX_RESULTS: int = 3
    WEB_SEARCH_BRAVE_URL: str = "https://api.search.brave.com/res/v1/web/search"

    RAG_TOP_K: int = 3
    RAG_MAX_CONTEXT_CHARS: int = 6000

    JWT_SECRET_KEY: str = "replace-me-with-a-secure-secret"
    JWT_ALGORITHM: str = "HS256"

    KNOWLEDGE_BASE_DIR: str = str(Path(__file__).resolve().parent.parent / "knowledge_base")
    VECTOR_STORE_PATH: str = str(Path(__file__).resolve().parent.parent / "vector_store.json")
    ADMIN_KNOWLEDGE_BASE_DIR: str = str(Path(__file__).resolve().parent.parent / "knowledge_base" / "admin")
    ADMIN_VECTOR_STORE_PATH: str = str(Path(__file__).resolve().parent.parent / "admin_vector_store.json")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
