from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "OrganicKart Auth Service"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    SERVICE_PORT: int = 8001
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    AUTH_DATABASE_URL: str
    JWT_SECRET_KEY: str = "development-secret-key-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    NOTIFICATION_SERVICE_URL: str = "http://localhost:8006"
    INTERNAL_SERVICE_KEY: str = "replace-me-with-an-internal-service-key"
    NOTIFICATION_REQUEST_TIMEOUT: float = 1.0

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
