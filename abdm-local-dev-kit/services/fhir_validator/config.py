from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuration settings for the FHIR Validator service."""

    # Service Configuration
    service_name: str = "FHIR Validator"
    service_version: str = "1.0.0"
    environment: str = "development"

    # Server Configuration
    port: int = 8094
    host: str = "0.0.0.0"
    debug: bool = False

    # CORS Configuration
    cors_origins: list = ["*"]
    cors_credentials: bool = True
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]

    # FHIR Configuration
    profiles_dir: Optional[str] = "/app/profiles/definitions"

    # Logging Configuration
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
