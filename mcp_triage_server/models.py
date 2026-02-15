"""Pydantic models for MCP Triage Server."""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class PatientBasic(BaseModel):
    """Basic patient info for search results."""
    patient_id: str
    abha_number: str
    abha_address: str
    name: str
    gender: str
    date_of_birth: date
    age: int
    city: str
    state: str


class Condition(BaseModel):
    """Medical condition."""
    code: str
    display: str
    clinical_status: str  # active, resolved, etc.
    onset_date: Optional[date] = None
    is_high_risk: bool = False
    is_cardiac: bool = False
    is_respiratory: bool = False
    is_immunocompromising: bool = False


class Medication(BaseModel):
    """Medication prescription."""
    code: str
    display: str
    status: str  # active, completed, etc.
    dosage: Optional[str] = None
    start_date: Optional[date] = None


class Allergy(BaseModel):
    """Allergy intolerance."""
    code: str
    display: str
    category: Optional[str] = None  # food, medication, environment
    criticality: Optional[str] = None  # low, high, unable-to-assess
    reaction_type: Optional[str] = None


class Vital(BaseModel):
    """Vital sign observation."""
    code: str
    display: str
    value: str
    unit: Optional[str] = None
    recorded_date: Optional[datetime] = None


class Encounter(BaseModel):
    """Healthcare encounter."""
    encounter_id: str
    encounter_type: str
    encounter_class: str  # AMB, EMER, IMP, etc.
    status: str
    start_date: Optional[date] = None
    reason: Optional[str] = None
    is_emergency: bool = False
    days_ago: int = 0


class ContextHints(BaseModel):
    """Context hints for clinical decision support."""
    elderly: bool = False
    pediatric: bool = False
    cardiac_history: bool = False
    respiratory_history: bool = False
    diabetic: bool = False
    polypharmacy: bool = False
    recent_ed_visit: bool = False
    high_risk_conditions: list[str] = []
    allergy_count: int = 0
    immunocompromised: bool = False
    active_condition_count: int = 0
    active_medication_count: int = 0


class PatientSnapshot(BaseModel):
    """Comprehensive patient snapshot with context hints."""
    # Demographics
    patient_id: str
    abha_number: str
    abha_address: str
    name: str
    gender: str
    date_of_birth: date
    age: int
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None

    # Clinical data
    conditions: list[Condition] = []
    medications: list[Medication] = []
    allergies: list[Allergy] = []
    recent_vitals: list[Vital] = []
    recent_encounters: list[Encounter] = []

    # Context hints for agent
    hints: ContextHints = ContextHints()
