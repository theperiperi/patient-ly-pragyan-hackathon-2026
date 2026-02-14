"""Base adapter classes and shared data types for the ingestion pipeline."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from fhir.resources.R4B.resource import Resource
from fhir.resources.R4B.patient import Patient as FHIRPatient


@dataclass
class PatientIdentity:
    """Extracted patient identifying info for cross-source linking."""

    source_id: str
    source_system: str  # e.g. "apple_health", "ems_108", "hospital_ehr"
    full_name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    birth_date: str | None = None  # ISO format YYYY-MM-DD
    gender: str | None = None  # "male", "female", "other", "unknown"
    phone: str | None = None
    email: str | None = None
    mrn: str | None = None  # Medical Record Number
    abha_id: str | None = None  # ABDM Health ID
    address_line: str | None = None
    address_city: str | None = None
    address_state: str | None = None
    address_postal_code: str | None = None


@dataclass
class AdapterResult:
    """Standardized output from any adapter."""

    patient_identity: PatientIdentity
    fhir_resources: list[Resource]
    fhir_patient: FHIRPatient | None = None
    source_type: str = ""
    raw_metadata: dict[str, Any] = field(default_factory=dict)


class BaseAdapter(ABC):
    """All source adapters inherit from this."""

    @property
    @abstractmethod
    def source_type(self) -> str:
        """Unique identifier for this source type."""
        ...

    @abstractmethod
    def parse(self, input_data: Any) -> AdapterResult:
        """Parse input data and return FHIR resources + patient identity."""
        ...

    @abstractmethod
    def supports(self, input_data: Any) -> bool:
        """Return True if this adapter can handle the given input."""
        ...
