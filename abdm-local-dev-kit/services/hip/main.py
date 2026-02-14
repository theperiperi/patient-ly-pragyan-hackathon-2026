"""HIP (Health Information Provider) Service - FastAPI Application."""
import logging
import logging.config
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from config import settings
from middleware import LoggingMiddleware, AuthMiddleware


# Configure logging
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "root": {
        "level": settings.log_level,
        "handlers": ["default"],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


# Global database connection
db: Optional[AsyncIOMotorDatabase] = None


def get_database():
    """Dependency to get database connection."""
    global db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage FastAPI application lifecycle."""
    global db

    # Startup
    logger.info(f"Starting {settings.service_name} service...")

    # Connect to MongoDB
    try:
        mongo_client = AsyncIOMotorClient(settings.mongo_uri)
        db = mongo_client[settings.mongo_db_name]

        # Verify connection
        await mongo_client.admin.command("ping")
        logger.info(f"Connected to MongoDB: {settings.mongo_db_name}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise

    logger.info(f"{settings.service_name} service started on port {settings.port}")

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.service_name} service...")
    if mongo_client:
        mongo_client.close()
    logger.info(f"{settings.service_name} service stopped")


# Create FastAPI application
app = FastAPI(
    title="ABDM HIP Service",
    description="Health Information Provider service for ABDM (Ayushman Bharat Digital Mission)",
    version="1.0.0",
    lifespan=lifespan,
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware (order matters - add in reverse order of execution)
app.add_middleware(AuthMiddleware)
app.add_middleware(LoggingMiddleware)


# Include API routers
from api import discovery, linking, data_transfer, callbacks
app.include_router(discovery.router)
app.include_router(linking.router)
app.include_router(data_transfer.router)
app.include_router(callbacks.router)


# Endpoint: Health Check
@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    try:
        # Check MongoDB connection
        if db is None:
            raise Exception("Database not initialized")

        await db.client.admin.command("ping")

        return {
            "status": "healthy",
            "service": settings.service_name,
            "version": "1.0.0",
            "database": "connected",
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy",
        )


# Endpoint: Service Info
@app.get("/")
async def service_info():
    """Get HIP service information."""
    return {
        "service": settings.service_name,
        "version": "1.0.0",
        "description": "ABDM Health Information Provider Service",
        "facility_id": settings.facility_id,
        "facility_name": settings.facility_name,
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
        },
        "standards": {
            "fhir": "R4",
            "abdm_compliance": "v6.5.0",
        },
    }


# Health Information Types endpoints (placeholders for future implementation)
@app.get("/health-information/discharge-summaries")
async def get_discharge_summaries(
    patient_id: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
):
    """Get discharge summaries for a patient."""
    return {
        "health_information_type": "discharge-summary",
        "count": 0,
        "records": [],
    }


@app.get("/health-information/prescriptions")
async def get_prescriptions(
    patient_id: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
):
    """Get prescriptions for a patient."""
    return {
        "health_information_type": "prescription",
        "count": 0,
        "records": [],
    }


@app.get("/health-information/diagnostic-reports")
async def get_diagnostic_reports(
    patient_id: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
):
    """Get diagnostic reports for a patient."""
    return {
        "health_information_type": "diagnostic-report",
        "count": 0,
        "records": [],
    }


@app.get("/health-information/op-consultations")
async def get_op_consultations(
    patient_id: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
):
    """Get outpatient consultation records for a patient."""
    return {
        "health_information_type": "op-consultation",
        "count": 0,
        "records": [],
    }


@app.get("/health-information/immunization-records")
async def get_immunization_records(
    patient_id: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
):
    """Get immunization records for a patient."""
    return {
        "health_information_type": "immunization-record",
        "count": 0,
        "records": [],
    }


@app.get("/health-information/wellness-records")
async def get_wellness_records(
    patient_id: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
):
    """Get wellness records for a patient."""
    return {
        "health_information_type": "wellness-record",
        "count": 0,
        "records": [],
    }


@app.get("/health-information/health-documents")
async def get_health_documents(
    patient_id: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
):
    """Get health documents for a patient."""
    return {
        "health_information_type": "health-document",
        "count": 0,
        "records": [],
    }


# Patient Management endpoints
@app.get("/patients")
async def list_patients(skip: int = 0, limit: int = 100):
    """List all patients in the HIP."""
    return {
        "total": 0,
        "skip": skip,
        "limit": limit,
        "patients": [],
    }


@app.get("/patients/{patient_id}")
async def get_patient(patient_id: str):
    """Get patient details."""
    return {
        "patient_id": patient_id,
        "name": None,
        "date_of_birth": None,
        "gender": None,
        "phone": None,
        "email": None,
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler."""
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail,
            "service": settings.service_name,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Generic exception handler."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "status_code": 500,
            "message": "Internal server error",
            "service": settings.service_name,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.port,
        log_level=settings.log_level.lower(),
    )
