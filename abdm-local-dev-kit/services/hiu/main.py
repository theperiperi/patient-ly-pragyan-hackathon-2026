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

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)

# Global database connection
db: AsyncIOMotorDatabase = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifespan events (startup and shutdown).

    Connects to MongoDB on startup and closes connection on shutdown.
    """
    # Startup
    logger.info("Starting HIU service...")
    global db
    try:
        client = AsyncIOMotorClient(settings.mongo_uri)
        db = client.get_database()
        # Verify connection
        await client.admin.command("ping")
        logger.info("Successfully connected to MongoDB")
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
    description="Health Information User (HIU) Service for ABDM",
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


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns the current status of the HIU service and its dependencies.
    """
    try:
        # Check MongoDB connection
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

    Returns metadata about the HIU service including ID, name, and version.
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
            "requests": "/health-info/requests",
            "consent": "/consent/list",
        }
    }


@app.post("/health-info/requests", tags=["Health Information"])
async def request_health_information(request_data: dict):
    """
    Request health information from HIP via gateway.

    This endpoint initiates a request for patient health information
    following the ABDM HIU API specifications.

    Args:
        request_data: Request details including patient ID and data range

    Returns:
        Request acknowledgment with request ID and status
    """
    logger.info(f"Received health information request: {request_data}")

    request_id = f"REQ-{datetime.utcnow().timestamp()}"

    return {
        "request_id": request_id,
        "status": "initiated",
        "message": "Health information request has been initiated",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/health-info/requests/{request_id}", tags=["Health Information"])
async def get_request_status(request_id: str):
    """
    Get status of a health information request.

    Args:
        request_id: The ID of the request to check

    Returns:
        Request status and details
    """
    logger.info(f"Checking status of request: {request_id}")

    return {
        "request_id": request_id,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
    }


@app.post("/consent/list", tags=["Consent"])
async def list_consents(query: dict):
    """
    List available consents for the HIU.

    Returns a list of consents that allow this HIU to access patient data.

    Args:
        query: Query parameters for filtering consents

    Returns:
        List of consents and their details
    """
    logger.info(f"Listing consents with query: {query}")

    return {
        "consents": [],
        "total": 0,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/consent/{consent_id}/data", tags=["Consent"])
async def request_data_with_consent(consent_id: str, data_request: dict):
    """
    Request specific health data using an existing consent.

    Args:
        consent_id: The ID of the consent to use
        data_request: Details of what data is being requested

    Returns:
        Data request acknowledgment
    """
    logger.info(f"Data request with consent {consent_id}: {data_request}")

    return {
        "status": "accepted",
        "request_id": f"DATA-{datetime.utcnow().timestamp()}",
        "consent_id": consent_id,
        "timestamp": datetime.utcnow().isoformat(),
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
