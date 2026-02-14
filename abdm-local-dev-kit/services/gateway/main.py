import logging
import uvicorn
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from datetime import datetime

from config import settings
from middleware.logging import LoggingMiddleware
from middleware.auth import AuthMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global database connection
db_client: AsyncIOMotorClient = None
db: AsyncIOMotorDatabase = None


async def connect_to_mongo():
    """Connect to MongoDB."""
    global db_client, db
    try:
        db_client = AsyncIOMotorClient(settings.mongo_uri)
        db = db_client[settings.mongodb_database]
        # Verify connection
        await db_client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {settings.mongodb_database}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise


async def close_mongo_connection():
    """Close MongoDB connection."""
    global db_client
    if db_client:
        db_client.close()
        logger.info("Closed MongoDB connection")


def get_database():
    """Dependency to get database connection."""
    global db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    logger.info(f"Starting {settings.service_name} v{settings.service_version}")
    try:
        await connect_to_mongo()
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        raise

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.service_name}")
    await close_mongo_connection()


# Create FastAPI app
app = FastAPI(
    title=settings.service_name,
    version=settings.service_version,
    description="ABDM Gateway service for routing requests between HIPs, HIUs, and Consent Manager",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers
)

# Add custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(AuthMiddleware)

# Include API routers
from api import consent_flow, discovery, linking, health_information
app.include_router(consent_flow.router)
app.include_router(discovery.router)
app.include_router(linking.router)
app.include_router(health_information.router)


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.service_name,
        "version": settings.service_version,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/")
async def root() -> dict:
    """Root endpoint returning service information."""
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "environment": settings.environment,
        "description": "ABDM Gateway service for routing requests between HIPs, HIUs, and Consent Manager",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        }
    }


@app.get("/status")
async def status() -> dict:
    """Status endpoint with detailed service information."""
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "environment": settings.environment,
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "database": {
            "mongodb_url": settings.mongodb_url,
            "database": settings.mongodb_database
        },
        "services": {
            "hip_service_url": settings.hip_service_url,
            "hiu_service_url": settings.hiu_service_url,
            "consent_manager_url": settings.consent_manager_url
        }
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    logger.info(f"Starting {settings.service_name} on {settings.host}:{settings.port}")
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower()
    )
