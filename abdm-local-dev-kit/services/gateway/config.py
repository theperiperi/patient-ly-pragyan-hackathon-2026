from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuration settings for the Gateway service."""

    # Service Configuration
    service_name: str = "ABDM Gateway"
    service_version: str = "1.0.0"
    environment: str = "development"

    # Server Configuration
    port: int = 8090
    host: str = "0.0.0.0"
    debug: bool = False

    # Database Configuration
    mongo_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "abdm"

    # JWT Configuration
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS Configuration
    cors_origins: list = ["*"]
    cors_credentials: bool = True
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]

    # Service URLs
    hip_service_url: Optional[str] = "http://hip:8091"
    hiu_service_url: Optional[str] = "http://hiu:8092"
    consent_manager_url: Optional[str] = "http://consent-manager:8093"

    # Logging Configuration
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
