from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./catalog.db"
    SERVICE_NAME: str = "product-service"
    SERVICE_PORT: int = 8003
    JWT_SECRET_KEY: str = "replace-me-with-a-secure-secret"
    JWT_ALGORITHM: str = "HS256"
    
    UNSPLASH_ACCESS_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()