"""Adapter for Synthea-generated FHIR transaction bundles.

Ingests raw Synthea JSON bundles and converts them into the pipeline's
AdapterResult format, extracting patient identity and all FHIR resources.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fhir.resources.R4B.patient import Patient as FHIRPatient
from fhir.resources.R4B.observation import Observation
from fhir.resources.R4B.condition import Condition
from fhir.resources.R4B.encounter import Encounter
from fhir.resources.R4B.diagnosticreport import DiagnosticReport
from fhir.resources.R4B.procedure import Procedure
from fhir.resources.R4B.immunization import Immunization
from fhir.resources.R4B.claim import Claim
from fhir.resources.R4B.explanationofbenefit import ExplanationOfBenefit
from fhir.resources.R4B.documentreference import DocumentReference
from fhir.resources.R4B.resource import Resource

from ingest.core.base_adapter import BaseAdapter, AdapterResult, PatientIdentity

# Map of Synthea resource types we can parse
_RESOURCE_PARSERS = {
    "Patient": FHIRPatient,
    "Observation": Observation,
    "Condition": Condition,
    "Encounter": Encounter,
    "DiagnosticReport": DiagnosticReport,
    "Procedure": Procedure,
    "Immunization": Immunization,
    "DocumentReference": DocumentReference,
}


class SyntheaAdapter(BaseAdapter):
    """Adapter for Synthea-generated FHIR R4 transaction bundles."""

    @property
    def source_type(self) -> str:
        return "synthea_fhir"

    def supports(self, input_data: Any) -> bool:
        """Check if input is a Synthea FHIR bundle JSON file."""
        if isinstance(input_data, str):
            path = Path(input_data)
            if not path.is_file() or path.suffix.lower() != ".json":
                return False
            try:
                with open(path) as f:
                    data = json.load(f)
                # Synthea bundles are transaction bundles with Patient entries
                if data.get("resourceType") != "Bundle":
                    return False
                if data.get("type") != "transaction":
                    return False
                # Check for Synthea marker in the first Patient entry
                for entry in data.get("entry", [])[:5]:
                    resource = entry.get("resource", {})
                    if resource.get("resourceType") == "Patient":
                        text = resource.get("text", {}).get("div", "")
                        if "synthea" in text.lower() or "synthetichealth" in text.lower():
                            return True
                        # Also accept if it has the synthea identifier system
                        for ident in resource.get("identifier", []):
                            if "synthetichealth" in ident.get("system", ""):
                                return True
                        # Accept any FHIR transaction bundle with a Patient
                        return True
                return False
            except (json.JSONDecodeError, OSError):
                return False
        return False

    def parse(self, input_data: Any) -> AdapterResult:
        """Parse a Synthea FHIR bundle into AdapterResult."""
        path = Path(input_data)
        with open(path) as f:
            bundle_data = json.load(f)

        entries = bundle_data.get("entry", [])

        patient_identity = None
        fhir_patient = None
        fhir_resources: list[Resource] = []
        resource_counts: dict[str, int] = {}

        for entry in entries:
            resource_data = entry.get("resource", {})
            resource_type = resource_data.get("resourceType", "")

            resource_counts[resource_type] = resource_counts.get(resource_type, 0) + 1

            if resource_type == "Patient":
                patient_identity = self._extract_identity(resource_data)
                fhir_patient = self._parse_patient(resource_data)
                continue

            # Parse known resource types
            parser_cls = _RESOURCE_PARSERS.get(resource_type)
            if parser_cls:
                try:
                    resource = parser_cls.model_validate(resource_data)
                    fhir_resources.append(resource)
                except Exception:
                    # Skip resources that fail validation; Synthea may produce
                    # resources with fields not in R4B strict mode
                    pass

        if patient_identity is None:
            patient_identity = PatientIdentity(
                source_id=path.stem,
                source_system="synthea_fhir",
            )

        return AdapterResult(
            patient_identity=patient_identity,
            fhir_resources=fhir_resources,
            fhir_patient=fhir_patient,
            source_type=self.source_type,
            raw_metadata={
                "source_file": str(path),
                "bundle_type": bundle_data.get("type"),
                "total_entries": len(entries),
                "resource_counts": resource_counts,
            },
        )

    def _extract_identity(self, patient: dict) -> PatientIdentity:
        """Extract PatientIdentity from a Synthea Patient resource."""
        names = patient.get("name", [])
        given_name = ""
        family_name = ""
        full_name = ""
        for n in names:
            if n.get("use") == "official" or not given_name:
                given_parts = n.get("given", [])
                given_name = given_parts[0] if given_parts else ""
                family_name = n.get("family", "")
                full_name = f"{given_name} {family_name}".strip()

        gender = patient.get("gender", None)
        birth_date = patient.get("birthDate", None)

        # Extract identifiers
        mrn = None
        for ident in patient.get("identifier", []):
            id_type = ident.get("type", {})
            for coding in id_type.get("coding", []):
                if coding.get("code") == "MR":
                    mrn = ident.get("value")
                    break
            if mrn:
                break

        # Extract phone
        phone = None
        for telecom in patient.get("telecom", []):
            if telecom.get("system") == "phone":
                phone = telecom.get("value")
                break

        # Extract address
        address_line = None
        address_city = None
        address_state = None
        address_postal = None
        for addr in patient.get("address", []):
            lines = addr.get("line", [])
            if lines:
                address_line = lines[0]
            address_city = addr.get("city")
            address_state = addr.get("state")
            address_postal = addr.get("postalCode")
            break

        return PatientIdentity(
            source_id=patient.get("id", ""),
            source_system="synthea_fhir",
            full_name=full_name or None,
            given_name=given_name or None,
            family_name=family_name or None,
            birth_date=birth_date,
            gender=gender,
            phone=phone,
            mrn=mrn,
            address_line=address_line,
            address_city=address_city,
            address_state=address_state,
            address_postal_code=address_postal,
        )

    def _parse_patient(self, patient_data: dict) -> FHIRPatient | None:
        """Parse Patient resource, handling Synthea-specific extensions gracefully."""
        try:
            return FHIRPatient.model_validate(patient_data)
        except Exception:
            # Synthea may include US Core extensions not in base R4B;
            # strip extensions and retry
            stripped = {k: v for k, v in patient_data.items() if k != "extension"}
            try:
                return FHIRPatient.model_validate(stripped)
            except Exception:
                return None
