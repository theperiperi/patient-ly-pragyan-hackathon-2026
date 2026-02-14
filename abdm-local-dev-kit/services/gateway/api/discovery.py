"""
Gateway Patient Discovery Endpoints

Implements ABDM Gateway patient discovery APIs:
- POST /v0.5/care-contexts/discover (Gateway → HIP)
- POST /v0.5/care-contexts/on-discover (HIP → Gateway callback)

All endpoints follow async 202 Accepted pattern.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4
import logging

from middleware.callback_router import CallbackRouter
from main import get_database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v0.5", tags=["patient-discovery"])


# Request/Response Models based on ABDM schema (gateway.yaml:3030-3175)

class Identifier(BaseModel):
    """Patient identifier (MOBILE, MR, NDHM_HEALTH_NUMBER, HEALTH_ID)."""
    type: str = Field(..., description="Identifier type: MR, MOBILE, NDHM_HEALTH_NUMBER, HEALTH_ID")
    value: str = Field(..., example="+919800083232")


class PatientDiscoveryPatient(BaseModel):
    """Patient details for discovery request."""
    id: str = Field(..., example="patient@sbx", description="Identifier of patient at consent manager")
    verifiedIdentifiers: List[Identifier] = Field(..., description="Verified identifiers like ABHA, mobile")
    unverifiedIdentifiers: Optional[List[Identifier]] = Field(default=None, description="Unverified identifiers")
    name: str = Field(..., example="chandler bing")
    gender: str = Field(..., description="Patient gender: M, F, O, U")
    yearOfBirth: int = Field(..., example=2000)


class PatientDiscoveryRequest(BaseModel):
    """Request for patient discovery at HIP."""
    requestId: UUID = Field(..., description="Unique nonce for each HTTP request")
    timestamp: datetime
    transactionId: UUID = Field(..., description="Correlation ID for discovery and subsequent linkage")
    patient: PatientDiscoveryPatient


class CareContextRepresentation(BaseModel):
    """Care context with reference number and display name."""
    referenceNumber: str = Field(..., description="HIP-specific care context ID")
    display: str = Field(..., description="Human-readable care context name")


class PatientRepresentation(BaseModel):
    """Matched patient representation from HIP."""
    referenceNumber: str = Field(..., description="HIP-specific patient ID")
    display: str = Field(..., description="Patient display name")
    careContexts: Optional[List[CareContextRepresentation]] = Field(default=None, description="Associated care contexts")
    matchedBy: Optional[List[str]] = Field(default=None, description="Identifiers that matched (MOBILE, MR, etc.)")


class RequestReference(BaseModel):
    """Standard request reference in response."""
    requestId: str = Field(..., description="Original request ID")


class Error(BaseModel):
    """Error details."""
    code: int = Field(..., description="Error code")
    message: str = Field(..., description="Error message")


class PatientDiscoveryResult(BaseModel):
    """Response from HIP with discovered patient."""
    requestId: UUID = Field(..., description="Original request ID")
    timestamp: datetime
    transactionId: UUID = Field(..., description="Same transaction ID from request")
    patient: Optional[PatientRepresentation] = Field(default=None, description="Matched patient if found")
    error: Optional[Error] = Field(default=None, description="Error if patient not found")
    resp: RequestReference = Field(..., description="Request reference")


class AcknowledgementResponse(BaseModel):
    """Standard 202 Accepted acknowledgement."""
    requestId: UUID
    timestamp: datetime
    resp: dict = Field(default_factory=lambda: {"requestId": str(uuid4())})


# API Endpoints

@router.post("/care-contexts/discover", status_code=202, response_model=AcknowledgementResponse)
async def discover_patient(
    request: PatientDiscoveryRequest,
    background_tasks: BackgroundTasks,
    db = Depends(get_database)
):
    """
    Initiate patient discovery at HIP.

    Flow:
    1. Receive discovery request from Consent Manager
    2. Validate request
    3. Return 202 Accepted immediately
    4. Forward to HIP asynchronously
    5. HIP will callback to /care-contexts/on-discover

    Args:
        request: Patient discovery request with demographics
        background_tasks: FastAPI background tasks
        db: Database connection

    Returns:
        202 Accepted acknowledgement
    """
    logger.info(f"Received patient discovery request {request.requestId} for patient {request.patient.id}")

    # Create callback router
    router_instance = CallbackRouter(db)

    # Determine target HIP (in production, route based on hip_id from request)
    # For now, route to our local HIP service
    hip_endpoint = "/v0.5/care-contexts/discover"

    # Schedule background task to forward to HIP
    background_tasks.add_task(
        router_instance.route_to_service,
        service="hip",
        endpoint=hip_endpoint,
        payload=request.dict(by_alias=True),
        request_id=str(request.requestId),
        transaction_id=str(request.transactionId)
    )

    # Return immediate acknowledgement
    return AcknowledgementResponse(
        requestId=request.requestId,
        timestamp=datetime.now(),
        resp={"requestId": str(uuid4())}
    )


@router.post("/care-contexts/on-discover")
async def on_patient_discovery(
    response: PatientDiscoveryResult,
    db = Depends(get_database)
):
    """
    Callback from HIP with patient discovery result.

    This endpoint receives the HIP's discovery result and forwards it
    back to the Consent Manager via callback.

    Args:
        response: Discovery result from HIP (patient found or error)
        db: Database connection

    Returns:
        Acknowledgement
    """
    logger.info(f"Received on-discover callback for request {response.requestId}")

    if response.patient:
        logger.info(f"Patient found: {response.patient.referenceNumber} with {len(response.patient.careContexts or [])} care contexts")
    elif response.error:
        logger.warning(f"Patient not found: {response.error.message}")

    router_instance = CallbackRouter(db)

    # Get callback URL for this request (stored when discovery was initiated)
    callback_url = await router_instance.get_callback_url(str(response.requestId))

    if callback_url:
        # Forward to Consent Manager
        success = await router_instance.route_callback(
            callback_url=callback_url,
            payload=response.dict(by_alias=True),
            request_id=str(response.requestId)
        )

        if success:
            await router_instance.mark_callback_delivered(str(response.requestId))

    return {"acknowledged": True}
