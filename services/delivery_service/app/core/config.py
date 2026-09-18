from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DELIVERY_DATABASE_URL: str
    ORDER_SERVICE_URL: str = "http://localhost:8004"
    JWT_SECRET_KEY: str = "development-secret-key-change-me"
    JWT_ALGORITHM: str = "HS256"
    SERVICE_REQUEST_TIMEOUT: float = 10.0
    SERVICE_PORT: int = 8005
    NOTIFICATION_SERVICE_URL: str = "http://localhost:8006"
    INTERNAL_SERVICE_KEY: str = "replace-me-with-an-internal-service-key"
    NOTIFICATION_REQUEST_TIMEOUT: float = 1.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
