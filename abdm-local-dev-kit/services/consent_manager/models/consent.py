"""
Consent Flow Pydantic Models

Based on official ABDM Gateway API specifications (gateway.yaml)
All models conform to ABDM Health Information Exchange protocol.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID


# Health Information Types - using string instead of enum per ABDM spec
# Valid values: OPConsultation, Prescription, DischargeSummary, DiagnosticReport,
# ImmunizationRecord, HealthDocumentRecord, WellnessRecord
VALID_HI_TYPES = {
    "OPConsultation",
    "Prescription",
    "DischargeSummary",
    "DiagnosticReport",
    "ImmunizationRecord",
    "HealthDocumentRecord",
    "WellnessRecord"
}


class ConsentStatus(str, Enum):
    """Consent status states as per ABDM specifications."""
    REQUESTED = "REQUESTED"
    GRANTED = "GRANTED"
    DENIED = "DENIED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"


class AccessMode(str, Enum):
    """Access mode for health information."""
    VIEW = "VIEW"
    STORE = "STORE"
    QUERY = "QUERY"
    STREAM = "STREAM"


class FrequencyUnit(str, Enum):
    """Frequency units for data access."""
    HOUR = "HOUR"
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    YEAR = "YEAR"


# Purpose codes - using string instead of enum per ABDM spec
# Valid values: CAREMGT, BTG, PUBHLTH, HPAYMT, DSRCH, PATRQT
VALID_PURPOSE_CODES = {
    "CAREMGT",    # Care Management
    "BTG",        # Break the Glass
    "PUBHLTH",    # Public Health
    "HPAYMT",     # Healthcare Payment
    "DSRCH",      # Disease Specific Healthcare Research
    "PATRQT"      # Self Requested
}


class UsePurpose(BaseModel):
    """Purpose of use for health information access."""
    text: str = Field(..., description="Human-readable purpose description")
    code: str = Field(..., description="Purpose code from fixed set")
    refUri: Optional[str] = Field(None, description="Reference URI for purpose definition")


class Frequency(BaseModel):
    """Frequency of data access."""
    unit: FrequencyUnit
    value: int = Field(..., ge=1, description="Frequency value")
    repeats: int = Field(..., ge=0, description="Number of repetitions")


class DateRange(BaseModel):
    """Date range for health information access."""
    from_date: datetime = Field(..., alias="from", description="Start date-time")
    to_date: datetime = Field(..., alias="to", description="End date-time")

    class Config:
        populate_by_name = True


class Permission(BaseModel):
    """Permissions for health information access."""
    accessMode: AccessMode
    dateRange: DateRange
    dataEraseAt: datetime = Field(..., description="Date-time when data must be erased")
    frequency: Frequency


class OrganizationRepresentation(BaseModel):
    """Organization identifier for HIP/HIU."""
    id: str = Field(..., description="Organization ID")


class ConsentManagerPatientID(BaseModel):
    """Patient identifier in Consent Manager."""
    id: str = Field(..., description="Patient health ID (ABHA@consent-manager-id)")


class CareContextDefinition(BaseModel):
    """Care context definition for consent."""
    patientReference: str = Field(..., description="Patient reference in HIP")
    careContextReference: str = Field(..., description="Care context reference (visit ID, episode ID)")


class Requester(BaseModel):
    """Requester details for consent."""
    name: str = Field(..., description="Name of the requester")
    identifier: Optional[str] = Field(None, description="Requester identifier")


class ConsentRequestDetail(BaseModel):
    """Consent request details."""
    purpose: UsePurpose
    patient: ConsentManagerPatientID
    hip: Optional[OrganizationRepresentation] = Field(None, description="Specific HIP if known")
    careContexts: Optional[List[CareContextDefinition]] = Field(None, description="Specific care contexts")
    hiu: OrganizationRepresentation
    requester: Requester
    hiTypes: List[str] = Field(..., description="Types of health information requested")
    permission: Permission
    consentNotificationUrl: str = Field(..., description="URL for consent notifications")


class ConsentRequest(BaseModel):
    """Main consent request structure sent to Gateway."""
    requestId: UUID = Field(..., description="Unique request ID for idempotency")
    timestamp: datetime
    consent: ConsentRequestDetail


class ConsentRequestResponse(BaseModel):
    """Response from Consent Manager after consent request creation."""
    id: UUID = Field(..., description="Consent request ID created by CM")
    timestamp: datetime


class ConsentArtefactDetail(BaseModel):
    """Consent artefact detail structure."""
    schemaVersion: Optional[str] = Field(None, description="Schema version")
    consentId: UUID = Field(..., description="Unique consent ID")
    createdAt: datetime
    patient: ConsentManagerPatientID
    careContexts: List[CareContextDefinition]
    purpose: UsePurpose
    hip: OrganizationRepresentation
    consentManager: OrganizationRepresentation
    hiTypes: List[str]
    permission: Permission


class ConsentArtefact(BaseModel):
    """Complete consent artefact with signature."""
    status: ConsentStatus
    consentId: UUID
    consentDetail: ConsentArtefactDetail
    signature: str = Field(..., description="Digital signature of consent manager")


class ConsentNotification(BaseModel):
    """Notification of consent status change."""
    requestId: UUID
    timestamp: datetime
    notification: ConsentArtefact


# MongoDB document models (adds database-specific fields)
class ConsentRequestDocument(BaseModel):
    """Consent request stored in MongoDB."""
    request_id: str = Field(..., description="UUID as string for MongoDB indexing")
    patient_abha: str = Field(..., description="Patient ABHA number")
    hiu_id: str = Field(..., description="HIU organization ID")
    hip_id: Optional[str] = Field(None, description="HIP organization ID if specified")
    purpose_code: str
    hi_types: List[str]
    status: ConsentStatus = ConsentStatus.REQUESTED
    consent_request: dict = Field(..., description="Full ABDM ConsentRequest as dict")
    created_at: datetime
    updated_at: datetime
    expires_at: datetime
    consent_id: Optional[str] = Field(None, description="Consent ID after approval")
    consent_artefact: Optional[dict] = Field(None, description="Consent artefact after approval")


class ConsentArtefactDocument(BaseModel):
    """Consent artefact stored in MongoDB."""
    consent_id: str = Field(..., description="UUID as string for MongoDB indexing")
    consent_request_id: str
    patient_abha: str
    hiu_id: str
    hip_id: str
    status: ConsentStatus = ConsentStatus.GRANTED
    consent_artefact: dict = Field(..., description="Full ABDM ConsentArtefact as dict")
    created_at: datetime
    granted_at: datetime
    expiry_date: datetime = Field(..., description="Permission dataEraseAt")
    revoked_at: Optional[datetime] = None
