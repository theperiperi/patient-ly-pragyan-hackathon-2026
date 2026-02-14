"""
Consent Manager - Patient Actions

Handles patient consent approval/denial actions.
Simulates patient interaction with ABHA app for consent approval.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4
import logging
import httpx

from models.consent import ConsentStatus
from dependencies import get_database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v0.5", tags=["patient-actions"])


class ConsentApprovalRequest(BaseModel):
    """Patient consent approval request."""
    consentRequestId: str = Field(..., description="Consent request ID to approve")
    careContexts: Optional[List[dict]] = Field(None, description="Specific care contexts to grant access to")


class ConsentDenialRequest(BaseModel):
    """Patient consent denial request."""
    consentRequestId: str = Field(..., description="Consent request ID to deny")


@router.post("/consent-requests/{consent_request_id}/approve")
async def approve_consent_request(
    consent_request_id: str,
    request: ConsentApprovalRequest,
    db = Depends(get_database)
):
    """
    Patient approves consent request.

    This endpoint simulates patient action in ABHA app.
    In production, this would be triggered by actual patient interaction.

    Flow:
    1. Find consent request
    2. Create consent artefact
    3. Update request status to GRANTED
    4. Notify HIU via Gateway

    Args:
        consent_request_id: Consent request ID
        request: Approval request
        db: Database connection

    Returns:
        Consent artefact details
    """
    logger.info(f"Patient approving consent request {consent_request_id}")

    # Find consent request
    consent_req = await db.consent_requests.find_one({
        "consent_request_id": consent_request_id
    })

    if not consent_req:
        raise HTTPException(status_code=404, detail=f"Consent request {consent_request_id} not found")

    if consent_req["status"] != ConsentStatus.REQUESTED.value:
        raise HTTPException(
            status_code=400,
            detail=f"Consent request is in {consent_req['status']} state, cannot approve"
        )

    # Generate consent ID
    consent_id = str(uuid4())

    # Extract original request details
    original_request = consent_req["consent_request"]["consent"]

    # Build consent artefact
    consent_artefact = {
        "status": ConsentStatus.GRANTED.value,
        "consentId": consent_id,
        "consentDetail": {
            "schemaVersion": "v1.0",
            "consentId": consent_id,
            "createdAt": datetime.now().isoformat(),
            "patient": original_request["patient"],
            "careContexts": request.careContexts or original_request.get("careContexts", []),
            "purpose": original_request["purpose"],
            "hip": original_request.get("hip") or {"id": "unknown"},
            "consentManager": {"id": "sbx"},
            "hiTypes": original_request["hiTypes"],
            "permission": original_request["permission"]
        },
        "signature": f"CM_SIGNATURE_{consent_id}"  # Mock signature
    }

    # Store consent artefact
    consent_artefact_doc = {
        "consent_id": consent_id,
        "consent_request_id": consent_request_id,
        "patient_abha": consent_req["patient_abha"],
        "hiu_id": consent_req["hiu_id"],
        "hip_id": consent_req.get("hip_id") or "unknown",
        "status": ConsentStatus.GRANTED.value,
        "consent_artefact": consent_artefact,
        "created_at": datetime.now(),
        "granted_at": datetime.now(),
        "expiry_date": datetime.fromisoformat(original_request["permission"]["dataEraseAt"]),
        "revoked_at": None
    }

    await db.consent_artefacts.insert_one(consent_artefact_doc)

    # Update consent request
    await db.consent_requests.update_one(
        {"consent_request_id": consent_request_id},
        {
            "$set": {
                "status": ConsentStatus.GRANTED.value,
                "consent_id": consent_id,
                "consent_artefact": consent_artefact,
                "updated_at": datetime.now()
            }
        }
    )

    logger.info(f"Consent {consent_id} granted for request {consent_request_id}")

    # Send notification to HIU via Gateway
    notification_payload = {
        "requestId": str(uuid4()),
        "timestamp": datetime.now().isoformat(),
        "notification": consent_artefact,
        "resp": {
            "requestId": str(uuid4())
        }
    }

    # Callback to HIU's notification URL
    callback_url = consent_req.get("callback_url")
    if callback_url:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    callback_url,
                    json=notification_payload,
                    headers={"Content-Type": "application/json"}
                )
                logger.info(f"Consent notification sent to HIU: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to notify HIU: {str(e)}")

    return {
        "consentId": consent_id,
        "status": ConsentStatus.GRANTED.value,
        "message": "Consent approved successfully"
    }


@router.post("/consent-requests/{consent_request_id}/deny")
async def deny_consent_request(
    consent_request_id: str,
    request: ConsentDenialRequest,
    db = Depends(get_database)
):
    """
    Patient denies consent request.

    Args:
        consent_request_id: Consent request ID
        request: Denial request
        db: Database connection

    Returns:
        Denial confirmation
    """
    logger.info(f"Patient denying consent request {consent_request_id}")

    # Find consent request
    consent_req = await db.consent_requests.find_one({
        "consent_request_id": consent_request_id
    })

    if not consent_req:
        raise HTTPException(status_code=404, detail=f"Consent request {consent_request_id} not found")

    if consent_req["status"] != ConsentStatus.REQUESTED.value:
        raise HTTPException(
            status_code=400,
            detail=f"Consent request is in {consent_req['status']} state, cannot deny"
        )

    # Update consent request status
    await db.consent_requests.update_one(
        {"consent_request_id": consent_request_id},
        {
            "$set": {
                "status": ConsentStatus.DENIED.value,
                "updated_at": datetime.now()
            }
        }
    )

    logger.info(f"Consent request {consent_request_id} denied")

    # Notify HIU
    notification_payload = {
        "requestId": str(uuid4()),
        "timestamp": datetime.now().isoformat(),
        "notification": {
            "status": ConsentStatus.DENIED.value,
            "consentRequestId": consent_request_id
        },
        "resp": {
            "requestId": str(uuid4())
        }
    }

    callback_url = consent_req.get("callback_url")
    if callback_url:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    callback_url,
                    json=notification_payload,
                    headers={"Content-Type": "application/json"}
                )
                logger.info(f"Denial notification sent to HIU: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to notify HIU: {str(e)}")

    return {
        "consentRequestId": consent_request_id,
        "status": ConsentStatus.DENIED.value,
        "message": "Consent denied successfully"
    }


@router.get("/consent-requests/pending")
async def list_pending_consent_requests(
    patient_abha: Optional[str] = None,
    db = Depends(get_database)
):
    """
    List pending consent requests (for patient dashboard).

    Args:
        patient_abha: Optional patient ABHA to filter
        db: Database connection

    Returns:
        List of pending consent requests
    """
    query = {"status": ConsentStatus.REQUESTED.value}
    if patient_abha:
        query["patient_abha"] = patient_abha

    cursor = db.consent_requests.find(query).sort("created_at", -1).limit(50)
    consent_requests = await cursor.to_list(length=50)

    # Format for response
    pending_requests = []
    for req in consent_requests:
        pending_requests.append({
            "consentRequestId": req["consent_request_id"],
            "patientAbha": req["patient_abha"],
            "hiuId": req["hiu_id"],
            "hiuName": req["consent_request"]["consent"]["hiu"].get("name", req["hiu_id"]),
            "purpose": req["consent_request"]["consent"]["purpose"],
            "hiTypes": req["hi_types"],
            "dateRange": req["consent_request"]["consent"]["permission"]["dateRange"],
            "createdAt": req["created_at"].isoformat(),
            "expiresAt": req["expires_at"].isoformat()
        })

    return {"consentRequests": pending_requests, "total": len(pending_requests)}


@router.get("/consents/granted")
async def list_granted_consents(
    patient_abha: Optional[str] = None,
    db = Depends(get_database)
):
    """
    List granted consents (for patient dashboard).

    Args:
        patient_abha: Optional patient ABHA to filter
        db: Database connection

    Returns:
        List of granted consents
    """
    query = {"status": ConsentStatus.GRANTED.value}
    if patient_abha:
        query["patient_abha"] = patient_abha

    cursor = db.consent_artefacts.find(query).sort("granted_at", -1).limit(50)
    consents = await cursor.to_list(length=50)

    # Format for response
    granted_consents = []
    for consent in consents:
        granted_consents.append({
            "consentId": consent["consent_id"],
            "patientAbha": consent["patient_abha"],
            "hiuId": consent["hiu_id"],
            "hipId": consent["hip_id"],
            "status": consent["status"],
            "grantedAt": consent["granted_at"].isoformat(),
            "expiryDate": consent["expiry_date"].isoformat(),
            "hiTypes": consent["consent_artefact"]["consentDetail"]["hiTypes"]
        })

    return {"consents": granted_consents, "total": len(granted_consents)}
