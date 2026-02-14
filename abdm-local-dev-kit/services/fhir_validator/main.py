import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pathlib import Path

from config import settings
from middleware.logging import LoggingMiddleware

# Import API router
from api import validate

# Import utilities
from utils.profile_loader import init_profile_loader

# Configure logging
logging.basicConfig(
    level=logging.getLevelName(settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.service_name,
    description="FHIR Resource Validator for ABDM Profiles - Validates FHIR resources against official ABDM IG v6.5.0",
    version=settings.service_version,
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Mount validation router
app.include_router(validate.router, prefix="", tags=["FHIR Validation"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    # Check if profile loader is initialized
    from utils.profile_loader import get_profile_loader
    profile_loader = get_profile_loader()

    profiles_status = "healthy" if profile_loader and profile_loader.is_loaded() else "unhealthy"
    profiles_count = profile_loader.get_profiles_count() if profile_loader else 0

    return {
        "status": "healthy" if profiles_status == "healthy" else "degraded",
        "service": settings.service_name,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "profiles": profiles_status
        },
        "info": {
            "profiles_loaded": profiles_count
        }
    }


@app.get("/")
async def root():
    """Root endpoint returning service information."""
    from utils.profile_loader import get_profile_loader
    profile_loader = get_profile_loader()
    profiles_count = profile_loader.get_profiles_count() if profile_loader else 0

    return {
        "service_name": settings.service_name,
        "service_version": settings.service_version,
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat(),
        "abdm_version": "IG v6.5.0",
        "profiles_loaded": profiles_count,
        "endpoints": {
            "health": "/health",
            "validate": "POST /validate",
            "profiles_list": "GET /profiles",
            "profile_details": "GET /profiles/{profile_name}",
            "validate_batch": "POST /validate-batch",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    }


@app.on_event("startup")
async def startup_event():
    """Event handler for application startup."""
    logger.info(f"Starting {settings.service_name} v{settings.service_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Server running on {settings.host}:{settings.port}")

    # Initialize profile loader
    profiles_dir = Path(settings.profiles_dir)
    logger.info(f"FHIR Profiles directory: {profiles_dir}")

    if not profiles_dir.exists():
        logger.error(f"Profiles directory does not exist: {profiles_dir}")
        logger.error("FHIR validation will not be available without profiles")
        return

    try:
        profile_loader = init_profile_loader(str(profiles_dir))
        profiles_count = profile_loader.get_profiles_count()
        logger.info(f"Successfully loaded {profiles_count} FHIR profiles")
    except Exception as e:
        logger.error(f"Failed to load FHIR profiles: {e}")
        logger.error("FHIR validation may not work correctly")


@app.on_event("shutdown")
async def shutdown_event():
    """Event handler for application shutdown."""
    logger.info(f"Shutting down {settings.service_name}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower()
    )
