from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuration settings for the HIU (Health Information User) service."""

    # Service Configuration
    service_name: str = "ABDM HIU"
    service_version: str = "1.0.0"
    environment: str = "development"

    # Server Configuration
    port: int = 8093
    host: str = "0.0.0.0"
    debug: bool = False

    # Database Configuration
    mongo_uri: str = "mongodb://localhost:27017/abdm"
    mongodb_database: str = "abdm_hiu"

    # JWT Configuration
    jwt_secret: str = "abdm-local-dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS Configuration
    cors_origins: list = ["*"]
    cors_credentials: bool = True
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]

    # HIU Configuration
    hiu_id: str = "Triage-AI-System"
    hiu_name: str = "AI-Powered Triage System"

    # Service URLs
    gateway_url: str = "http://gateway:8090"
    consent_manager_url: Optional[str] = "http://consent-manager:8091"
    hip_registry_url: Optional[str] = "http://hip:8092"

    # Logging Configuration
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
