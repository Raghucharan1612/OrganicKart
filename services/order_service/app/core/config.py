from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ORDER_DATABASE_URL: str
    PRODUCT_SERVICE_URL: str = "http://localhost:8003"
    USER_SERVICE_URL: str = "http://localhost:8001"
    JWT_SECRET_KEY: str = "development-secret-key-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    SERVICE_PORT: int = 8004
    NOTIFICATION_SERVICE_URL: str = "http://localhost:8006"
    DELIVERY_SERVICE_URL: str = "http://localhost:8005"
    INTERNAL_SERVICE_KEY: str = "replace-me-with-an-internal-service-key"
    NOTIFICATION_REQUEST_TIMEOUT: float = 1.0
    RAZORPAY_KEY_ID: str | None = None
    RAZORPAY_KEY_SECRET: str | None = None
    RAZORPAY_WEBHOOK_SECRET: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
