"""
HIU Consent Management API

Handles consent request initiation and consent notifications from CM.
"""

import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Header, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

# Get database dependency
async def get_db():
    """Get database connection."""
    import database
    return database.get_database()

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Consent Management"])

class ConsentManagerPatientID(BaseModel):
    """Patient identifier at consent manager."""
    id: str = Field(..., example="hinapatel@sbx", description="Patient's health ID")

class OrganizationRepresentation(BaseModel):
    """Organization representation per ABDM spec."""
    id: str = Field(..., example="10000005", description="Organization ID")

class CareContextDefinition(BaseModel):
    """Care context definition."""
    patientReference: str = Field(..., example="hinapatel@sbx")
    careContextReference: str = Field(..., example="VISIT-001")

class UsePurpose(BaseModel):
    """Purpose of data request."""
    text: str = Field(..., example="Care Management")
    code: str = Field(..., example="CAREMGT", description="Must be valid purpose code")
    refUri: Optional[str] = Field(None, example="http://terminology.hl7.org/CodeSystem/v3-ActReason")

class RequesterIdentifier(BaseModel):
    """Requester identifier structure."""
    type: str = Field(..., example="REGNO")
    value: str = Field(..., example="MH1001")
    system: str = Field(..., example="https://www.mciindia.org")

class Requester(BaseModel):
    """Requester information."""
    name: str = Field(..., example="Dr. Manju")
    identifier: Optional[RequesterIdentifier] = None

class Permission(BaseModel):
    """Data access permission."""
    accessMode: str = Field(..., example="VIEW")
    dateRange: "DateRange" = Field(...)
    dataEraseAt: datetime = Field(..., example="2025-01-01T00:00:00.000Z")
    frequency: "Frequency" = Field(...)

class DateRange(BaseModel):
    """Date range for data access."""
    from_: datetime = Field(..., alias="from", example="2024-01-01T00:00:00.000Z")
    to: datetime = Field(..., example="2024-12-31T23:59:59.999Z")

class Frequency(BaseModel):
    """Frequency of data access."""
    unit: str = Field(..., example="HOUR")
    value: int = Field(..., example=1)
    repeats: int = Field(..., example=0)

class ConsentDetail(BaseModel):
    """Consent details for request."""
    purpose: UsePurpose
    patient: ConsentManagerPatientID
    hip: Optional[OrganizationRepresentation] = None
    careContexts: Optional[List[CareContextDefinition]] = None
    hiu: OrganizationRepresentation
    requester: Requester
    hiTypes: List[str] = Field(..., example=["DiagnosticReport", "Prescription"])
    permission: Permission

class ConsentRequest(BaseModel):
    """Consent request structure per ABDM spec."""
    requestId: UUID = Field(..., example="499a5a4a-7dda-4f20-9b67-e24589627061")
    timestamp: datetime = Field(..., example="2024-01-01T12:00:00.000Z")
    consent: ConsentDetail

class RequestReference(BaseModel):
    """Request reference for correlation."""
    requestId: UUID = Field(..., description="The requestId that was passed")

class ConsentRequestInitResponse(BaseModel):
    """Response to consent request init (callback from CM)."""
    requestId: UUID = Field(..., example="5f7a535d-a3fd-416b-b069-c97d021fbacd")
    timestamp: datetime = Field(..., example="2024-01-01T12:00:00.000Z")
    consentRequest: Optional[dict] = Field(None, description="Created consent request with ID")
    error: Optional[dict] = None
    resp: RequestReference

class ConsentArtefactReference(BaseModel):
    """Reference to consent artefact."""
    id: str = Field(..., example="f29f0e59-8388-4698-9fe6-05db67aeac46")

class ConsentNotification(BaseModel):
    """Consent notification details."""
    consentRequestId: str = Field(..., example="<consent-request-id>")
    status: str = Field(..., example="GRANTED", description="GRANTED, DENIED, EXPIRED, REVOKED")
    consentArtefacts: Optional[List[ConsentArtefactReference]] = Field(None)

