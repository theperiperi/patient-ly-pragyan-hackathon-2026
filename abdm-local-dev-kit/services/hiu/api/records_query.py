"""
HIU Records Query API

Query and retrieve collected health information.
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

# Get database dependency
async def get_db():
    """Get database connection."""
    import database
    return database.get_database()

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Records Query"])


# ============================================================================
# Pydantic Models
# ============================================================================

class HealthRecordSummary(BaseModel):
    """Summary of a health record."""
    bundleId: str = Field(..., description="FHIR Bundle ID")
    resourceType: str = Field(..., example="Bundle")
    type: str = Field(..., example="document")
    hiType: str = Field(..., example="DiagnosticReport")
    timestamp: datetime = Field(..., description="Bundle creation timestamp")
    careContext: Optional[str] = Field(None, description="Care context reference")
    entries: int = Field(..., description="Number of entries in bundle")

class ConsentSummary(BaseModel):
    """Summary of consent used for data collection."""
    consentId: str = Field(..., description="Consent artefact ID")
    consentRequestId: str = Field(..., description="Original consent request ID")
    status: str = Field(..., example="GRANTED")
    purpose: str = Field(..., example="CAREMGT")
    grantedAt: Optional[datetime] = None

class TransactionSummary(BaseModel):
    """Summary of health information transaction."""
    transactionId: str = Field(..., description="HI transaction ID")
    requestId: str = Field(..., description="Original HI request ID")
    status: str = Field(..., example="ACKNOWLEDGED")
    bundlesReceived: int = Field(..., description="Number of bundles received")
    receivedAt: Optional[datetime] = None

class PatientHealthRecords(BaseModel):
    """Patient's health records collected by HIU."""
    patientId: str = Field(..., example="hinapatel@sbx")
    totalRecords: int = Field(..., description="Total number of records")
    totalBundles: int = Field(..., description="Total number of FHIR bundles")
    consents: List[ConsentSummary] = Field(default_factory=list)
    transactions: List[TransactionSummary] = Field(default_factory=list)
    records: List[HealthRecordSummary] = Field(default_factory=list)
    queriedAt: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/v0.5/patients/{abha}/records")
