"""
HIU Health Information Data Collection API

Handles health information requests and data reception from HIP via CM.
"""

import logging
from datetime import datetime
from typing import Optional
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
router = APIRouter(tags=["Health Information"])


# ============================================================================
# Pydantic Models (matching ABDM gateway.yaml schema)
# ============================================================================

class KeyObject(BaseModel):
    """Encryption key object."""
    expiry: datetime = Field(..., example="2025-01-01T00:00:00.000Z")
    parameters: str = Field(..., example="Curve25519/32byte random key")
    keyValue: str = Field(..., description="Base64 encoded public key")

class KeyMaterial(BaseModel):
    """Encryption key material for secure data transfer."""
    cryptoAlg: str = Field(..., example="ECDH", description="Encryption algorithm")
    curve: str = Field(..., example="Curve25519", description="Elliptic curve")
    dhPublicKey: KeyObject = Field(..., description="Diffie-Hellman public key")
    nonce: str = Field(..., example="3fa85f64-5717-4562-b3fc-2c963f66afa6", description="32 byte string")

class ConsentReference(BaseModel):
    """Consent artefact reference."""
    id: str = Field(..., description="Consent artefact ID")

class DateRange(BaseModel):
    """Date range for data request."""
    from_: datetime = Field(..., alias="from", example="2024-01-01T00:00:00.000Z")
    to: datetime = Field(..., example="2024-12-31T23:59:59.999Z")

class HIRequestDetail(BaseModel):
    """Health information request details."""
    consent: ConsentReference
    dateRange: DateRange
    dataPushUrl: str = Field(..., example="https://hiu.example.com/data-push")
    keyMaterial: KeyMaterial

class HIRequest(BaseModel):
    """Health information request to CM."""
    requestId: UUID = Field(..., example="499a5a4a-7dda-4f20-9b67-e24589627061")
    timestamp: datetime = Field(..., example="2024-01-01T12:00:00.000Z")
    hiRequest: HIRequestDetail

class RequestReference(BaseModel):
    """Request reference for correlation."""
    requestId: UUID = Field(..., description="The requestId that was passed")

class HIRequestContext(BaseModel):
    """Health information request context."""
    transactionId: UUID = Field(..., description="Transaction ID from CM")
    sessionStatus: str = Field(..., example="ACKNOWLEDGED", description="Session status")

class Error(BaseModel):
    """Error details."""
    code: int = Field(..., example=1000)
    message: str = Field(..., example="Invalid consent artefact id")

class HIUHealthInformationRequestResponse(BaseModel):
    """Response from CM about HI request (callback)."""
    requestId: UUID = Field(..., example="5f7a535d-a3fd-416b-b069-c97d021fbacd")
    timestamp: datetime = Field(..., example="2024-01-01T12:00:00.000Z")
    hiRequest: Optional[HIRequestContext] = None
    error: Optional[Error] = None
    resp: RequestReference


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/v0.5/health-information/cm/request", status_code=202)
async def health_information_request(
    request: HIRequest,
    authorization: str = Header(..., description="Bearer token"),
    x_cm_id: str = Header(..., alias="X-CM-ID", description="Consent Manager ID"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Request health information from HIP via CM.

    HIU requests health data against a valid consent artefact ID. CM validates
    the consent and forwards request to HIP if valid.

    Args:
        request: Health information request details
        authorization: Bearer token
        x_cm_id: Consent Manager ID
        db: Database connection

    Returns:
        202 Accepted with acknowledgement
    """
    logger.info(f"HI request: requestId={request.requestId}, consentId={request.hiRequest.consent.id}")

    # Verify consent artefact exists and is valid
    consent = await db.consent_artefacts.find_one({
        "artefactId": request.hiRequest.consent.id
    })

    if not consent:
        logger.error(f"Consent artefact not found: {request.hiRequest.consent.id}")
        # In production, this would be handled by CM callback with error
        # For dev kit, we store it anyway

    # Store HI request
    hi_request_doc = {
        "requestId": str(request.requestId),
        "timestamp": request.timestamp,
        "consentId": request.hiRequest.consent.id,
        "dateRange": {
            "from": request.hiRequest.dateRange.from_,
            "to": request.hiRequest.dateRange.to
        },
        "dataPushUrl": request.hiRequest.dataPushUrl,
        "keyMaterial": {
            "cryptoAlg": request.hiRequest.keyMaterial.cryptoAlg,
            "curve": request.hiRequest.keyMaterial.curve,
            "dhPublicKey": {
                "expiry": request.hiRequest.keyMaterial.dhPublicKey.expiry,
                "parameters": request.hiRequest.keyMaterial.dhPublicKey.parameters,
                "keyValue": request.hiRequest.keyMaterial.dhPublicKey.keyValue
            },
            "nonce": request.hiRequest.keyMaterial.nonce
        },
        "status": "REQUESTED",
        "transactionId": None,  # Will be filled by callback
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }

    await db.hi_requests.insert_one(hi_request_doc)
    logger.info(f"Stored HI request: {request.requestId}")

    # In real implementation, forward to gateway/CM here
    # For dev kit, we simulate acceptance

    return {
        "status": "accepted",
        "message": "Health information request accepted for processing"
    }


@router.post("/v0.5/health-information/cm/on-request", status_code=202)
async def health_information_on_request(
    response: HIUHealthInformationRequestResponse,
    authorization: str = Header(..., description="Bearer token"),
    x_hiu_id: str = Header(..., alias="X-HIU-ID", description="HIU ID"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Callback from CM with result of HI request.

    CM validates the health information request against consent and responds with
    either a transaction ID (if valid) or an error.

    Possible errors:
    - Invalid consent artefact ID
    - Consent has expired
    - Date ranges are invalid

    Args:
        response: Response from CM with transaction ID or error
        authorization: Bearer token
        x_hiu_id: HIU ID
        db: Database connection

    Returns:
        202 Accepted
    """
    logger.info(f"HI request callback: requestId={response.requestId}")

    # Find original HI request
    original_request = await db.hi_requests.find_one({
        "requestId": str(response.resp.requestId)
    })

    if not original_request:
        logger.error(f"Original HI request not found: {response.resp.requestId}")
        raise HTTPException(status_code=400, detail="Original request not found")

    # Update with transaction ID or error
    if response.hiRequest:
        transaction_id = str(response.hiRequest.transactionId)
        session_status = response.hiRequest.sessionStatus
        logger.info(f"HI request acknowledged: transactionId={transaction_id}, status={session_status}")

        await db.hi_requests.update_one(
            {"requestId": str(response.resp.requestId)},
            {
                "$set": {
                    "transactionId": transaction_id,
                    "sessionStatus": session_status,
                    "status": "ACKNOWLEDGED",
                    "updatedAt": datetime.utcnow()
                }
            }
        )

        # Store transaction for tracking data push
        await db.hi_transactions.insert_one({
            "transactionId": transaction_id,
            "requestId": str(response.resp.requestId),
            "status": session_status,
            "dataReceived": False,
            "bundles": [],
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        })

    elif response.error:
        logger.error(f"HI request failed: {response.error.message}")

        await db.hi_requests.update_one(
            {"requestId": str(response.resp.requestId)},
            {
                "$set": {
                    "status": "FAILED",
                    "error": {
                        "code": response.error.code,
                        "message": response.error.message
                    },
                    "updatedAt": datetime.utcnow()
                }
            }
        )

    return {"status": "acknowledged"}
