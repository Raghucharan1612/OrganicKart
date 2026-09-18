from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "OrganicKart API Gateway"
    APP_VERSION: str = "1.0.0"
    SERVICE_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    PRODUCT_SERVICE_URL: str = "http://localhost:8003"
    ORDER_SERVICE_URL: str = "http://localhost:8004"
    DELIVERY_SERVICE_URL: str = "http://localhost:8005"
    NOTIFICATION_SERVICE_URL: str = "http://localhost:8006"
    REQUEST_TIMEOUT_SECONDS: int = 15

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
