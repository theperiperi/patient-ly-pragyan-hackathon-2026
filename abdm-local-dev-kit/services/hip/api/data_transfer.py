"""
HIP Health Information Data Transfer Handler

Implements health information retrieval and transfer:
- Validate consent artefact
- Retrieve FHIR bundles for linked care contexts
- Encrypt data (simulated)
- Push to HIU's dataPushUrl
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4
import logging
import httpx
import base64
import json

from main import get_database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v0.5", tags=["health-information"])


# Models (matching gateway schema)

class DateRange(BaseModel):
    """Date range for health information."""
    from_date: datetime = Field(..., alias="from")
    to_date: datetime = Field(..., alias="to")

    class Config:
        populate_by_name = True


class Consent(BaseModel):
    """Consent reference."""
    id: str


class KeyObject(BaseModel):
    """Public key object."""
    expiry: datetime
    parameters: str
    keyValue: str


class KeyMaterial(BaseModel):
    """Encryption key material."""
    cryptoAlg: str
    curve: str
    dhPublicKey: KeyObject
    nonce: str


class HIPHIRequestDetail(BaseModel):
    """HI request details."""
    consent: Consent
    dateRange: DateRange
    dataPushUrl: str
    keyMaterial: KeyMaterial


class HIPHIRequest(BaseModel):
    """Health information request from Gateway."""
    requestId: UUID
    timestamp: datetime
    transactionId: UUID
    hiRequest: HIPHIRequestDetail


class RequestReference(BaseModel):
    """Request reference."""
    requestId: str


class Error(BaseModel):
    """Error details."""
    code: int
    message: str


# Data Retrieval Functions

async def get_consent_artefact(db, consent_id: str) -> Optional[dict]:
    """Retrieve consent artefact from database."""
    consents_collection = db.consent_artefacts

    consent = await consents_collection.find_one({"consent_id": consent_id})

    if not consent:
        logger.warning(f"Consent artefact not found: {consent_id}")
        return None

    # Check if consent is valid (status=GRANTED, not expired)
    if consent.get("status") != "GRANTED":
        logger.warning(f"Consent not granted: {consent_id}")
        return None

    # Check expiry
    permission = consent.get("permission", {})
    data_erase_at = permission.get("dataEraseAt")
    if data_erase_at and isinstance(data_erase_at, datetime) and datetime.now() > data_erase_at:
        logger.warning(f"Consent expired: {consent_id}")
        return None

    return consent


async def get_linked_care_contexts(db, consent_artefact: dict) -> List[str]:
    """Extract care context references from consent artefact."""
    care_contexts = consent_artefact.get("careContexts", [])

    # Extract care context reference numbers
    cc_refs = []
    for cc in care_contexts:
        if isinstance(cc, dict):
            ref = cc.get("careContextReference") or cc.get("referenceNumber")
            if ref:
                cc_refs.append(ref)
        elif isinstance(cc, str):
            cc_refs.append(cc)

    logger.info(f"Found {len(cc_refs)} care contexts in consent")
    return cc_refs


async def retrieve_fhir_bundles(
    db,
    care_context_refs: List[str],
    date_range: DateRange,
    hi_types: Optional[List[str]] = None
) -> List[dict]:
    """Retrieve FHIR bundles for specified care contexts."""
    bundles_collection = db.fhir_bundles

    bundles = []

    for cc_ref in care_context_refs:
        # Build query
        query = {"_id": cc_ref}

        # Add date range filter if bundle has created_at
        if date_range:
            query["created_at"] = {
                "$gte": date_range.from_date,
                "$lte": date_range.to_date
            }

        # Add HI type filter if specified
        if hi_types:
            query["bundle_type"] = {"$in": hi_types}

        bundle = await bundles_collection.find_one(query)

        if bundle:
            logger.info(f"Retrieved bundle {cc_ref}: {bundle.get('bundle_type')}")
            bundles.append(bundle)
        else:
            logger.warning(f"Bundle not found for care context {cc_ref}")

    logger.info(f"Retrieved {len(bundles)} FHIR bundles")
    return bundles


def encrypt_data(data: dict, key_material: KeyMaterial) -> dict:
    """
    Encrypt FHIR bundle data (SIMULATED).

    In production, this would:
    1. Use ECDH with HIP private key + HIU public key → shared secret
    2. Derive encryption key from shared secret
    3. Encrypt FHIR bundle using AES-256-GCM
    4. Return encrypted data + metadata

    For development, we base64 encode to simulate encryption.
    """
    # Simulate encryption by base64 encoding
    json_data = json.dumps(data)
    encrypted_bytes = json_data.encode('utf-8')
    encrypted_b64 = base64.b64encode(encrypted_bytes).decode('utf-8')

    return {
        "encryptedData": encrypted_b64,
        "keyMaterial": {
            "cryptoAlg": key_material.cryptoAlg,
            "curve": key_material.curve,
            "nonce": key_material.nonce
        }
    }


async def push_data_to_hiu(
    data_push_url: str,
    transaction_id: UUID,
    encrypted_bundles: List[dict]
):
    """Push encrypted health information to HIU."""
    payload = {
        "transactionId": str(transaction_id),
        "timestamp": datetime.now().isoformat(),
        "entries": encrypted_bundles
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                data_push_url,
                json=payload,
                timeout=30.0
            )

            if response.status_code in [200, 202]:
                logger.info(f"Successfully pushed {len(encrypted_bundles)} bundles to HIU")
                return True
            else:
                logger.error(f"Failed to push data to HIU: {response.status_code}")
                return False

    except Exception as e:
        logger.error(f"Error pushing data to HIU: {str(e)}")
        return False


# API Endpoints

@router.post("/health-information/hip/request")
async def request_health_information(
    request: HIPHIRequest,
    db = Depends(get_database)
):
    """
    Process health information request from CM/Gateway.

    Flow:
    1. Validate consent artefact (exists, granted, not expired)
    2. Extract care contexts from consent
    3. Retrieve FHIR bundles for those care contexts
    4. Filter by date range and HI types
    5. Encrypt bundles (simulate)
    6. Push to HIU's dataPushUrl
    7. Callback to Gateway (on-request)

    Args:
        request: HI request from Gateway
        db: Database connection

    Returns:
        Acknowledgement
    """
    logger.info(f"Processing HI request {request.requestId} for consent {request.hiRequest.consent.id}")

    # Step 1: Validate consent
    consent_artefact = await get_consent_artefact(db, request.hiRequest.consent.id)

    if not consent_artefact:
        # Invalid consent
        logger.error(f"Invalid or expired consent: {request.hiRequest.consent.id}")

        # Callback to Gateway with error
        gateway_url = "http://gateway:8090/v0.5/health-information/hip/on-request"

        error_response = {
            "requestId": str(request.requestId),
            "timestamp": datetime.now().isoformat(),
            "error": {
                "code": 1000,
                "message": f"Invalid or expired consent: {request.hiRequest.consent.id}"
            },
            "resp": {"requestId": str(request.requestId)}
        }

        try:
            async with httpx.AsyncClient() as client:
                await client.post(gateway_url, json=error_response, timeout=10.0)
        except Exception as e:
            logger.error(f"Failed to send error callback: {str(e)}")

        return {"acknowledged": True}

    # Step 2: Extract care contexts
    care_context_refs = await get_linked_care_contexts(db, consent_artefact)

    if not care_context_refs:
        logger.warning(f"No care contexts in consent {request.hiRequest.consent.id}")

    # Step 3 & 4: Retrieve FHIR bundles
    hi_types = consent_artefact.get("hiTypes", [])

    bundles = await retrieve_fhir_bundles(
        db,
        care_context_refs,
        request.hiRequest.dateRange,
        hi_types
    )

    if not bundles:
        logger.warning(f"No bundles found for consent {request.hiRequest.consent.id}")

    # Step 5: Encrypt bundles
    encrypted_bundles = []

    for bundle in bundles:
        # Remove MongoDB _id before encryption
        bundle_copy = dict(bundle)
        if "_id" in bundle_copy:
            del bundle_copy["_id"]
        if "created_at" in bundle_copy:
            bundle_copy["created_at"] = bundle_copy["created_at"].isoformat()

        encrypted = encrypt_data(bundle_copy, request.hiRequest.keyMaterial)

        encrypted_bundles.append({
            "careContextReference": bundle.get("_id"),
            "bundleType": bundle.get("bundle_type"),
            "content": encrypted
        })

    # Step 6: Push to HIU
    push_success = await push_data_to_hiu(
        request.hiRequest.dataPushUrl,
        request.transactionId,
        encrypted_bundles
    )

    # Step 7: Callback to Gateway
    gateway_url = "http://gateway:8090/v0.5/health-information/hip/on-request"

    callback_response = {
        "requestId": str(request.requestId),
        "timestamp": datetime.now().isoformat(),
        "hiRequest": {
            "transactionId": str(request.transactionId),
            "sessionStatus": "TRANSFERRED" if push_success else "FAILED"
        },
        "resp": {"requestId": str(request.requestId)}
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                gateway_url,
                json=callback_response,
                timeout=10.0
            )

            if response.status_code == 200:
                logger.info(f"Callback sent to Gateway for request {request.requestId}")
            else:
                logger.error(f"Failed to send callback to Gateway: {response.status_code}")

    except Exception as e:
        logger.error(f"Error sending callback to Gateway: {str(e)}")

    logger.info(f"HI request {request.requestId} processed: {len(encrypted_bundles)} bundles transferred")

    return {"acknowledged": True}
