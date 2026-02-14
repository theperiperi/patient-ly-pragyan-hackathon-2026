"""Configuration for HIP Service using Pydantic Settings."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """HIP Service Configuration."""

    # Service Configuration
    service_name: str = "hip"
    port: int = 8092
    debug: bool = False
    log_level: str = "INFO"

    # MongoDB Configuration
    mongo_uri: str = "mongodb://admin:abdm123@localhost:27017/abdm?authSource=admin"

    # JWT Configuration
    jwt_secret: str = "abdm-local-dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24

    # Service URLs
    gateway_url: str = "http://localhost:8090"

    # HIP Specific Configuration
    facility_id: str = "Apollo-Hospitals-Bangalore"
    facility_name: str = "Apollo Hospitals Bangalore"

    # Optional Configuration
    cors_origins: list = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def mongo_db_name(self) -> str:
        """Extract database name from MongoDB URI."""
        return "abdm"


# Create global settings instance
settings = Settings()
