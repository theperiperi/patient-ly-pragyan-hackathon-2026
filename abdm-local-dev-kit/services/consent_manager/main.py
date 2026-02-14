"""
Consent Manager Service - ABDM Local Development Kit

This service manages the patient consent lifecycle in the ABDM (Ayushman Bharat Digital Mission) ecosystem.
It handles consent creation, revocation, and querying according to ABDM specifications.

The Consent Manager:
- Manages patient consent for data access
- Validates consent requests from Health Information Users (HIUs)
- Tracks consent artifacts and permissions
- Integrates with the Gateway service for routing
- Stores consent records in MongoDB
"""

import logging
import logging.config
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import uvicorn

from config import settings
from middleware.logging import LoggingMiddleware
from middleware.auth import JWTAuthMiddleware
from dependencies import set_database

# Configure logging
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": settings.log_level,
            "class": "logging.StreamHandler",
            "formatter": "detailed",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": settings.log_level,
            "propagate": True,
        },
    },
}

logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="ABDM Consent Manager",
    description="Manages patient consent lifecycle in ABDM ecosystem",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Global variables for database connection
db_client: AsyncIOMotorClient = None
db: AsyncIOMotorDatabase = None


# ============================================================================
# Middleware Setup
# ============================================================================


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Add custom middleware (order matters - add these after CORS)
app.add_middleware(JWTAuthMiddleware, secret_key=settings.jwt_secret)
app.add_middleware(LoggingMiddleware)


# ============================================================================
# Include API Routers
# ============================================================================

from api import consent_requests, patient_actions

app.include_router(consent_requests.router)
app.include_router(patient_actions.router)


# ============================================================================
# Event Handlers
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """
    Initialize database connection on application startup.
    """
    global db_client, db

    logger.info(f"Starting {settings.service_name} service on port {settings.port}")

    try:
        # Create MongoDB client
        db_client = AsyncIOMotorClient(settings.mongo_uri)
        # Get database reference
        db = db_client[settings.mongo_db_name]

        # Set global database for dependencies
        set_database(db)

        # Test connection
        await db_client.admin.command("ping")
        logger.info("Successfully connected to MongoDB")

        # Create indexes for collections
        await _create_indexes()

    except Exception as exc:
        logger.error(f"Failed to connect to MongoDB: {str(exc)}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """
    Clean up resources on application shutdown.
    """
    global db_client

    logger.info(f"Shutting down {settings.service_name} service")

    if db_client:
        db_client.close()
        logger.info("MongoDB connection closed")


async def _create_indexes():
    """
    Create MongoDB indexes for optimal query performance.
    """
    try:
        # Create consent collection indexes
        consent_collection = db["consents"]
        await consent_collection.create_index("patient_id")
        await consent_collection.create_index("hiu_id")
        await consent_collection.create_index("status")
        await consent_collection.create_index("created_at")
        await consent_collection.create_index([("patient_id", 1), ("hiu_id", 1)])

        logger.info("Database indexes created successfully")
    except Exception as exc:
        logger.error(f"Failed to create indexes: {str(exc)}", exc_info=True)


# ============================================================================
# Health Check Endpoint
# ============================================================================


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring service status.

    Returns:
        dict: Service health status
    """
    try:
        # Check database connection
        if db_client:
            await db_client.admin.command("ping")
            db_status = "healthy"
        else:
            db_status = "disconnected"
    except Exception as exc:
        logger.warning(f"Database health check failed: {str(exc)}")
        db_status = "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "service": settings.service_name,
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status,
    }


# ============================================================================
# Service Information Endpoint
# ============================================================================


@app.get("/", tags=["Service"])
async def service_info():
    """
    Get service information.

    Returns:
        dict: Service metadata and configuration
    """
    return {
        "name": settings.service_name,
        "version": "1.0.0",
        "description": "ABDM Consent Manager - Manages patient consent lifecycle",
        "port": settings.port,
        "gateway_url": settings.gateway_url,
        "timestamp": datetime.utcnow().isoformat(),
    }


# ============================================================================
# Root Endpoint
# ============================================================================


@app.get("/v1", tags=["Service"])
async def api_root():
    """
    API root endpoint providing service information.

    Returns:
        dict: API version and available endpoints
    """
    return {
        "service": settings.service_name,
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "consent": "/v1/consent",
            "status": "/v1/consent/status",
        },
        "documentation": "/docs",
        "timestamp": datetime.utcnow().isoformat(),
    }


# ============================================================================
# Placeholder Routes for ABDM Consent Manager API
# ============================================================================


@app.post("/v1/consent", tags=["Consent Management"])
async def create_consent(request: Request):
    """
    Create a new patient consent record.

    This endpoint accepts a consent request from a Health Information User (HIU)
    and creates a consent artifact in the system.

    Args:
        request: The HTTP request containing consent details

    Returns:
        dict: Consent creation response with consent ID and status
    """
    try:
        body = await request.json()
        logger.info(f"Consent creation request received for HIU: {body.get('hiu_id')}")

        # Placeholder implementation
        return {
            "status": "created",
            "consent_id": "CONSENT-001",
            "patient_id": body.get("patient_id"),
            "hiu_id": body.get("hiu_id"),
            "created_at": datetime.utcnow().isoformat(),
        }
    except Exception as exc:
        logger.error(f"Error creating consent: {str(exc)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create consent",
        )


@app.get("/v1/consent/status/{consent_id}", tags=["Consent Management"])
async def get_consent_status(consent_id: str):
    """
    Get the status of a consent request.

    Args:
        consent_id: The unique identifier of the consent

    Returns:
        dict: Consent status and details
    """
    try:
        logger.info(f"Status check for consent: {consent_id}")

        # Placeholder implementation
        return {
            "consent_id": consent_id,
            "status": "active",
            "patient_id": "PATIENT-001",
            "hiu_id": "HIU-001",
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": "2025-12-31T23:59:59Z",
        }
    except Exception as exc:
        logger.error(f"Error retrieving consent status: {str(exc)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consent not found",
        )


@app.delete("/v1/consent/{consent_id}", tags=["Consent Management"])
async def revoke_consent(consent_id: str):
    """
    Revoke a patient consent.

    Args:
        consent_id: The unique identifier of the consent to revoke

    Returns:
        dict: Revocation confirmation
    """
    try:
        logger.info(f"Consent revocation request for: {consent_id}")

        # Placeholder implementation
        return {
            "consent_id": consent_id,
            "status": "revoked",
            "revoked_at": datetime.utcnow().isoformat(),
            "message": "Consent has been revoked successfully",
        }
    except Exception as exc:
        logger.error(f"Error revoking consent: {str(exc)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to revoke consent",
        )


# ============================================================================
# Error Handlers
# ============================================================================


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom HTTP exception handler.

    Args:
        request: The HTTP request
        exc: The HTTP exception

    Returns:
        JSONResponse: Error response
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    General exception handler for unhandled errors.

    Args:
        request: The HTTP request
        exc: The exception

    Returns:
        JSONResponse: Error response
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


# ============================================================================
# Main Entry Point
# ============================================================================


if __name__ == "__main__":
    logger.info(
        f"Starting {settings.service_name} on {settings.host}:{settings.port}"
    )
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )
