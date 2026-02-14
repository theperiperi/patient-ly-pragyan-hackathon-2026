"""
Gateway Consent Flow Endpoints

Implements ABDM Gateway consent flow APIs:
- Consent request initiation (HIU → CM)
- Consent request status
- Consent artefact fetching

All endpoints follow async 202 Accepted pattern.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4
import logging

from middleware.callback_router import CallbackRouter, route_consent_request
from main import get_database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v0.5", tags=["consent-flow"])


# Request/Response Models based on ABDM schema
class ConsentPurpose(BaseModel):
    """Purpose of consent request."""
    text: str
    code: str
    refUri: Optional[str] = None


class DateRange(BaseModel):
    """Date range for health information access."""
    from_date: datetime = Field(..., alias="from")
    to_date: datetime = Field(..., alias="to")

    class Config:
        populate_by_name = True


class Frequency(BaseModel):
    """Access frequency."""
    unit: str  # HOUR, DAY, WEEK, MONTH, YEAR
    value: int
    repeats: int


class Permission(BaseModel):
    """Access permissions."""
    accessMode: str  # VIEW, STORE, QUERY, STREAM
    dateRange: DateRange
    dataEraseAt: datetime
    frequency: Frequency


class PatientIdentifier(BaseModel):
    """Patient identifier."""
    id: str  # ABHA@sbx


class OrganizationRef(BaseModel):
    """Organization reference."""
    id: str


class CareContext(BaseModel):
    """Care context reference."""
    patientReference: str
    careContextReference: str


class RequesterIdentifier(BaseModel):
    """Requester identifier structure per ABDM spec."""
    type: str = Field(..., description="Identifier type, e.g., REGNO")
    value: str = Field(..., description="Identifier value, e.g., MH1001")
    system: str = Field(..., description="Identifier system URL, e.g., https://www.mciindia.org")


class Requester(BaseModel):
    """Consent requester details."""
    name: str
    identifier: Optional[RequesterIdentifier] = None


class ConsentDetail(BaseModel):
    """Consent request details."""
    purpose: ConsentPurpose
    patient: PatientIdentifier
    hip: Optional[OrganizationRef] = None
    careContexts: Optional[List[CareContext]] = None
    hiu: OrganizationRef
    requester: Requester
    hiTypes: List[str]
    permission: Permission
    consentNotificationUrl: str = Field(..., description="URL for consent status notifications")


class ConsentRequestInit(BaseModel):
    """Consent request initialization."""
    requestId: UUID
    timestamp: datetime
    consent: ConsentDetail


class ConsentRequestResponse(BaseModel):
    """Response for consent request initialization."""
    id: UUID = Field(..., description="Consent request ID")
    timestamp: datetime


class AcknowledgementResponse(BaseModel):
    """Standard 202 Accepted acknowledgement."""
    requestId: UUID
    timestamp: datetime
    resp: dict = Field(default_factory=lambda: {"requestId": str(uuid4())})


class ErrorResponse(BaseModel):
    """Error response structure."""
    code: int
    message: str


class ConsentRequestStatusRequest(BaseModel):
    """Request for consent request status."""
    requestId: UUID
    timestamp: datetime
    consentRequestId: UUID


class ConsentFetchRequest(BaseModel):
    """Request to fetch consent artefact."""
    requestId: UUID
    timestamp: datetime
    consentId: UUID


# API Endpoints

@router.post("/consent-requests/init", status_code=202, response_model=AcknowledgementResponse)
async def init_consent_request(
    request: ConsentRequestInit,
    background_tasks: BackgroundTasks,
    db = Depends(get_database)
):
    """
    Initialize consent request from HIU.

    Flow:
    1. Receive consent request from HIU
    2. Validate request
    3. Return 202 Accepted immediately
    4. Forward to Consent Manager asynchronously
    5. CM will callback to HIU's consentNotificationUrl

    Args:
        request: Consent request initialization
        background_tasks: FastAPI background tasks
        token: Authenticated token
        db: Database connection

    Returns:
        202 Accepted acknowledgement
    """
    logger.info(f"Received consent request {request.requestId} from HIU {request.consent.hiu.id}")

    # Validate requester is authorized HIU
    # (In production, verify token.client_id matches request.consent.hiu.id)

    # Create callback router
    router_instance = CallbackRouter(db)

    # Schedule background task to forward to CM
    background_tasks.add_task(
        route_consent_request,
        router=router_instance,
        consent_request=request.dict(by_alias=True),
        request_id=str(request.requestId),
        callback_url=request.consent.consentNotificationUrl
    )

    # Return immediate acknowledgement
    return AcknowledgementResponse(
        requestId=request.requestId,
        timestamp=datetime.now(),
        resp={"requestId": str(uuid4())}
    )


@router.post("/consent-requests/status", status_code=202, response_model=AcknowledgementResponse)
async def get_consent_request_status(
    request: ConsentRequestStatusRequest,
    background_tasks: BackgroundTasks,

    db = Depends(get_database)
):
    """
    Get status of consent request.

    Flow:
    1. Receive status request from HIU
    2. Return 202 Accepted
    3. Query CM for status asynchronously
    4. CM will callback with status

    Args:
        request: Status request
        background_tasks: FastAPI background tasks
        token: Authenticated token
        db: Database connection

    Returns:
        202 Accepted acknowledgement
    """
    logger.info(f"Received consent status request for {request.consentRequestId}")

    router_instance = CallbackRouter(db)

    # Forward to CM
    background_tasks.add_task(
        router_instance.route_to_service,
        service="consent_manager",
        endpoint="/v0.5/consent-requests/status",
        payload=request.dict(),
        request_id=str(request.requestId)
    )

    return AcknowledgementResponse(
        requestId=request.requestId,
        timestamp=datetime.now()
    )


@router.post("/consents/fetch", status_code=202, response_model=AcknowledgementResponse)
async def fetch_consent_artefact(
    request: ConsentFetchRequest,
    background_tasks: BackgroundTasks,

    db = Depends(get_database)
):
    """
    Fetch consent artefact by consent ID.

    Flow:
    1. Receive fetch request from HIU
    2. Return 202 Accepted
    3. Query CM for consent artefact
    4. CM will callback with artefact

    Args:
        request: Fetch request
        background_tasks: FastAPI background tasks
        token: Authenticated token
        db: Database connection

    Returns:
        202 Accepted acknowledgement
    """
    logger.info(f"Received consent fetch request for {request.consentId}")

    router_instance = CallbackRouter(db)

    # Forward to CM
    background_tasks.add_task(
        router_instance.route_to_service,
        service="consent_manager",
        endpoint="/v0.5/consents/fetch",
        payload=request.dict(),
        request_id=str(request.requestId)
    )

    return AcknowledgementResponse(
        requestId=request.requestId,
        timestamp=datetime.now()
    )


# Callback endpoints (from Consent Manager)

@router.post("/consent-requests/on-init")
async def on_consent_request_init(
    response: dict,
    db = Depends(get_database)
):
    """
    Callback from Consent Manager after consent request creation.

    This endpoint receives the CM's response and forwards it to the HIU
    via the registered callback URL.

    Args:
        response: Consent request creation response from CM
        db: Database connection

    Returns:
        Acknowledgement
    """
    request_id = response.get("requestId") or response.get("resp", {}).get("requestId")
    logger.info(f"Received on-init callback for request {request_id}")

    router_instance = CallbackRouter(db)

    # Get callback URL for this request
    callback_url = await router_instance.get_callback_url(request_id)

    if callback_url:
        # Forward to HIU
        success = await router_instance.route_callback(
            callback_url=callback_url,
            payload=response,
            request_id=request_id
        )

        if success:
            await router_instance.mark_callback_delivered(request_id)

    return {"acknowledged": True}


@router.post("/consent-requests/on-status")
async def on_consent_request_status(
    response: dict,
    db = Depends(get_database)
):
    """
    Callback from CM with consent request status.

    Args:
        response: Consent status from CM
        db: Database connection

    Returns:
        Acknowledgement
    """
    request_id = response.get("requestId") or response.get("resp", {}).get("requestId")
    logger.info(f"Received on-status callback for request {request_id}")

    router_instance = CallbackRouter(db)
    callback_url = await router_instance.get_callback_url(request_id)

    if callback_url:
        await router_instance.route_callback(
            callback_url=callback_url,
            payload=response,
            request_id=request_id
        )

    return {"acknowledged": True}


@router.post("/consents/on-fetch")
async def on_consent_fetch(
    response: dict,
    db = Depends(get_database)
):
    """
    Callback from CM with consent artefact.

    Args:
        response: Consent artefact from CM
        db: Database connection

    Returns:
        Acknowledgement
    """
    request_id = response.get("requestId") or response.get("resp", {}).get("requestId")
    logger.info(f"Received on-fetch callback for request {request_id}")

    router_instance = CallbackRouter(db)
    callback_url = await router_instance.get_callback_url(request_id)

    if callback_url:
        await router_instance.route_callback(
            callback_url=callback_url,
            payload=response,
            request_id=request_id
        )

    return {"acknowledged": True}