async def get_patient_records(
    abha: str,
    hi_type: Optional[str] = Query(None, description="Filter by HI type (DiagnosticReport, Prescription, etc.)"),
    from_date: Optional[datetime] = Query(None, alias="from", description="Filter from date"),
    to_date: Optional[datetime] = Query(None, alias="to", description="Filter to date"),
    limit: int = Query(50, description="Max number of records to return", ge=1, le=500),
    offset: int = Query(0, description="Offset for pagination", ge=0),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Query collected health records for a patient.

    Retrieves all health information collected by this HIU for the specified patient,
    with optional filtering by HI type and date range.

    Args:
        abha: Patient's ABHA number (e.g., "hinapatel@sbx")
        hi_type: Filter by health information type
        from_date: Start date for filtering
        to_date: End date for filtering
        limit: Maximum number of records to return
        offset: Offset for pagination
        db: Database connection

    Returns:
        Patient health records with consents, transactions, and bundles
    """
    logger.info(f"Query patient records: abha={abha}, hiType={hi_type}, from={from_date}, to={to_date}")

    # Find all consents for this patient
    consent_query = {"patientId": abha}
    consents_cursor = db.consent_artefacts.find(consent_query)
    consents = await consents_cursor.to_list(length=None)

    consent_ids = [c["artefactId"] for c in consents]
    logger.info(f"Found {len(consents)} consents for patient {abha}")

    # Find all HI requests/transactions for these consents
    if consent_ids:
        hi_requests = await db.hi_requests.find({
            "consentId": {"$in": consent_ids},
            "status": {"$in": ["ACKNOWLEDGED", "COMPLETED"]}
        }).to_list(length=None)

        transaction_ids = [req["transactionId"] for req in hi_requests if req.get("transactionId")]
    else:
        hi_requests = []
        transaction_ids = []

    logger.info(f"Found {len(hi_requests)} HI requests and {len(transaction_ids)} transactions")

    # Build query for health bundles
    bundle_query = {
        "$or": [
            {"transactionId": {"$in": transaction_ids}},
            {"patient.id": abha}
        ]
    } if transaction_ids else {"patient.id": abha}

    # Apply filters
    if hi_type:
        bundle_query["hiType"] = hi_type

    if from_date or to_date:
        date_filter = {}
        if from_date:
            date_filter["$gte"] = from_date
        if to_date:
            date_filter["$lte"] = to_date
        bundle_query["timestamp"] = date_filter

    # Query health bundles with pagination
    total_bundles = await db.health_bundles.count_documents(bundle_query)
    bundles_cursor = db.health_bundles.find(bundle_query).skip(offset).limit(limit)
    bundles = await bundles_cursor.to_list(length=limit)

    logger.info(f"Found {total_bundles} total bundles, returning {len(bundles)}")

    # Build response
    consent_summaries = [
        ConsentSummary(
            consentId=c["artefactId"],
            consentRequestId=c.get("consentRequestId", ""),
            status=c.get("status", "UNKNOWN"),
            purpose=c.get("purpose", ""),
            grantedAt=c.get("grantedAt")
        )
        for c in consents
    ]

    # Get transactions from hi_requests
    transaction_summaries = []
    for req in hi_requests:
        if req.get("transactionId"):
            # Count bundles for this transaction
            bundle_count = await db.health_bundles.count_documents({
                "transactionId": req["transactionId"]
            })

            transaction_summaries.append(TransactionSummary(
                transactionId=req["transactionId"],
                requestId=req["requestId"],
                status=req.get("sessionStatus", req.get("status", "UNKNOWN")),
                bundlesReceived=bundle_count,
                receivedAt=req.get("updatedAt")
            ))

    # Build record summaries
    record_summaries = [
        HealthRecordSummary(
            bundleId=bundle.get("id", str(bundle["_id"])),
            resourceType=bundle.get("resourceType", "Bundle"),
            type=bundle.get("type", "document"),
            hiType=bundle.get("hiType", "Unknown"),
            timestamp=bundle.get("timestamp", bundle.get("createdAt")),
            careContext=bundle.get("careContext"),
            entries=len(bundle.get("entry", []))
        )
        for bundle in bundles
    ]

    return PatientHealthRecords(
        patientId=abha,
        totalRecords=total_bundles,
        totalBundles=total_bundles,
        consents=consent_summaries,
        transactions=transaction_summaries,
        records=record_summaries
    )


@router.get("/v0.5/health-bundles/{bundle_id}")
async def get_health_bundle(
    bundle_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Retrieve a specific FHIR bundle by ID.

    Args:
        bundle_id: FHIR Bundle ID
        db: Database connection

    Returns:
        Complete FHIR bundle
    """
    logger.info(f"Retrieve bundle: {bundle_id}")

    bundle = await db.health_bundles.find_one({"id": bundle_id})

    if not bundle:
        # Try finding by MongoDB _id
        from bson import ObjectId
        try:
            bundle = await db.health_bundles.find_one({"_id": ObjectId(bundle_id)})
        except:
            pass

    if not bundle:
        raise HTTPException(status_code=404, detail=f"Bundle not found: {bundle_id}")

    # Remove MongoDB _id for clean JSON response
    bundle.pop("_id", None)

    return bundle


@router.get("/v0.5/hi-requests")
async def list_hi_requests(
    status: Optional[str] = Query(None, description="Filter by status (REQUESTED, ACKNOWLEDGED, COMPLETED, FAILED)"),
    consent_id: Optional[str] = Query(None, description="Filter by consent ID"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    List health information requests made by this HIU.

    Args:
        status: Filter by request status
        consent_id: Filter by consent artefact ID
        limit: Maximum results
        offset: Pagination offset
        db: Database connection

    Returns:
        List of HI requests
    """
    logger.info(f"List HI requests: status={status}, consentId={consent_id}")

    query = {}
    if status:
        query["status"] = status
    if consent_id:
        query["consentId"] = consent_id

    total = await db.hi_requests.count_documents(query)
    cursor = db.hi_requests.find(query).skip(offset).limit(limit).sort("createdAt", -1)
    requests = await cursor.to_list(length=limit)

    # Remove MongoDB _id for clean response
    for req in requests:
        req.pop("_id", None)

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "requests": requests
    }


@router.get("/v0.5/consent-requests")
async def list_consent_requests(
    status: Optional[str] = Query(None, description="Filter by status (REQUESTED, GRANTED, DENIED, EXPIRED, REVOKED)"),
    patient_id: Optional[str] = Query(None, description="Filter by patient ID"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    List consent requests made by this HIU.

    Args:
        status: Filter by consent status
        patient_id: Filter by patient ID
        limit: Maximum results
        offset: Pagination offset
        db: Database connection

    Returns:
        List of consent requests
    """
    logger.info(f"List consent requests: status={status}, patientId={patient_id}")

    query = {}
    if status:
        query["status"] = status
    if patient_id:
        query["patient"] = patient_id

    total = await db.consent_requests.count_documents(query)
    cursor = db.consent_requests.find(query).skip(offset).limit(limit).sort("createdAt", -1)
    requests = await cursor.to_list(length=limit)

    # Remove MongoDB _id for clean response
    for req in requests:
        req.pop("_id", None)

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "consent_requests": requests
    }
