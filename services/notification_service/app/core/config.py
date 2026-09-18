from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    NOTIFICATION_DATABASE_URL: str
    USER_SERVICE_URL: str = "http://localhost:8001"
    ORDER_SERVICE_URL: str = "http://localhost:8004"
    DELIVERY_SERVICE_URL: str = "http://localhost:8005"
    SERVICE_REQUEST_TIMEOUT: float = 10.0
    INTERNAL_SERVICE_KEY: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    SERVICE_PORT: int = 8006

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
