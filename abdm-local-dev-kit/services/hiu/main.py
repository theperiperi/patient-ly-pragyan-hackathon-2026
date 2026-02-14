import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import uvicorn

from config import settings
from middleware.logging import LoggingMiddleware
import database

# Import API routers
from api import consent_management, data_collection, records_query

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)

# Database is managed by database module


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifespan events (startup and shutdown).

    Connects to MongoDB on startup and closes connection on shutdown.
    """
    # Startup
    logger.info("Starting HIU service...")
    try:
        client = AsyncIOMotorClient(settings.mongo_uri)
        db = client.get_database()
        database.set_database(db)
        # Verify connection
        await client.admin.command("ping")
        logger.info("Successfully connected to MongoDB")

        # Create indexes for HIU collections
        await db.consent_requests.create_index("requestId", unique=True)
        await db.consent_requests.create_index("consentRequestId")
        await db.consent_requests.create_index("patient")
        await db.consent_requests.create_index("status")

        await db.consent_artefacts.create_index("artefactId", unique=True)
        await db.consent_artefacts.create_index("consentRequestId")
        await db.consent_artefacts.create_index("status")

        await db.hi_requests.create_index("requestId", unique=True)
        await db.hi_requests.create_index("transactionId")
        await db.hi_requests.create_index("consentId")
        await db.hi_requests.create_index("status")

        await db.hi_transactions.create_index("transactionId", unique=True)
        await db.hi_transactions.create_index("requestId")

        await db.health_bundles.create_index("id")
        await db.health_bundles.create_index("transactionId")
        await db.health_bundles.create_index("patient.id")
        await db.health_bundles.create_index("hiType")
        await db.health_bundles.create_index("timestamp")

        logger.info("Created MongoDB indexes for HIU collections")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down HIU service...")
    try:
        client.close()
        logger.info("MongoDB connection closed")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {e}")


# Create FastAPI app
app = FastAPI(
    title=settings.service_name,
    description="Health Information User (HIU) Service for ABDM - Requests and collects patient health data via consent flow",
    version=settings.service_version,
    lifespan=lifespan,
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

# Mount API routers
app.include_router(consent_management.router, prefix="", tags=["Consent Management"])
app.include_router(data_collection.router, prefix="", tags=["Health Information"])
app.include_router(records_query.router, prefix="", tags=["Records Query"])


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns the current status of the HIU service and its dependencies.
    """
    try:
        # Check MongoDB connection
        db = database.get_database()
        await db.command("ping")
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "service": settings.service_name,
        "version": settings.service_version,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "database": db_status,
        }
    }


@app.get("/", tags=["Information"])
async def get_service_info():
    """
    Get HIU service information.

    Returns metadata about the HIU service including ID, name, and available endpoints.
    """
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "environment": settings.environment,
        "hiu_id": settings.hiu_id,
        "hiu_name": settings.hiu_name,
        "endpoints": {
            "health": "/health",
            "info": "/",
            "openapi": "/docs",

            # Consent Management
            "consent_request_init": "POST /v0.5/consent-requests/init",
            "consent_request_callback": "POST /v0.5/consent-requests/on-init",
            "consent_notification": "POST /v0.5/consents/hiu/notify",

            # Health Information
            "hi_request": "POST /v0.5/health-information/cm/request",
            "hi_request_callback": "POST /v0.5/health-information/cm/on-request",

            # Records Query
            "patient_records": "GET /v0.5/patients/{abha}/records",
            "bundle_retrieve": "GET /v0.5/health-bundles/{bundle_id}",
            "list_hi_requests": "GET /v0.5/hi-requests",
            "list_consent_requests": "GET /v0.5/consent-requests",
        }
    }


@app.get("/openapi.json", tags=["API Documentation"])
async def get_openapi():
    """
    Get OpenAPI schema.

    Returns the OpenAPI specification for this service.
    """
    return app.openapi()


if __name__ == "__main__":
    logger.info(f"Starting HIU service on {settings.host}:{settings.port}")
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )
