"""Pydantic schemas for structured voice extraction output."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ExtractedVitals(BaseModel):
    heart_rate: float | None = None
    blood_pressure_systolic: float | None = None
    blood_pressure_diastolic: float | None = None
    spo2: float | None = None
    temperature: float | None = None
    respiratory_rate: float | None = None
    body_weight: float | None = None
    body_height: float | None = None
    bmi: float | None = None


class ExtractedDiagnosis(BaseModel):
    code: str | None = None
    description: str = ""
    clinical_status: str = "active"
    onset_date: str | None = None


class ExtractedEncounter(BaseModel):
    encounter_class: str | None = None  # "inpatient", "outpatient", "emergency"
    period_start: str | None = None
    period_end: str | None = None
    status: str = "in-progress"


class VoiceExtractionResult(BaseModel):
    """Complete structured extraction from a voice transcript."""

    # Patient demographics
    patient_name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    birth_date: str | None = None
    gender: str | None = None
    phone: str | None = None
    email: str | None = None
    mrn: str | None = None
    abha_id: str | None = None
    address_line: str | None = None
    address_city: str | None = None
    address_state: str | None = None
    address_postal_code: str | None = None

    # Clinical
    chief_complaint: str | None = None
    vitals: ExtractedVitals = Field(default_factory=ExtractedVitals)
    diagnoses: list[ExtractedDiagnosis] = Field(default_factory=list)
    medications: list[str] = Field(default_factory=list)
    encounter: ExtractedEncounter | None = None

    # Metadata
    notes: str | None = None
