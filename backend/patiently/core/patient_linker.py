"""Cross-source patient matching and linking."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from fhir.resources.R4B.patient import Patient as FHIRPatient
from fhir.resources.R4B.resource import Resource

from patiently.core.base_adapter import PatientIdentity, AdapterResult
from patiently.core.fhir_helpers import make_patient


@dataclass
class LinkedPatient:
    """A unified patient aggregated from multiple sources."""

    canonical_id: str
    identities: list[PatientIdentity] = field(default_factory=list)
    fhir_patient: FHIRPatient | None = None
    all_resources: list[Resource] = field(default_factory=list)
    source_types: set[str] = field(default_factory=set)


class PatientLinker:
    """Matches patient identities across data sources and merges them."""

    def __init__(self):
        self._linked_patients: list[LinkedPatient] = []

    def ingest(self, result: AdapterResult) -> LinkedPatient:
        """Try to match the result's patient to an existing LinkedPatient, or create new."""
        match = self._find_match(result.patient_identity)

        if match is None:
            match = LinkedPatient(canonical_id=str(uuid.uuid4()))
            self._linked_patients.append(match)

        match.identities.append(result.patient_identity)
        match.source_types.add(result.source_type)
        match.all_resources.extend(result.fhir_resources)

        # Merge patient resource — take the most complete fields
        match.fhir_patient = self._merge_patient(match.identities)

        return match

    def get_all_patients(self) -> list[LinkedPatient]:
        """Return all linked patients."""
        return list(self._linked_patients)

    def _find_match(self, identity: PatientIdentity) -> LinkedPatient | None:
        """Deterministic matching with tiered priority."""
        for lp in self._linked_patients:
            for existing in lp.identities:
                # Tier 1: Exact MRN match
                if identity.mrn and existing.mrn and identity.mrn == existing.mrn:
                    return lp

                # Tier 2: Exact ABHA ID match
                if identity.abha_id and existing.abha_id and identity.abha_id == existing.abha_id:
                    return lp

                # Tier 3: Exact normalized name + DOB match
                if identity.birth_date and existing.birth_date:
                    if identity.birth_date == existing.birth_date:
                        name_a = self._normalize_name(identity)
                        name_b = self._normalize_name(existing)
                        if name_a and name_b and name_a == name_b:
                            return lp

                # Tier 4: Phone or email match
                if identity.phone and existing.phone:
                    if self._normalize_phone(identity.phone) == self._normalize_phone(existing.phone):
                        return lp
                if identity.email and existing.email:
                    if identity.email.lower() == existing.email.lower():
                        return lp

        return None

    def _merge_patient(self, identities: list[PatientIdentity]) -> FHIRPatient:
        """Create a merged FHIR Patient from all linked identities, taking the most complete fields."""
        merged = PatientIdentity(source_id="merged", source_system="merged")

        for ident in identities:
            if ident.given_name and not merged.given_name:
                merged.given_name = ident.given_name
            if ident.family_name and not merged.family_name:
                merged.family_name = ident.family_name
            if ident.full_name and not merged.full_name:
                merged.full_name = ident.full_name
            if ident.birth_date and not merged.birth_date:
                merged.birth_date = ident.birth_date
            if ident.gender and not merged.gender:
                merged.gender = ident.gender
            if ident.mrn and not merged.mrn:
                merged.mrn = ident.mrn
            if ident.abha_id and not merged.abha_id:
                merged.abha_id = ident.abha_id
            if ident.phone and not merged.phone:
                merged.phone = ident.phone
            if ident.email and not merged.email:
                merged.email = ident.email
            if ident.address_line and not merged.address_line:
                merged.address_line = ident.address_line
            if ident.address_city and not merged.address_city:
                merged.address_city = ident.address_city
            if ident.address_state and not merged.address_state:
                merged.address_state = ident.address_state
            if ident.address_postal_code and not merged.address_postal_code:
                merged.address_postal_code = ident.address_postal_code

        return make_patient(merged)

    @staticmethod
    def _normalize_name(identity: PatientIdentity) -> str | None:
        """Normalize a name for comparison: lowercase, stripped, sorted parts."""
        name = identity.full_name
        if not name:
            parts = []
            if identity.given_name:
                parts.append(identity.given_name)
            if identity.family_name:
                parts.append(identity.family_name)
            name = " ".join(parts) if parts else None
        if not name:
            return None
        # Lowercase, strip, remove extra spaces, sort parts for order-independence
        parts = sorted(name.lower().strip().split())
        return " ".join(parts)

    @staticmethod
    def _normalize_phone(phone: str) -> str:
        """Normalize phone number by keeping only digits."""
        return "".join(c for c in phone if c.isdigit())
