"""
Configuration module for Consent Manager service.
Uses Pydantic Settings for environment variable management.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # Service Configuration
    service_name: str = "consent-manager"
    port: int = 8091
    host: str = "0.0.0.0"
    log_level: str = "INFO"
    debug: bool = False

    # MongoDB Configuration
    mongo_uri: str = "mongodb://admin:abdm123@localhost:27017/abdm?authSource=admin"
    mongo_db_name: str = "abdm"

    # JWT Authentication
    jwt_secret: str = "abdm-local-dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24

    # Gateway Configuration
    gateway_url: str = "http://localhost:8090"

    # CORS Configuration
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8090",
        "http://localhost:8091",
        "http://localhost:8092",
        "http://localhost:8093",
        "http://localhost:8094",
        "*",
    ]
    cors_credentials: bool = True
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False

        # Map environment variable names
        fields = {
            "mongo_uri": {"env": "MONGO_URI"},
            "mongo_db_name": {"env": "MONGO_DB_NAME"},
            "jwt_secret": {"env": "JWT_SECRET"},
            "jwt_algorithm": {"env": "JWT_ALGORITHM"},
            "jwt_expiry_hours": {"env": "JWT_EXPIRY_HOURS"},
            "log_level": {"env": "LOG_LEVEL"},
            "gateway_url": {"env": "GATEWAY_URL"},
            "service_name": {"env": "SERVICE_NAME"},
            "port": {"env": "PORT"},
            "host": {"env": "HOST"},
            "debug": {"env": "DEBUG"},
        }


# Create settings instance
settings = Settings()
