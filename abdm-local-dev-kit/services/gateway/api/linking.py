"""
Gateway Care Context Linking Endpoints

Implements ABDM Gateway care context linking APIs:
- POST /v0.5/links/link/init (Gateway → HIP)
- POST /v0.5/links/link/on-init (HIP → Gateway callback)
- POST /v0.5/links/link/confirm (Gateway → HIP)
- POST /v0.5/links/link/on-confirm (HIP → Gateway callback)

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

router = APIRouter(prefix="/v0.5", tags=["care-context-linking"])


# Request/Response Models based on ABDM schema (gateway.yaml:3176-3330)

class CareContext(BaseModel):
    """Care context reference."""
    referenceNumber: str


class PatientLinkPatient(BaseModel):
    """Patient details for link request."""
    id: str = Field(..., example="hinapatel79@ndhm", description="Identifier of patient at consent manager")
    referenceNumber: str = Field(..., example="TMH-PUID-001", description="Patient ID at HIP")
    careContexts: List[CareContext]


class PatientLinkReferenceRequest(BaseModel):
    """Request to initiate care context linking."""
    requestId: UUID
    timestamp: datetime
    transactionId: UUID
    patient: PatientLinkPatient


class Meta(BaseModel):
    """Metadata for OTP communication."""
    communicationMedium: Optional[str] = Field(default=None, description="MOBILE or EMAIL")
    communicationHint: Optional[str] = Field(default=None, description="Masked hint like +91******7890")
    communicationExpiry: Optional[str] = Field(default=None, description="OTP expiry timestamp")


class LinkReference(BaseModel):
    """Link reference with authentication details."""
    referenceNumber: str = Field(..., description="Link reference number for OTP confirmation")
    authenticationType: str = Field(..., description="DIRECT or MEDIATED")
    meta: Optional[Meta] = None


class RequestReference(BaseModel):
    """Standard request reference."""
    requestId: str


class Error(BaseModel):
    """Error details."""
    code: int
    message: str


class PatientLinkReferenceResult(BaseModel):
    """Response from HIP after link init."""
    requestId: UUID
    timestamp: datetime
    transactionId: UUID
    link: Optional[LinkReference] = None
    error: Optional[Error] = None
    resp: RequestReference


class LinkConfirmation(BaseModel):
    """Link confirmation with OTP."""
    linkRefNumber: str = Field(..., description="Reference number from link/init")
    token: str = Field(..., description="OTP token")


class LinkConfirmationRequest(BaseModel):
    """Request to confirm link with OTP."""
    requestId: UUID
    timestamp: datetime
    confirmation: LinkConfirmation


class CareContextRepresentation(BaseModel):
    """Care context representation."""
    referenceNumber: str
    display: str


class PatientResult(BaseModel):
    """Linked patient result."""
    referenceNumber: str
    display: str
    careContexts: List[CareContextRepresentation]


class PatientLinkResult(BaseModel):
    """Response after successful link confirmation."""
    requestId: UUID
    timestamp: datetime
    patient: Optional[PatientResult] = None
    error: Optional[Error] = None
    resp: RequestReference


class AcknowledgementResponse(BaseModel):
    """Standard 202 Accepted acknowledgement."""
    requestId: UUID
    timestamp: datetime
    resp: dict = Field(default_factory=lambda: {"requestId": str(uuid4())})


# API Endpoints

@router.post("/links/link/init", status_code=202, response_model=AcknowledgementResponse)
async def init_link(
    request: PatientLinkReferenceRequest,
    background_tasks: BackgroundTasks,
    db = Depends(get_database)
):
    """
    Initiate care context linking.

    Flow:
    1. Receive link init request from Consent Manager
    2. Validate request
    3. Return 202 Accepted immediately
    4. Forward to HIP asynchronously
    5. HIP sends OTP to patient
    6. HIP calls back to /links/link/on-init

    Args:
        request: Link initialization request
        background_tasks: FastAPI background tasks
        db: Database connection

    Returns:
        202 Accepted acknowledgement
    """
    logger.info(f"Received link init request {request.requestId} for patient {request.patient.id}")

    router_instance = CallbackRouter(db)

    # Forward to HIP
    hip_endpoint = "/v0.5/links/link/init"

    background_tasks.add_task(
        router_instance.route_to_service,
        service="hip",
        endpoint=hip_endpoint,
        payload=request.dict(by_alias=True),
        request_id=str(request.requestId),
        transaction_id=str(request.transactionId)
    )

    return AcknowledgementResponse(
        requestId=request.requestId,
        timestamp=datetime.now(),
        resp={"requestId": str(uuid4())}
    )


@router.post("/links/link/on-init")
async def on_link_init(
    response: PatientLinkReferenceResult,
    db = Depends(get_database)
):
    """
    Callback from HIP after link init (OTP sent).

    Args:
        response: Link reference result from HIP
        db: Database connection

    Returns:
        Acknowledgement
    """
    logger.info(f"Received on-link-init callback for request {response.requestId}")

    if response.link:
        logger.info(f"Link reference: {response.link.referenceNumber}, auth type: {response.link.authenticationType}")
    elif response.error:
        logger.warning(f"Link init failed: {response.error.message}")

    router_instance = CallbackRouter(db)
    callback_url = await router_instance.get_callback_url(str(response.requestId))

    if callback_url:
        success = await router_instance.route_callback(
            callback_url=callback_url,
            payload=response.dict(by_alias=True),
            request_id=str(response.requestId)
        )

        if success:
            await router_instance.mark_callback_delivered(str(response.requestId))

    return {"acknowledged": True}


@router.post("/links/link/confirm", status_code=202, response_model=AcknowledgementResponse)
async def confirm_link(
    request: LinkConfirmationRequest,
    background_tasks: BackgroundTasks,
    db = Depends(get_database)
):
    """
    Confirm care context linking with OTP.

    Flow:
    1. Receive confirmation request from Consent Manager (with OTP)
    2. Return 202 Accepted immediately
    3. Forward to HIP asynchronously
    4. HIP verifies OTP and links care contexts
    5. HIP calls back to /links/link/on-confirm

    Args:
        request: Link confirmation request with OTP
        background_tasks: FastAPI background tasks
        db: Database connection

    Returns:
        202 Accepted acknowledgement
    """
    logger.info(f"Received link confirm request {request.requestId} for linkRef {request.confirmation.linkRefNumber}")

    router_instance = CallbackRouter(db)

    # Forward to HIP
    hip_endpoint = "/v0.5/links/link/confirm"

    background_tasks.add_task(
        router_instance.route_to_service,
        service="hip",
        endpoint=hip_endpoint,
        payload=request.dict(by_alias=True),
        request_id=str(request.requestId)
    )

    return AcknowledgementResponse(
        requestId=request.requestId,
        timestamp=datetime.now(),
        resp={"requestId": str(uuid4())}
    )


@router.post("/links/link/on-confirm")
async def on_link_confirm(
    response: PatientLinkResult,
    db = Depends(get_database)
):
    """
    Callback from HIP after link confirmation.

    Args:
        response: Link result from HIP (success or error)
        db: Database connection

    Returns:
        Acknowledgement
    """
    logger.info(f"Received on-link-confirm callback for request {response.requestId}")

    if response.patient:
        logger.info(f"Link confirmed for patient {response.patient.referenceNumber} with {len(response.patient.careContexts)} care contexts")
    elif response.error:
        logger.warning(f"Link confirmation failed: {response.error.message}")

    router_instance = CallbackRouter(db)
    callback_url = await router_instance.get_callback_url(str(response.requestId))

    if callback_url:
        success = await router_instance.route_callback(
            callback_url=callback_url,
            payload=response.dict(by_alias=True),
            request_id=str(response.requestId)
        )

        if success:
            await router_instance.mark_callback_delivered(str(response.requestId))

    return {"acknowledged": True}
