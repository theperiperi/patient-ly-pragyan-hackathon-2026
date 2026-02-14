"""
HIP Care Context Linking Handler

Implements care context linking logic:
- Generate OTP for patient authentication
- Verify OTP and link care contexts
- Store linked care contexts for health information requests
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
from uuid import UUID, uuid4
import logging
import httpx
import random
import string

from main import get_database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v0.5", tags=["care-context-linking"])


# Models (matching gateway schema)

class CareContext(BaseModel):
    """Care context reference."""
    referenceNumber: str


class PatientLinkPatient(BaseModel):
    """Patient details for link request."""
    id: str
    referenceNumber: str
    careContexts: List[CareContext]


class PatientLinkReferenceRequest(BaseModel):
    """Link init request from Gateway."""
    requestId: UUID
    timestamp: datetime
    transactionId: UUID
    patient: PatientLinkPatient


class Meta(BaseModel):
    """OTP communication metadata."""
    communicationMedium: Optional[str] = None
    communicationHint: Optional[str] = None
    communicationExpiry: Optional[str] = None


class LinkReference(BaseModel):
    """Link reference with auth details."""
    referenceNumber: str
    authenticationType: str
    meta: Optional[Meta] = None


class RequestReference(BaseModel):
    """Request reference."""
    requestId: str


class Error(BaseModel):
    """Error details."""
    code: int
    message: str


class PatientLinkReferenceResult(BaseModel):
    """Link init result."""
    requestId: UUID
    timestamp: datetime
    transactionId: UUID
    link: Optional[LinkReference] = None
    error: Optional[Error] = None
    resp: RequestReference


class LinkConfirmation(BaseModel):
    """Link confirmation with OTP."""
    linkRefNumber: str
    token: str


class LinkConfirmationRequest(BaseModel):
    """Link confirmation request."""
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
    """Link confirmation result."""
    requestId: UUID
    timestamp: datetime
    patient: Optional[PatientResult] = None
    error: Optional[Error] = None
    resp: RequestReference


# OTP Management

def generate_otp(length: int = 6) -> str:
    """Generate random numeric OTP."""
    return ''.join(random.choices(string.digits, k=length))


async def store_otp(db, link_ref: str, otp: str, patient_id: str, care_contexts: List[str], expiry_minutes: int = 10):
    """Store OTP in database with expiry."""
    otp_collection = db.otp_store

    await otp_collection.insert_one({
        "link_ref": link_ref,
        "otp": otp,
        "patient_id": patient_id,
        "care_contexts": care_contexts,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(minutes=expiry_minutes),
        "verified": False
    })

    logger.info(f"Stored OTP for link_ref {link_ref}, expires in {expiry_minutes} minutes")


async def verify_otp(db, link_ref: str, otp: str) -> Optional[dict]:
    """Verify OTP and return stored data."""
    otp_collection = db.otp_store

    otp_record = await otp_collection.find_one({
        "link_ref": link_ref,
        "otp": otp,
        "verified": False
    })

    if not otp_record:
        logger.warning(f"OTP not found or already used for link_ref {link_ref}")
        return None

    # Check expiry
    if datetime.now() > otp_record["expires_at"]:
        logger.warning(f"OTP expired for link_ref {link_ref}")
        return None

    # Mark as verified
    await otp_collection.update_one(
        {"_id": otp_record["_id"]},
        {"$set": {"verified": True, "verified_at": datetime.now()}}
    )

    logger.info(f"OTP verified successfully for link_ref {link_ref}")
    return otp_record


async def link_care_contexts(db, patient_id: str, cm_patient_id: str, care_context_refs: List[str]):
    """Store linked care contexts for future HI requests."""
    links_collection = db.care_context_links

    # Store each care context link
    for cc_ref in care_context_refs:
        await links_collection.update_one(
            {
                "patient_id": patient_id,
                "care_context_ref": cc_ref,
                "cm_patient_id": cm_patient_id
            },
            {
                "$set": {
                    "patient_id": patient_id,
                    "care_context_ref": cc_ref,
                    "cm_patient_id": cm_patient_id,
                    "linked_at": datetime.now(),
                    "status": "active"
                }
            },
            upsert=True
        )

    logger.info(f"Linked {len(care_context_refs)} care contexts for patient {patient_id}")


async def get_patient_phone(db, patient_id: str) -> Optional[str]:
    """Get patient phone number for OTP hint."""
    patients_collection = db.patients

    patient = await patients_collection.find_one({"abha_number": patient_id})

    if patient and "telecom" in patient:
        for telecom in patient["telecom"]:
            if telecom.get("system") == "phone":
                phone = telecom.get("value", "")
                # Mask phone: +91******7890
                if len(phone) > 4:
                    return f"{phone[:3]}******{phone[-4:]}"

    return None


# API Endpoints

@router.post("/links/link/init")
async def init_link(
    request: PatientLinkReferenceRequest,
    db = Depends(get_database)
):
    """
    Initialize care context linking with OTP.

    Flow:
    1. Validate patient and care contexts exist
    2. Generate OTP
    3. Store OTP with expiry
    4. Simulate sending OTP to patient (log only)
    5. Callback to Gateway with link reference

    Args:
        request: Link initialization request
        db: Database connection

    Returns:
        Acknowledgement (callback sent asynchronously)
    """
    logger.info(f"Processing link init request {request.requestId} for patient {request.patient.referenceNumber}")

    # Validate patient exists
    patients_collection = db.patients
    patient = await patients_collection.find_one({"abha_number": request.patient.referenceNumber})

    if not patient:
        # Patient not found
        result = PatientLinkReferenceResult(
            requestId=request.requestId,
            timestamp=datetime.now(),
            transactionId=request.transactionId,
            error=Error(code=1000, message=f"Patient not found: {request.patient.referenceNumber}"),
            resp=RequestReference(requestId=str(request.requestId))
        )
    else:
        # Generate OTP
        otp = generate_otp(6)
        link_ref = f"LINK-{uuid4().hex[:12].upper()}"

        # Store OTP
        care_context_refs = [cc.referenceNumber for cc in request.patient.careContexts]
        await store_otp(
            db,
            link_ref=link_ref,
            otp=otp,
            patient_id=request.patient.referenceNumber,
            care_contexts=care_context_refs,
            expiry_minutes=10
        )

        # Simulate sending OTP (in production, send via SMS/email)
        phone_hint = await get_patient_phone(db, request.patient.referenceNumber)
        logger.info(f"🔐 OTP for patient {request.patient.referenceNumber}: {otp} (link_ref: {link_ref})")

        # Prepare result
        expiry = (datetime.now() + timedelta(minutes=10)).isoformat() + "Z"

        result = PatientLinkReferenceResult(
            requestId=request.requestId,
            timestamp=datetime.now(),
            transactionId=request.transactionId,
            link=LinkReference(
                referenceNumber=link_ref,
                authenticationType="DIRECT",
                meta=Meta(
                    communicationMedium="MOBILE" if phone_hint else None,
                    communicationHint=phone_hint,
                    communicationExpiry=expiry
                )
            ),
            resp=RequestReference(requestId=str(request.requestId))
        )

    # Callback to Gateway
    gateway_url = "http://gateway:8090/v0.5/links/link/on-init"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                gateway_url,
                json=result.dict(by_alias=True),
                timeout=10.0
            )

            if response.status_code == 200:
                logger.info(f"Link init result sent to Gateway for request {request.requestId}")
            else:
                logger.error(f"Failed to send link init result to Gateway: {response.status_code}")

    except Exception as e:
        logger.error(f"Error sending callback to Gateway: {str(e)}")

    return {"acknowledged": True}


@router.post("/links/link/confirm")
async def confirm_link(
    request: LinkConfirmationRequest,
    db = Depends(get_database)
):
    """
    Confirm care context linking with OTP verification.

    Flow:
    1. Verify OTP
    2. If valid, link care contexts to patient ABHA
    3. Callback to Gateway with success/error

    Args:
        request: Link confirmation request with OTP
        db: Database connection

    Returns:
        Acknowledgement (callback sent asynchronously)
    """
    logger.info(f"Processing link confirm request {request.requestId} for linkRef {request.confirmation.linkRefNumber}")

    # Verify OTP
    otp_record = await verify_otp(
        db,
        request.confirmation.linkRefNumber,
        request.confirmation.token
    )

    if not otp_record:
        # Invalid or expired OTP
        result = PatientLinkResult(
            requestId=request.requestId,
            timestamp=datetime.now(),
            error=Error(code=1000, message="Invalid or expired OTP"),
            resp=RequestReference(requestId=str(request.requestId))
        )
    else:
        # OTP valid, link care contexts
        patient_id = otp_record["patient_id"]
        care_contexts = otp_record["care_contexts"]

        # Get CM patient ID (from original request, stored in OTP)
        # In production, this would be passed through the confirmation request
        cm_patient_id = patient_id + "@sbx"  # Simplified for demo

        await link_care_contexts(db, patient_id, cm_patient_id, care_contexts)

        # Get patient details and care context display names
        patients_collection = db.patients
        patient = await patients_collection.find_one({"abha_number": patient_id})

        display_name = patient_id
        if patient and "name" in patient:
            name_obj = patient["name"][0] if isinstance(patient["name"], list) else patient["name"]
            given = name_obj.get("given", [])
            family = name_obj.get("family", "")
            display_name = f"{' '.join(given)} {family}"

        # Get care context representations
        bundles_collection = db.fhir_bundles
        cc_representations = []

        for cc_ref in care_contexts:
            bundle = await bundles_collection.find_one({"_id": cc_ref})
            if bundle:
                bundle_type = bundle.get("bundle_type", "Unknown")
                created_at = bundle.get("created_at", datetime.now())
                cc_representations.append(CareContextRepresentation(
                    referenceNumber=cc_ref,
                    display=f"{bundle_type} - {created_at.strftime('%Y-%m-%d')}"
                ))

        result = PatientLinkResult(
            requestId=request.requestId,
            timestamp=datetime.now(),
            patient=PatientResult(
                referenceNumber=patient_id,
                display=display_name,
                careContexts=cc_representations
            ),
            resp=RequestReference(requestId=str(request.requestId))
        )

        logger.info(f"Successfully linked {len(care_contexts)} care contexts for patient {patient_id}")

    # Callback to Gateway
    gateway_url = "http://gateway:8090/v0.5/links/link/on-confirm"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                gateway_url,
                json=result.dict(by_alias=True),
                timeout=10.0
            )

            if response.status_code == 200:
                logger.info(f"Link confirm result sent to Gateway for request {request.requestId}")
            else:
                logger.error(f"Failed to send link confirm result to Gateway: {response.status_code}")

    except Exception as e:
        logger.error(f"Error sending callback to Gateway: {str(e)}")

    return {"acknowledged": True}
