"""
HIP Callback Handlers

Implements ABDM Gateway callback endpoints for HIP:
- POST /v0.5/care-contexts/on-discover - Discovery result callback
- POST /v0.5/links/link/on-init - Link initialization callback
- POST /v0.5/links/link/on-confirm - Link confirmation callback
- POST /v0.5/health-information/hip/on-request - HI request callback
- POST /v0.5/links/link/add-contexts - Add care contexts to link
- POST /v0.5/links/link/on-add-contexts - Add contexts callback
- POST /v0.5/links/context/notify - Notify context changes
- POST /v0.5/links/context/on-notify - Context notify callback

These endpoints receive async callbacks from the Gateway after HIP
initiates operations or when external parties need to notify HIP.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
import logging

from main import get_database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v0.5", tags=["callbacks"])


# ============================================================================
# Pydantic Models (matching gateway.yaml schema)
# ============================================================================

class RequestReference(BaseModel):
    """Standard request reference."""
    requestId: str


class Error(BaseModel):
    """Error details."""
    code: int
    message: str


class AcknowledgementResponse(BaseModel):
    """Standard acknowledgement response."""
    acknowledged: bool = True


# Discovery Callback Models

class CareContextRepresentation(BaseModel):
    """Care context representation."""
    referenceNumber: str
    display: str


class PatientRepresentation(BaseModel):
    """Patient representation in discovery result."""
    referenceNumber: str
    display: str
    careContexts: Optional[List[CareContextRepresentation]] = None
    matchedBy: Optional[List[str]] = None


class DiscoveryResult(BaseModel):
    """Discovery result from Gateway."""
    requestId: UUID
    timestamp: datetime
    transactionId: UUID
    patient: Optional[PatientRepresentation] = None
    error: Optional[Error] = None
    resp: RequestReference


# Link Initialization Callback Models

class Meta(BaseModel):
    """OTP communication metadata."""
    communicationMedium: Optional[str] = None
    communicationHint: Optional[str] = None
    communicationExpiry: Optional[str] = None


class LinkReference(BaseModel):
    """Link reference with OTP details."""
    referenceNumber: str
    authenticationType: str
    meta: Optional[Meta] = None


class LinkInitResult(BaseModel):
    """Link initialization result from Gateway."""
    requestId: UUID
    timestamp: datetime
    transactionId: UUID
    link: Optional[LinkReference] = None
    error: Optional[Error] = None
    resp: RequestReference


# Link Confirmation Callback Models

class PatientLinkResult(BaseModel):
    """Patient link confirmation result."""
    referenceNumber: str
    display: str
    careContexts: List[CareContextRepresentation]


class LinkConfirmResult(BaseModel):
    """Link confirmation result from Gateway."""
    requestId: UUID
    timestamp: datetime
    patient: Optional[PatientLinkResult] = None
    error: Optional[Error] = None
    resp: RequestReference


# Health Information Request Callback Models

class HIRequestAcknowledgement(BaseModel):
    """HI request acknowledgement details."""
    transactionId: UUID
    sessionStatus: str  # REQUESTED, ACKNOWLEDGED


class HIRequestResult(BaseModel):
    """HI request result from Gateway."""
    requestId: UUID
    timestamp: datetime
    hiRequest: Optional[HIRequestAcknowledgement] = None
    error: Optional[Error] = None
    resp: RequestReference


# Add Contexts Models

class CareContext(BaseModel):
    """Care context reference."""
    referenceNumber: str
    display: str


class PatientReference(BaseModel):
    """Patient reference for add-contexts."""
    referenceNumber: str
    display: str


class LinkAddContextsRequest(BaseModel):
    """Request to add more care contexts to existing link."""
    requestId: UUID
    timestamp: datetime
    link: PatientReference
    patient: PatientReference
    careContexts: List[CareContext]


class AddContextsResult(BaseModel):
    """Result of add-contexts operation."""
    requestId: UUID
    timestamp: datetime
    acknowledgement: Optional[dict] = None
    error: Optional[Error] = None
    resp: RequestReference


# Context Notification Models

class ContextNotificationContent(BaseModel):
    """Context notification content."""
    careContext: CareContext
    hiTypes: List[str]
    date: datetime
    period: Optional[dict] = None


class ContextNotifyRequest(BaseModel):
    """Context change notification request."""
    requestId: UUID
    timestamp: datetime
    notification: ContextNotificationContent


class ContextNotifyResult(BaseModel):
    """Context notification result."""
    requestId: UUID
    timestamp: datetime
    acknowledgement: Optional[dict] = None
    error: Optional[Error] = None
    resp: RequestReference


# ============================================================================
# Callback Endpoints
# ============================================================================

@router.post("/care-contexts/on-discover")
async def on_discovery_callback(
    result: DiscoveryResult,
    db = Depends(get_database)
):
    """
    Callback from Gateway with patient discovery result.

    This endpoint is called by Gateway after CM forwards the discovery
    result from HIP. Updates the discovery request status in database.

    Args:
        result: Discovery result (patient found or error)
        db: Database connection

    Returns:
        Acknowledgement
    """
    logger.info(f"Received on-discover callback for request {result.requestId}")

    try:
        # Store discovery result in database
        discovery_record = {
            "requestId": str(result.requestId),
            "transactionId": str(result.transactionId),
            "timestamp": result.timestamp,
            "status": "COMPLETED" if result.patient else "FAILED",
            "patient": result.patient.dict() if result.patient else None,
            "error": result.error.dict() if result.error else None,
            "updated_at": datetime.now()
        }

        # Update or insert discovery record
        await db.discovery_requests.update_one(
            {"requestId": str(result.requestId)},
            {"$set": discovery_record},
            upsert=True
        )

        if result.patient:
            logger.info(f"Discovery successful: patient {result.patient.referenceNumber} with {len(result.patient.careContexts or [])} care contexts")
        else:
            logger.warning(f"Discovery failed: {result.error.message if result.error else 'Unknown error'}")

        return AcknowledgementResponse()

    except Exception as e:
        logger.error(f"Error processing on-discover callback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/links/link/on-init")
async def on_link_init_callback(
    result: LinkInitResult,
    db = Depends(get_database)
):
    """
    Callback from Gateway after link initialization (OTP sent).

    This callback confirms that OTP has been sent to patient for
    linking care contexts.

    Args:
        result: Link initialization result with OTP reference
        db: Database connection

    Returns:
        Acknowledgement
    """
    logger.info(f"Received on-link-init callback for request {result.requestId}")

    try:
        # Store link initialization result
        link_init_record = {
            "requestId": str(result.requestId),
            "transactionId": str(result.transactionId),
            "timestamp": result.timestamp,
            "status": "OTP_SENT" if result.link else "FAILED",
            "linkReference": result.link.dict() if result.link else None,
            "error": result.error.dict() if result.error else None,
            "updated_at": datetime.now()
        }

        # Update or insert link request record
        await db.link_requests.update_one(
            {"requestId": str(result.requestId)},
            {"$set": link_init_record},
            upsert=True
        )

        if result.link:
            logger.info(f"Link init successful: ref={result.link.referenceNumber}, auth={result.link.authenticationType}")
            if result.link.meta and result.link.meta.communicationHint:
                logger.info(f"OTP sent to: {result.link.meta.communicationHint}")
        else:
            logger.warning(f"Link init failed: {result.error.message if result.error else 'Unknown error'}")

        return AcknowledgementResponse()

    except Exception as e:
        logger.error(f"Error processing on-link-init callback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/links/link/on-confirm")
async def on_link_confirm_callback(
    result: LinkConfirmResult,
    db = Depends(get_database)
):
    """
    Callback from Gateway after link confirmation (OTP verified).

    This callback confirms that patient identity has been linked
    with care contexts successfully.

    Args:
        result: Link confirmation result
        db: Database connection

    Returns:
        Acknowledgement
    """
    logger.info(f"Received on-link-confirm callback for request {result.requestId}")

    try:
        # Store link confirmation result
        link_confirm_record = {
            "requestId": str(result.requestId),
            "timestamp": result.timestamp,
            "status": "CONFIRMED" if result.patient else "FAILED",
            "patient": result.patient.dict() if result.patient else None,
            "error": result.error.dict() if result.error else None,
            "updated_at": datetime.now()
        }

        # Update link request record
        await db.link_requests.update_one(
            {"requestId": str(result.requestId)},
            {"$set": link_confirm_record},
            upsert=True
        )

        if result.patient:
            logger.info(f"Link confirmed for patient {result.patient.referenceNumber} with {len(result.patient.careContexts)} care contexts")

            # Store confirmed link in links collection
            link_record = {
                "patientId": result.patient.referenceNumber,
                "patientDisplay": result.patient.display,
                "careContexts": [cc.dict() for cc in result.patient.careContexts],
                "status": "ACTIVE",
                "linkedAt": datetime.now()
            }

            await db.patient_links.insert_one(link_record)

        else:
            logger.warning(f"Link confirmation failed: {result.error.message if result.error else 'Unknown error'}")

        return AcknowledgementResponse()

    except Exception as e:
        logger.error(f"Error processing on-link-confirm callback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/health-information/hip/on-request")
async def on_health_info_request_callback(
    result: HIRequestResult,
    db = Depends(get_database)
):
    """
    Callback from Gateway acknowledging HI request.

    This callback confirms that HIP's health information request
    has been acknowledged by CM/Gateway and a transaction ID has
    been created.

    Args:
        result: HI request acknowledgement
        db: Database connection

    Returns:
        Acknowledgement
    """
    logger.info(f"Received on-request callback for HI request {result.requestId}")

    try:
        # Update HI request record
        hi_request_update = {
            "timestamp": result.timestamp,
            "status": "ACKNOWLEDGED" if result.hiRequest else "FAILED",
            "transactionId": str(result.hiRequest.transactionId) if result.hiRequest else None,
            "sessionStatus": result.hiRequest.sessionStatus if result.hiRequest else None,
            "error": result.error.dict() if result.error else None,
            "updated_at": datetime.now()
        }

        await db.hi_requests.update_one(
            {"requestId": str(result.requestId)},
            {"$set": hi_request_update},
            upsert=True
        )

        if result.hiRequest:
            logger.info(f"HI request acknowledged: transaction={result.hiRequest.transactionId}, status={result.hiRequest.sessionStatus}")
        else:
            logger.warning(f"HI request failed: {result.error.message if result.error else 'Unknown error'}")

        return AcknowledgementResponse()

    except Exception as e:
        logger.error(f"Error processing on-request callback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/links/link/add-contexts", status_code=202)
async def add_care_contexts_to_link(
    request: LinkAddContextsRequest,
    db = Depends(get_database)
):
    """
    Add more care contexts to an existing patient link.

    This endpoint allows adding new care contexts (encounters, episodes)
    to an already linked patient without requiring new OTP verification.

    Args:
        request: Add contexts request
        db: Database connection

    Returns:
        202 Accepted acknowledgement
    """
    logger.info(f"Received add-contexts request {request.requestId} for patient {request.patient.referenceNumber}")

    try:
        # Verify patient link exists
        existing_link = await db.patient_links.find_one({
            "patientId": request.patient.referenceNumber,
            "status": "ACTIVE"
        })

        if not existing_link:
            logger.error(f"No active link found for patient {request.patient.referenceNumber}")

            # Send error callback to Gateway
            error_result = AddContextsResult(
                requestId=request.requestId,
                timestamp=datetime.now(),
                error=Error(code=2000, message=f"No active link found for patient {request.patient.referenceNumber}"),
                resp=RequestReference(requestId=str(request.requestId))
            )

            # TODO: Send callback to Gateway
            return {"acknowledged": True}

        # Add new care contexts to existing link
        new_care_contexts = [cc.dict() for cc in request.careContexts]

        await db.patient_links.update_one(
            {"_id": existing_link["_id"]},
            {
                "$push": {"careContexts": {"$each": new_care_contexts}},
                "$set": {"updated_at": datetime.now()}
            }
        )

        logger.info(f"Added {len(request.careContexts)} care contexts to patient link {request.patient.referenceNumber}")

        # Send success callback to Gateway
        success_result = AddContextsResult(
            requestId=request.requestId,
            timestamp=datetime.now(),
            acknowledgement={"status": "SUCCESS"},
            resp=RequestReference(requestId=str(request.requestId))
        )

        # TODO: Send callback to Gateway /v0.5/links/link/on-add-contexts

        return {"acknowledged": True, "requestId": str(request.requestId)}

    except Exception as e:
        logger.error(f"Error processing add-contexts request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/links/link/on-add-contexts")
async def on_add_contexts_callback(
    result: AddContextsResult,
    db = Depends(get_database)
):
    """
    Callback from Gateway after add-contexts operation.

    Args:
        result: Add contexts result
        db: Database connection

    Returns:
        Acknowledgement
    """
    logger.info(f"Received on-add-contexts callback for request {result.requestId}")

    try:
        # Store add-contexts result
        add_contexts_record = {
            "requestId": str(result.requestId),
            "timestamp": result.timestamp,
            "status": "SUCCESS" if result.acknowledgement else "FAILED",
            "acknowledgement": result.acknowledgement,
            "error": result.error.dict() if result.error else None,
            "updated_at": datetime.now()
        }

        await db.add_contexts_requests.update_one(
            {"requestId": str(result.requestId)},
            {"$set": add_contexts_record},
            upsert=True
        )

        if result.acknowledgement:
            logger.info(f"Add-contexts successful for request {result.requestId}")
        else:
            logger.warning(f"Add-contexts failed: {result.error.message if result.error else 'Unknown error'}")

        return AcknowledgementResponse()

    except Exception as e:
        logger.error(f"Error processing on-add-contexts callback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/links/context/notify", status_code=202)
async def notify_context_change(
    request: ContextNotifyRequest,
    db = Depends(get_database)
):
    """
    Notify about new or updated health information in a care context.

    This endpoint allows HIP to notify HIU/CM about availability of
    new health information without requiring explicit data request.

    Args:
        request: Context notification request
        db: Database connection

    Returns:
        202 Accepted acknowledgement
    """
    logger.info(f"Received context notify request {request.requestId} for care context {request.notification.careContext.referenceNumber}")

    try:
        # Store notification
        notification_record = {
            "requestId": str(request.requestId),
            "timestamp": request.timestamp,
            "careContext": request.notification.careContext.dict(),
            "hiTypes": request.notification.hiTypes,
            "date": request.notification.date,
            "period": request.notification.period,
            "status": "NOTIFIED",
            "created_at": datetime.now()
        }

        await db.context_notifications.insert_one(notification_record)

        logger.info(f"Context notification stored: {request.notification.careContext.referenceNumber} - HI types: {', '.join(request.notification.hiTypes)}")

        # Send success callback to Gateway
        success_result = ContextNotifyResult(
            requestId=request.requestId,
            timestamp=datetime.now(),
            acknowledgement={"status": "SUCCESS"},
            resp=RequestReference(requestId=str(request.requestId))
        )

        # TODO: Send callback to Gateway /v0.5/links/context/on-notify

        return {"acknowledged": True, "requestId": str(request.requestId)}

    except Exception as e:
        logger.error(f"Error processing context notify request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/links/context/on-notify")
async def on_context_notify_callback(
    result: ContextNotifyResult,
    db = Depends(get_database)
):
    """
    Callback from Gateway after context notification.

    Args:
        result: Context notification result
        db: Database connection

    Returns:
        Acknowledgement
    """
    logger.info(f"Received on-notify callback for request {result.requestId}")

    try:
        # Update notification record
        notification_update = {
            "timestamp": result.timestamp,
            "status": "ACKNOWLEDGED" if result.acknowledgement else "FAILED",
            "acknowledgement": result.acknowledgement,
            "error": result.error.dict() if result.error else None,
            "updated_at": datetime.now()
        }

        await db.context_notifications.update_one(
            {"requestId": str(result.requestId)},
            {"$set": notification_update}
        )

        if result.acknowledgement:
            logger.info(f"Context notification acknowledged for request {result.requestId}")
        else:
            logger.warning(f"Context notification failed: {result.error.message if result.error else 'Unknown error'}")

        return AcknowledgementResponse()

    except Exception as e:
        logger.error(f"Error processing on-notify callback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
