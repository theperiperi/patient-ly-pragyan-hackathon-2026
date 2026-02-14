"""
HIP Patient Discovery Handler

Implements patient discovery logic:
- Fuzzy matching by demographics (name, gender, yearOfBirth)
- Exact matching by identifiers (ABHA, mobile, MR)
- Returns matched patient with care contexts
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4
import logging
import httpx

from main import get_database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v0.5", tags=["patient-discovery"])


# Models (matching gateway schema)

class Identifier(BaseModel):
    """Patient identifier."""
    type: str
    value: str


class PatientDiscoveryPatient(BaseModel):
    """Patient details for discovery."""
    id: str
    verifiedIdentifiers: List[Identifier]
    unverifiedIdentifiers: Optional[List[Identifier]] = None
    name: str
    gender: str
    yearOfBirth: int


class PatientDiscoveryRequest(BaseModel):
    """Patient discovery request from Gateway."""
    requestId: UUID
    timestamp: datetime
    transactionId: UUID
    patient: PatientDiscoveryPatient


class CareContextRepresentation(BaseModel):
    """Care context representation."""
    referenceNumber: str
    display: str


class PatientRepresentation(BaseModel):
    """Matched patient representation."""
    referenceNumber: str
    display: str
    careContexts: Optional[List[CareContextRepresentation]] = None
    matchedBy: Optional[List[str]] = None


class RequestReference(BaseModel):
    """Request reference."""
    requestId: str


class Error(BaseModel):
    """Error details."""
    code: int
    message: str


class PatientDiscoveryResult(BaseModel):
    """Discovery result to send back to Gateway."""
    requestId: UUID
    timestamp: datetime
    transactionId: UUID
    patient: Optional[PatientRepresentation] = None
    error: Optional[Error] = None
    resp: RequestReference


# Patient Matching Logic

async def find_patient_by_identifiers(
    db,
    verified_identifiers: List[Identifier],
    unverified_identifiers: Optional[List[Identifier]] = None
) -> Optional[dict]:
    """
    Find patient by exact identifier match (ABHA, mobile, MR).

    Priority order:
    1. NDHM_HEALTH_NUMBER (ABHA)
    2. HEALTH_ID (ABHA @sbx format)
    3. MOBILE
    4. MR (Medical Record Number)
    """
    patients_collection = db.patients

    # Try verified identifiers first
    for identifier in verified_identifiers:
        query = None

        if identifier.type in ["NDHM_HEALTH_NUMBER", "HEALTH_ID"]:
            # Match by ABHA number
            # Remove @sbx suffix if present for matching
            abha_value = identifier.value.split("@")[0]
            query = {"abha_number": abha_value}

        elif identifier.type == "MOBILE":
            # Match by phone number
            # Normalize: remove +91, spaces, hyphens
            phone = identifier.value.replace("+91", "").replace("-", "").replace(" ", "")
            query = {"telecom": {"$elemMatch": {"value": {"$regex": f".*{phone}.*"}}}}

        elif identifier.type == "MR":
            # Match by medical record number (stored in identifier array)
            query = {"identifier": {"$elemMatch": {"value": identifier.value}}}

        if query:
            patient = await patients_collection.find_one(query)
            if patient:
                logger.info(f"Patient found by {identifier.type}: {identifier.value}")
                return patient

    # Try unverified identifiers if no match yet
    if unverified_identifiers:
        for identifier in unverified_identifiers:
            if identifier.type == "MOBILE":
                phone = identifier.value.replace("+91", "").replace("-", "").replace(" ", "")
                query = {"telecom": {"$elemMatch": {"value": {"$regex": f".*{phone}.*"}}}}
                patient = await patients_collection.find_one(query)
                if patient:
                    logger.info(f"Patient found by unverified {identifier.type}")
                    return patient

    return None


async def find_patient_by_demographics(
    db,
    name: str,
    gender: str,
    year_of_birth: int
) -> Optional[dict]:
    """
    Fuzzy match patient by demographics.

    Matching criteria:
    - Name: case-insensitive partial match
    - Gender: exact match
    - Year of birth: exact match
    """
    patients_collection = db.patients

    # Normalize name for fuzzy matching
    name_parts = name.lower().split()

    # Build regex pattern for name matching (any part of name)
    name_pattern = "|".join(name_parts)

    query = {
        "gender": gender,
        "birthDate": {"$regex": f"^{year_of_birth}-"}  # Match YYYY-MM-DD format
    }

    # Find all patients matching gender and year
    candidates = []
    async for patient in patients_collection.find(query):
        # Check name match
        patient_name = ""
        if isinstance(patient.get("name"), list) and len(patient["name"]) > 0:
            name_obj = patient["name"][0]
            given = name_obj.get("given", [])
            family = name_obj.get("family", "")
            patient_name = f"{' '.join(given)} {family}".lower()

        # Check if any name part matches
        for part in name_parts:
            if part in patient_name:
                candidates.append(patient)
                logger.info(f"Fuzzy match candidate: {patient.get('abha_number')} - {patient_name}")
                break

    # Return first candidate (in production, would rank by match confidence)
    return candidates[0] if candidates else None


async def get_patient_care_contexts(db, patient_id: str) -> List[CareContextRepresentation]:
    """
    Get all care contexts (encounters/bundles) for a patient.
    """
    bundles_collection = db.fhir_bundles

    care_contexts = []

    # Find all bundles for this patient
    async for bundle in bundles_collection.find({"patient_id": patient_id}):
        bundle_type = bundle.get("bundle_type", "Unknown")
        created_at = bundle.get("created_at", datetime.now())

        care_contexts.append(CareContextRepresentation(
            referenceNumber=str(bundle["_id"]),
            display=f"{bundle_type} - {created_at.strftime('%Y-%m-%d')}"
        ))

    logger.info(f"Found {len(care_contexts)} care contexts for patient {patient_id}")
    return care_contexts


# API Endpoint

@router.post("/care-contexts/discover")
async def discover_patient(
    request: PatientDiscoveryRequest,
    db = Depends(get_database)
):
    """
    Discover patient by demographics and identifiers.

    Matching strategy:
    1. Try exact match by verified identifiers (ABHA, mobile, MR)
    2. Try exact match by unverified identifiers
    3. Try fuzzy match by demographics (name, gender, yearOfBirth)
    4. If no match, return error

    Then callback to Gateway with result.
    """
    logger.info(f"Processing discovery request {request.requestId} for patient {request.patient.name}")

    patient = None
    matched_by = []

    # Step 1: Try identifier matching
    patient = await find_patient_by_identifiers(
        db,
        request.patient.verifiedIdentifiers,
        request.patient.unverifiedIdentifiers
    )

    if patient:
        # Determine which identifier matched
        for identifier in request.patient.verifiedIdentifiers:
            if identifier.type in ["NDHM_HEALTH_NUMBER", "HEALTH_ID"]:
                abha = identifier.value.split("@")[0]
                if patient.get("abha_number") == abha:
                    matched_by.append(identifier.type)
            elif identifier.type == "MOBILE":
                matched_by.append("MOBILE")
            elif identifier.type == "MR":
                matched_by.append("MR")

    # Step 2: Try demographic matching if no identifier match
    if not patient:
        patient = await find_patient_by_demographics(
            db,
            request.patient.name,
            request.patient.gender,
            request.patient.yearOfBirth
        )
        if patient:
            matched_by = ["DEMOGRAPHIC"]

    # Prepare response
    result = PatientDiscoveryResult(
        requestId=request.requestId,
        timestamp=datetime.now(),
        transactionId=request.transactionId,
        resp=RequestReference(requestId=str(request.requestId))
    )

    if patient:
        # Get care contexts
        patient_id = patient.get("abha_number")
        care_contexts = await get_patient_care_contexts(db, patient_id)

        # Get patient display name
        display_name = request.patient.name  # Default to search name
        if isinstance(patient.get("name"), list) and len(patient["name"]) > 0:
            name_obj = patient["name"][0]
            given = name_obj.get("given", [])
            family = name_obj.get("family", "")
            display_name = f"{' '.join(given)} {family}"

        result.patient = PatientRepresentation(
            referenceNumber=patient_id,
            display=display_name,
            careContexts=care_contexts if care_contexts else None,
            matchedBy=matched_by if matched_by else None
        )

        logger.info(f"Patient discovered: {patient_id} (matched by {matched_by})")
    else:
        # No match found
        result.error = Error(
            code=1000,
            message=f"No patient found matching demographics: {request.patient.name}, {request.patient.gender}, {request.patient.yearOfBirth}"
        )
        logger.warning(f"No patient match for {request.patient.name}")

    # Callback to Gateway
    gateway_url = "http://gateway:8090/v0.5/care-contexts/on-discover"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                gateway_url,
                json=result.dict(by_alias=True),
                timeout=10.0
            )

            if response.status_code == 200:
                logger.info(f"Discovery result sent to Gateway for request {request.requestId}")
            else:
                logger.error(f"Failed to send discovery result to Gateway: {response.status_code}")

    except Exception as e:
        logger.error(f"Error sending callback to Gateway: {str(e)}")

    return {"acknowledged": True}
