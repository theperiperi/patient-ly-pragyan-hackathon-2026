"""
Gateway Health Information Request Endpoints

Implements ABDM Gateway health information request APIs:
- POST /v0.5/health-information/cm/request (HIU → Gateway → CM)
- POST /v0.5/health-information/cm/on-request (CM → Gateway → HIU callback)
- POST /v0.5/health-information/hip/on-request (HIP → Gateway callback)

All endpoints follow async 202 Accepted pattern.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
import logging

from middleware.callback_router import CallbackRouter
from main import get_database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v0.5", tags=["health-information"])


# Request/Response Models based on ABDM schema (gateway.yaml:3331+, 3980+, 4008+)

class DateRange(BaseModel):
    """Date range for health information."""
    from_date: datetime = Field(..., alias="from")
    to_date: datetime = Field(..., alias="to")

    class Config:
        populate_by_name = True


class Consent(BaseModel):
    """Consent reference."""
    id: str = Field(..., description="Consent artefact ID")


class KeyObject(BaseModel):
    """Public key object."""
    expiry: datetime = Field(..., description="Key expiry timestamp")
    parameters: str = Field(..., example="Curve25519/32byte random key")
    keyValue: str = Field(..., description="Base64 encoded public key")


class KeyMaterial(BaseModel):
    """Encryption key material for data transfer."""
    cryptoAlg: str = Field(..., example="ECDH", description="Cryptographic algorithm")
    curve: str = Field(..., example="Curve25519", description="Elliptic curve")
    dhPublicKey: KeyObject = Field(..., description="Diffie-Hellman public key")
    nonce: str = Field(..., description="32 byte nonce")


class HIRequestDetail(BaseModel):
    """Health information request details."""
    consent: Consent
    dateRange: DateRange
    dataPushUrl: str = Field(..., description="URL where HIP should push encrypted data")
    keyMaterial: KeyMaterial


class HIRequest(BaseModel):
    """Health information request from HIU."""
    requestId: UUID
    timestamp: datetime
    hiRequest: HIRequestDetail


class HIRequestInfo(BaseModel):
    """HI request info in response."""
    transactionId: UUID
    sessionStatus: str = Field(..., description="REQUESTED or ACKNOWLEDGED")


class RequestReference(BaseModel):
    """Request reference."""
    requestId: str


class Error(BaseModel):
    """Error details."""
    code: int
    message: str


class HIUHealthInformationRequestResponse(BaseModel):
    """Response from CM to HIU about HI request."""
    requestId: UUID
    timestamp: datetime
    hiRequest: Optional[HIRequestInfo] = None
    error: Optional[Error] = None
    resp: RequestReference


class HIPHIRequestDetail(BaseModel):
    """HI request details sent to HIP."""
    consent: Consent
    dateRange: DateRange
    dataPushUrl: str
    keyMaterial: KeyMaterial


class HIPHIRequest(BaseModel):
    """Health information request to HIP."""
    requestId: UUID
    timestamp: datetime
    transactionId: UUID
    hiRequest: HIPHIRequestDetail


class AcknowledgementResponse(BaseModel):
    """Standard 202 Accepted acknowledgement."""
    requestId: UUID
    timestamp: datetime
    resp: dict = Field(default_factory=lambda: {"requestId": str(uuid4())})


# API Endpoints

@router.post("/health-information/cm/request", status_code=202, response_model=AcknowledgementResponse)
async def request_health_information(
    request: HIRequest,
    background_tasks: BackgroundTasks,
    db = Depends(get_database)
):
    """
    Request health information from CM/HIP.

    Flow:
    1. Receive HI request from HIU (with consent ID, date range, encryption keys)
    2. Return 202 Accepted immediately
    3. Forward to Consent Manager asynchronously
    4. CM validates consent and generates transaction ID
    5. CM calls back to /health-information/cm/on-request
    6. CM forwards to HIP via /health-information/hip/request
    7. HIP retrieves and encrypts data, pushes to dataPushUrl

    Args:
        request: Health information request
        background_tasks: FastAPI background tasks
        db: Database connection

    Returns:
        202 Accepted acknowledgement
    """
    logger.info(f"Received HI request {request.requestId} for consent {request.hiRequest.consent.id}")

    router_instance = CallbackRouter(db)

    # Forward to Consent Manager
    cm_endpoint = "/v0.5/health-information/cm/request"

    background_tasks.add_task(
        router_instance.route_to_service,
        service="consent_manager",
        endpoint=cm_endpoint,
        payload=request.dict(by_alias=True),
        request_id=str(request.requestId)
    )

    return AcknowledgementResponse(
        requestId=request.requestId,
        timestamp=datetime.now(),
        resp={"requestId": str(uuid4())}
    )


@router.post("/health-information/cm/on-request")
async def on_hi_request_from_cm(
    response: HIUHealthInformationRequestResponse,
    background_tasks: BackgroundTasks,
    db = Depends(get_database)
):
    """
    Callback from CM with HI request acknowledgement.

    This callback confirms that CM has validated the consent and
    created a transaction ID for the HI request. If successful,
    the HIP will be notified separately to push data.

    Args:
        response: HI request response from CM
        background_tasks: FastAPI background tasks
        db: Database connection

    Returns:
        Acknowledgement
    """
    logger.info(f"Received on-request callback from CM for request {response.requestId}")

    if response.hiRequest:
        logger.info(f"HI request acknowledged: transaction {response.hiRequest.transactionId}, status {response.hiRequest.sessionStatus}")
    elif response.error:
        logger.warning(f"HI request failed: {response.error.message}")

    router_instance = CallbackRouter(db)

    # Get callback URL for original HIU request
    callback_url = await router_instance.get_callback_url(str(response.requestId))

    if callback_url:
        # Forward to HIU
        success = await router_instance.route_callback(
            callback_url=callback_url,
            payload=response.dict(by_alias=True),
            request_id=str(response.requestId)
        )

        if success:
            await router_instance.mark_callback_delivered(str(response.requestId))

    return {"acknowledged": True}


@router.post("/health-information/hip/on-request")
async def on_hi_request_from_hip(
    response: dict,
    db = Depends(get_database)
):
    """
    Callback from HIP acknowledging HI request.

    This callback confirms that HIP has received the request
    and will push data to the dataPushUrl.

    Args:
        response: Acknowledgement from HIP
        db: Database connection

    Returns:
        Acknowledgement
    """
    request_id = response.get("requestId")
    logger.info(f"Received on-request callback from HIP for request {request_id}")

    # Log for monitoring (data push will happen directly to dataPushUrl)
    logger.info(f"HIP acknowledged HI request, data will be pushed to dataPushUrl")

    return {"acknowledged": True}