class HIUConsentNotificationEvent(BaseModel):
    """Consent notification event from CM."""
    requestId: UUID = Field(..., example="5f7a535d-a3fd-416b-b069-c97d021fbacd")
    timestamp: datetime = Field(..., example="2024-01-01T12:00:00.000Z")
    notification: ConsentNotification


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/v0.5/consent-requests/init", status_code=202)
async def consent_request_init(
    request: ConsentRequest,
    authorization: str = Header(..., description="Bearer token"),
    x_cm_id: str = Header(..., alias="X-CM-ID", description="Consent Manager ID"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Create consent request to get patient data.

    HIU initiates a consent request by calling this endpoint. The request is
    forwarded to the Consent Manager, which notifies the patient.

    Args:
        request: Consent request details
        authorization: Bearer token for authentication
        x_cm_id: Consent Manager ID
        db: Database connection

    Returns:
        202 Accepted with acknowledgement
    """
    logger.info(f"Consent request init: requestId={request.requestId}, patient={request.consent.patient.id}")

    # Store consent request in database
    consent_request_doc = {
        "requestId": str(request.requestId),
        "timestamp": request.timestamp,
        "consentRequestId": None,  # Will be filled by callback
        "status": "REQUESTED",
        "purpose": request.consent.purpose.code,
        "patient": request.consent.patient.id,
        "hip": request.consent.hip.id if request.consent.hip else None,
        "hiu": request.consent.hiu.id,
        "requester": request.consent.requester.name,
        "hiTypes": request.consent.hiTypes,
        "permission": {
            "accessMode": request.consent.permission.accessMode,
            "dateRange": {
                "from": request.consent.permission.dateRange.from_,
                "to": request.consent.permission.dateRange.to
            },
            "dataEraseAt": request.consent.permission.dataEraseAt,
            "frequency": {
                "unit": request.consent.permission.frequency.unit,
                "value": request.consent.permission.frequency.value,
                "repeats": request.consent.permission.frequency.repeats
            }
        },
        "careContexts": [
            {
                "patientReference": cc.patientReference,
                "careContextReference": cc.careContextReference
            } for cc in (request.consent.careContexts or [])
        ],
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }

    await db.consent_requests.insert_one(consent_request_doc)
    logger.info(f"Stored consent request: {request.requestId}")

    # In a real implementation, forward to gateway/CM here
    # For dev kit, we simulate acceptance

    return {
        "status": "accepted",
        "message": "Consent request accepted for processing"
    }


@router.post("/v0.5/consent-requests/on-init", status_code=202)
async def consent_request_on_init(
    response: ConsentRequestInitResponse,
    authorization: str = Header(..., description="Bearer token"),
    x_hiu_id: str = Header(..., alias="X-HIU-ID", description="HIU ID"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Callback from CM with result of consent request creation.

    This callback receives the consent request ID created by CM or an error
    if the request was invalid.

    Args:
        response: Response from CM with consent request ID or error
        authorization: Bearer token
        x_hiu_id: HIU ID
        db: Database connection

    Returns:
        202 Accepted
    """
    logger.info(f"Consent request callback: requestId={response.requestId}")

    # Find original consent request
    original_request = await db.consent_requests.find_one({
        "requestId": str(response.resp.requestId)
    })

    if not original_request:
        logger.error(f"Original consent request not found: {response.resp.requestId}")
        raise HTTPException(status_code=400, detail="Original request not found")

    # Update with consent request ID from CM
    if response.consentRequest:
        consent_request_id = response.consentRequest.get("id")
        logger.info(f"Consent request created: {consent_request_id}")

        await db.consent_requests.update_one(
            {"requestId": str(response.resp.requestId)},
            {
                "$set": {
                    "consentRequestId": consent_request_id,
                    "status": "REQUESTED",
                    "updatedAt": datetime.utcnow()
                }
            }
        )
    elif response.error:
        logger.error(f"Consent request failed: {response.error}")

        await db.consent_requests.update_one(
            {"requestId": str(response.resp.requestId)},
            {
                "$set": {
                    "status": "FAILED",
                    "error": response.error,
                    "updatedAt": datetime.utcnow()
                }
            }
        )

    return {"status": "acknowledged"}


@router.post("/v0.5/consents/hiu/notify", status_code=202)
async def consent_notification(
    event: HIUConsentNotificationEvent,
    authorization: str = Header(..., description="Bearer token"),
    x_hiu_id: str = Header(..., alias="X-HIU-ID", description="HIU ID"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Receive consent notification from CM.

    HIU receives notifications about consent status changes:
    - GRANTED: Consent approved by patient with artefact IDs
    - DENIED: Consent denied by patient
    - EXPIRED: Consent request expired
    - REVOKED: Consent was revoked by patient

    Args:
        event: Consent notification event
        authorization: Bearer token
        x_hiu_id: HIU ID
        db: Database connection

    Returns:
        202 Accepted
    """
    logger.info(f"Consent notification: consentRequestId={event.notification.consentRequestId}, status={event.notification.status}")

    # Update consent request status
    update_data = {
        "status": event.notification.status,
        "updatedAt": datetime.utcnow(),
        "notificationTimestamp": event.timestamp
    }

    if event.notification.consentArtefacts:
        artefact_ids = [ca.id for ca in event.notification.consentArtefacts]
        update_data["consentArtefactIds"] = artefact_ids
        logger.info(f"Consent artefacts: {artefact_ids}")

        # Store consent artefacts for later data requests
        for artefact_id in artefact_ids:
            await db.consent_artefacts.update_one(
                {"artefactId": artefact_id},
                {
                    "$set": {
                        "artefactId": artefact_id,
                        "consentRequestId": event.notification.consentRequestId,
                        "status": event.notification.status,
                        "grantedAt": datetime.utcnow() if event.notification.status == "GRANTED" else None,
                        "revokedAt": datetime.utcnow() if event.notification.status == "REVOKED" else None,
                        "createdAt": datetime.utcnow(),
                        "updatedAt": datetime.utcnow()
                    }
                },
                upsert=True
            )

    await db.consent_requests.update_one(
        {"consentRequestId": event.notification.consentRequestId},
        {"$set": update_data}
    )

    logger.info(f"Updated consent request {event.notification.consentRequestId} to {event.notification.status}")

    return {"status": "acknowledged"}
