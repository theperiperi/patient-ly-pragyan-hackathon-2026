"""
Consent Manager - Consent Request Handling

Handles consent request lifecycle:
1. Receive consent request from Gateway
2. Store and validate request
3. Generate consent request ID
4. Callback to HIU via Gateway
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
from uuid import UUID, uuid4
import logging
import httpx

from models.consent import (
    ConsentRequest, ConsentRequestResponse, ConsentStatus,
    ConsentRequestDocument, ConsentArtefactDocument,
    ConsentArtefact, ConsentArtefactDetail
)
from dependencies import get_database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v0.5", tags=["consent-requests"])


class ConsentRequestStatusRequest(BaseModel):
    """Request for consent status."""
    requestId: UUID
    timestamp: datetime
    consentRequestId: UUID


class ConsentRequestStatusResponse(BaseModel):
    """Response with consent request status."""
    requestId: UUID
    timestamp: datetime
    consentRequest: dict


class ConsentFetchRequest(BaseModel):
    """Request to fetch consent artefact."""
    requestId: UUID
    timestamp: datetime
    consentId: UUID


@router.post("/consent-requests/on-init")
async def on_init_consent_request(
    request: ConsentRequest,
    background_tasks: BackgroundTasks,
    db = Depends(get_database)
):
    """
    Handle consent request from Gateway.

    Flow:
    1. Receive consent request from Gateway
    2. Validate and store request
    3. Generate consent request ID
    4. Callback to HIU via Gateway with consent request ID

    Args:
        request: Consent request
        background_tasks: Background tasks
        db: Database connection

    Returns:
        Acknowledgement
    """
    logger.info(f"Received consent request {request.requestId} for patient {request.consent.patient.id}")

    # Extract patient ABHA
    patient_abha = request.consent.patient.id.split("@")[0]

    # Generate consent request ID
    consent_request_id = str(uuid4())

    # Calculate expiry (7 days from now)
    expires_at = datetime.now() + timedelta(days=7)

    # Create consent request document
    consent_doc = {
        "request_id": str(request.requestId),
        "consent_request_id": consent_request_id,
        "patient_abha": patient_abha,
        "hiu_id": request.consent.hiu.id,
        "hip_id": request.consent.hip.id if request.consent.hip else None,
        "purpose_code": request.consent.purpose.code,
        "hi_types": request.consent.hiTypes,
        "status": ConsentStatus.REQUESTED.value,
        "consent_request": request.dict(by_alias=True),
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "expires_at": expires_at,
        "consent_id": None,
        "consent_artefact": None,
        "callback_url": request.consent.consentNotificationUrl
    }

    # Store in database
    await db.consent_requests.insert_one(consent_doc)
    logger.info(f"Stored consent request {consent_request_id}")

    # Prepare callback response
    callback_response = {
        "requestId": str(request.requestId),
        "timestamp": datetime.now().isoformat(),
        "consentRequest": {
            "id": consent_request_id
        },
        "resp": {
            "requestId": str(uuid4())
        }
    }

    # Callback to Gateway (which will forward to HIU)
    background_tasks.add_task(
        callback_to_gateway,
        endpoint="/v0.5/consent-requests/on-init",
        payload=callback_response,
        request_id=str(request.requestId)
    )

    return {"acknowledged": True, "consentRequestId": consent_request_id}


@router.post("/consent-requests/status")
async def get_consent_request_status(
    request: ConsentRequestStatusRequest,
    background_tasks: BackgroundTasks,
    db = Depends(get_database)
):
    """
    Get status of consent request.

    Args:
        request: Status request
        background_tasks: Background tasks
        db: Database connection

    Returns:
        Acknowledgement
    """
    logger.info(f"Status request for consent request {request.consentRequestId}")

    # Find consent request
    consent_req = await db.consent_requests.find_one({
        "consent_request_id": str(request.consentRequestId)
    })

    if not consent_req:
        # Return error callback
        error_response = {
            "requestId": str(request.requestId),
            "timestamp": datetime.now().isoformat(),
            "error": {
                "code": 1000,
                "message": f"Consent request {request.consentRequestId} not found"
            },
            "resp": {
                "requestId": str(uuid4())
            }
        }

        background_tasks.add_task(
            callback_to_gateway,
            endpoint="/v0.5/consent-requests/on-status",
            payload=error_response,
            request_id=str(request.requestId)
        )

        return {"acknowledged": True}

    # Prepare status response
    status_response = {
        "requestId": str(request.requestId),
        "timestamp": datetime.now().isoformat(),
        "consentRequest": {
            "id": consent_req["consent_request_id"],
            "status": consent_req["status"],
            "createdAt": consent_req["created_at"].isoformat(),
            "purpose": consent_req["consent_request"]["consent"]["purpose"],
            "patient": consent_req["consent_request"]["consent"]["patient"],
            "hiu": consent_req["consent_request"]["consent"]["hiu"],
            "hiTypes": consent_req["hi_types"],
            "permission": consent_req["consent_request"]["consent"]["permission"]
        },
        "resp": {
            "requestId": str(uuid4())
        }
    }

    # Callback to Gateway
    background_tasks.add_task(
        callback_to_gateway,
        endpoint="/v0.5/consent-requests/on-status",
        payload=status_response,
        request_id=str(request.requestId)
    )

    return {"acknowledged": True}


@router.post("/consents/fetch")
async def fetch_consent_artefact(
    request: ConsentFetchRequest,
    background_tasks: BackgroundTasks,
    db = Depends(get_database)
):
    """
    Fetch consent artefact by consent ID.

    Args:
        request: Fetch request
        background_tasks: Background tasks
        db: Database connection

    Returns:
        Acknowledgement
    """
    logger.info(f"Fetch request for consent {request.consentId}")

    # Find consent artefact
    consent = await db.consent_artefacts.find_one({
        "consent_id": str(request.consentId)
    })

    if not consent:
        # Return error
        error_response = {
            "requestId": str(request.requestId),
            "timestamp": datetime.now().isoformat(),
            "error": {
                "code": 1001,
                "message": f"Consent {request.consentId} not found"
            },
            "resp": {
                "requestId": str(uuid4())
            }
        }

        background_tasks.add_task(
            callback_to_gateway,
            endpoint="/v0.5/consents/on-fetch",
            payload=error_response,
            request_id=str(request.requestId)
        )

        return {"acknowledged": True}

    # Return consent artefact
    fetch_response = {
        "requestId": str(request.requestId),
        "timestamp": datetime.now().isoformat(),
        "consent": consent["consent_artefact"],
        "resp": {
            "requestId": str(uuid4())
        }
    }

    # Callback to Gateway
    background_tasks.add_task(
        callback_to_gateway,
        endpoint="/v0.5/consents/on-fetch",
        payload=fetch_response,
        request_id=str(request.requestId)
    )

    return {"acknowledged": True}


async def callback_to_gateway(endpoint: str, payload: dict, request_id: str):
    """
    Send callback to Gateway.

    Args:
        endpoint: Gateway endpoint
        payload: Callback payload
        request_id: Request ID for logging
    """
    gateway_url = "http://gateway:8090"
    full_url = f"{gateway_url}{endpoint}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                full_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            logger.info(f"Callback {request_id} sent to Gateway: {response.status_code}")
    except Exception as e:
        logger.error(f"Failed to callback to Gateway: {str(e)}")
