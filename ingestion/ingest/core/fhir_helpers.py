"""Shared FHIR R4 resource factory functions.

All functions return validated fhir.resources.R4B model instances.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.observation import Observation, ObservationComponent
from fhir.resources.R4B.encounter import Encounter
from fhir.resources.R4B.condition import Condition
from fhir.resources.R4B.documentreference import DocumentReference, DocumentReferenceContent
from fhir.resources.R4B.imagingstudy import ImagingStudy, ImagingStudySeries
from fhir.resources.R4B.diagnosticreport import DiagnosticReport
from fhir.resources.R4B.bundle import Bundle, BundleEntry, BundleEntryRequest

from ingest.core.base_adapter import PatientIdentity
from ingest import config as cfg


def _uuid() -> str:
    return str(uuid.uuid4())


def make_patient(identity: PatientIdentity) -> Patient:
    """Create a FHIR Patient resource from extracted identity."""
    identifiers = []
    if identity.mrn:
        identifiers.append({
            "system": "urn:oid:1.2.36.146.595.217.0.1",
            "value": identity.mrn,
            "type": {
                "coding": [{"system": "http://terminology.hl7.org/CodeSystem/v2-0203", "code": "MR"}]
            },
        })
    if identity.abha_id:
        identifiers.append({
            "system": cfg.ABDM_HEALTH_ID_SYSTEM,
            "value": identity.abha_id,
        })

    name_parts = {}
    if identity.family_name:
        name_parts["family"] = identity.family_name
    if identity.given_name:
        name_parts["given"] = [identity.given_name]
    if not name_parts and identity.full_name:
        parts = identity.full_name.strip().split()
        if len(parts) >= 2:
            name_parts = {"family": parts[-1], "given": [" ".join(parts[:-1])]}
        elif parts:
            name_parts = {"family": parts[0]}

    address = None
    if any([identity.address_line, identity.address_city, identity.address_state]):
        addr = {"use": "home"}
        if identity.address_line:
            addr["line"] = [identity.address_line]
        if identity.address_city:
            addr["city"] = identity.address_city
        if identity.address_state:
            addr["state"] = identity.address_state
        if identity.address_postal_code:
            addr["postalCode"] = identity.address_postal_code
        address = [addr]

    data: dict = {
        "id": _uuid(),
        "meta": {"profile": [cfg.NRCES_PATIENT_PROFILE]},
    }
    if identifiers:
        data["identifier"] = identifiers
    if name_parts:
        data["name"] = [{"use": "official", **name_parts}]
    if identity.gender:
        data["gender"] = identity.gender
    if identity.birth_date:
        data["birthDate"] = identity.birth_date
    if identity.phone:
        data["telecom"] = [{"system": "phone", "value": identity.phone, "use": "mobile"}]
    if address:
        data["address"] = address

    return Patient(**data)


def make_observation_vital(
    patient_ref: str,
    loinc_code: tuple[str, str],
    value: float,
    unit_display: str,
    ucum_code: str,
    effective_dt: str,
    *,
    observation_id: str | None = None,
) -> Observation:
    """Create a vital sign Observation with LOINC coding."""
    return Observation(
        id=observation_id or _uuid(),
        status="final",
        category=[{
            "coding": [{
                "system": cfg.OBSERVATION_CATEGORY_SYSTEM,
                "code": "vital-signs",
                "display": "Vital Signs",
            }]
        }],
        code={
            "coding": [{
                "system": cfg.LOINC_SYSTEM,
                "code": loinc_code[0],
                "display": loinc_code[1],
            }]
        },
        subject={"reference": patient_ref},
        effectiveDateTime=effective_dt,
        valueQuantity={
            "value": value,
            "unit": unit_display,
            "system": cfg.UCUM_SYSTEM,
            "code": ucum_code,
        },
    )


def make_observation_bp(
    patient_ref: str,
    systolic: float,
    diastolic: float,
    effective_dt: str,
    *,
    observation_id: str | None = None,
) -> Observation:
    """Create a blood pressure Observation with systolic + diastolic components."""
    return Observation(
        id=observation_id or _uuid(),
        status="final",
        category=[{
            "coding": [{
                "system": cfg.OBSERVATION_CATEGORY_SYSTEM,
                "code": "vital-signs",
                "display": "Vital Signs",
            }]
        }],
        code={
            "coding": [{
                "system": cfg.LOINC_SYSTEM,
                "code": cfg.LOINC_BP_PANEL[0],
                "display": cfg.LOINC_BP_PANEL[1],
            }]
        },
        subject={"reference": patient_ref},
        effectiveDateTime=effective_dt,
        component=[
            ObservationComponent(
                code={
                    "coding": [{
                        "system": cfg.LOINC_SYSTEM,
                        "code": cfg.LOINC_BP_SYSTOLIC[0],
                        "display": cfg.LOINC_BP_SYSTOLIC[1],
                    }]
                },
                valueQuantity={
                    "value": systolic,
                    "unit": "mmHg",
                    "system": cfg.UCUM_SYSTEM,
                    "code": cfg.UCUM_MMHG,
                },
            ),
            ObservationComponent(
                code={
                    "coding": [{
                        "system": cfg.LOINC_SYSTEM,
                        "code": cfg.LOINC_BP_DIASTOLIC[0],
                        "display": cfg.LOINC_BP_DIASTOLIC[1],
                    }]
                },
                valueQuantity={
                    "value": diastolic,
                    "unit": "mmHg",
                    "system": cfg.UCUM_SYSTEM,
                    "code": cfg.UCUM_MMHG,
                },
            ),
        ],
    )


def make_observation_lab(
    patient_ref: str,
    loinc_code: tuple[str, str],
    value: float,
    unit: str,
    ucum_code: str,
    effective_dt: str,
    reference_range_low: float | None = None,
    reference_range_high: float | None = None,
) -> Observation:
    """Create a laboratory Observation."""
    obs_data: dict = {
        "id": _uuid(),
        "status": "final",
        "category": [{
            "coding": [{
                "system": cfg.OBSERVATION_CATEGORY_SYSTEM,
                "code": "laboratory",
                "display": "Laboratory",
            }]
        }],
        "code": {
            "coding": [{
                "system": cfg.LOINC_SYSTEM,
                "code": loinc_code[0],
                "display": loinc_code[1],
            }]
        },
        "subject": {"reference": patient_ref},
        "effectiveDateTime": effective_dt,
        "valueQuantity": {
            "value": value,
            "unit": unit,
            "system": cfg.UCUM_SYSTEM,
            "code": ucum_code,
        },
    }
    if reference_range_low is not None or reference_range_high is not None:
        rr: dict = {}
        if reference_range_low is not None:
            rr["low"] = {"value": reference_range_low, "unit": unit, "system": cfg.UCUM_SYSTEM, "code": ucum_code}
        if reference_range_high is not None:
            rr["high"] = {"value": reference_range_high, "unit": unit, "system": cfg.UCUM_SYSTEM, "code": ucum_code}
        obs_data["referenceRange"] = [rr]
    return Observation(**obs_data)


def make_encounter(
    patient_ref: str,
    encounter_class: str,
    class_display: str,
    period_start: str,
    period_end: str | None = None,
    *,
    status: str = "finished",
    encounter_id: str | None = None,
) -> Encounter:
    """Create an Encounter resource."""
    period = {"start": period_start}
    if period_end:
        period["end"] = period_end
    return Encounter(
        id=encounter_id or _uuid(),
        status=status,
        **{"class": {
            "system": cfg.ENCOUNTER_CLASS_SYSTEM,
            "code": encounter_class,
            "display": class_display,
        }},
        subject={"reference": patient_ref},
        period=period,
    )


def make_condition(
    patient_ref: str,
    code: str,
    display: str,
    system: str = cfg.SNOMED_SYSTEM,
    *,
    clinical_status: str = "active",
    verification_status: str = "confirmed",
    category: str = "encounter-diagnosis",
    onset_date: str | None = None,
) -> Condition:
    """Create a Condition resource."""
    data: dict = {
        "id": _uuid(),
        "clinicalStatus": {
            "coding": [{"system": cfg.CONDITION_CLINICAL_SYSTEM, "code": clinical_status}]
        },
        "verificationStatus": {
            "coding": [{"system": cfg.CONDITION_VERIFICATION_SYSTEM, "code": verification_status}]
        },
        "category": [{
            "coding": [{"system": cfg.CONDITION_CATEGORY_SYSTEM, "code": category}]
        }],
        "code": {
            "coding": [{"system": system, "code": code, "display": display}]
        },
        "subject": {"reference": patient_ref},
    }
    if onset_date:
        data["onsetDateTime"] = onset_date
    return Condition(**data)


def make_document_reference(
    patient_ref: str,
    content_type: str,
    data_b64: str,
    description: str,
    *,
    doc_type_code: str = "34108-1",
    doc_type_display: str = "Outpatient note",
    title: str | None = None,
) -> DocumentReference:
    """Create a DocumentReference with a base64-encoded attachment."""
    return DocumentReference(
        id=_uuid(),
        status="current",
        docStatus="final",
        type={
            "coding": [{
                "system": cfg.DOCUMENT_TYPE_SYSTEM,
                "code": doc_type_code,
                "display": doc_type_display,
            }]
        },
        subject={"reference": patient_ref},
        date=datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        description=description,
        content=[
            DocumentReferenceContent(
                attachment={
                    "contentType": content_type,
                    "data": data_b64,
                    "title": title or description,
                }
            )
        ],
    )


def make_imaging_study(
    patient_ref: str,
    modality: str,
    study_uid: str,
    series_uid: str,
    *,
    study_description: str | None = None,
    body_part: str | None = None,
    started: str | None = None,
    status: str = "available",
) -> ImagingStudy:
    """Create an ImagingStudy resource for DICOM data."""
    series = ImagingStudySeries(
        uid=series_uid,
        modality={"system": "http://dicom.nema.org/resources/ontology/DCM", "code": modality},
        numberOfInstances=1,
    )
    if body_part:
        series.bodySite = {"system": cfg.SNOMED_SYSTEM, "display": body_part}

    data: dict = {
        "id": _uuid(),
        "status": status,
        "subject": {"reference": patient_ref},
        "numberOfSeries": 1,
        "numberOfInstances": 1,
        "series": [series],
    }
    if study_description:
        data["description"] = study_description
    if started:
        data["started"] = started

    return ImagingStudy(**data)


def make_diagnostic_report(
    patient_ref: str,
    category_code: str,
    category_display: str,
    report_code: tuple[str, str],
    result_refs: list[str] | None = None,
    conclusion: str | None = None,
    *,
    effective_dt: str | None = None,
    status: str = "final",
) -> DiagnosticReport:
    """Create a DiagnosticReport resource."""
    data: dict = {
        "id": _uuid(),
        "status": status,
        "category": [{
            "coding": [{
                "system": cfg.DIAGNOSTIC_REPORT_CATEGORY_SYSTEM,
                "code": category_code,
                "display": category_display,
            }]
        }],
        "code": {
            "coding": [{
                "system": cfg.LOINC_SYSTEM,
                "code": report_code[0],
                "display": report_code[1],
            }]
        },
        "subject": {"reference": patient_ref},
    }
    if effective_dt:
        data["effectiveDateTime"] = effective_dt
    if result_refs:
        data["result"] = [{"reference": r} for r in result_refs]
    if conclusion:
        data["conclusion"] = conclusion
    return DiagnosticReport(**data)


def make_observation_sampled_data(
    patient_ref: str,
    loinc_code: tuple[str, str],
    data_string: str,
    period_ms: float,
    dimensions: int,
    effective_dt: str,
    origin_value: float = 0.0,
    origin_unit: str = "mV",
    origin_ucum: str = "mV",
) -> Observation:
    """Create an Observation with SampledData (for waveforms like ECG)."""
    return Observation(
        id=_uuid(),
        status="final",
        category=[{
            "coding": [{
                "system": cfg.OBSERVATION_CATEGORY_SYSTEM,
                "code": "vital-signs",
                "display": "Vital Signs",
            }]
        }],
        code={
            "coding": [{
                "system": cfg.LOINC_SYSTEM,
                "code": loinc_code[0],
                "display": loinc_code[1],
            }]
        },
        subject={"reference": patient_ref},
        effectiveDateTime=effective_dt,
        valueSampledData={
            "origin": {
                "value": origin_value,
                "unit": origin_unit,
                "system": cfg.UCUM_SYSTEM,
                "code": origin_ucum,
            },
            "period": period_ms,
            "dimensions": dimensions,
            "data": data_string,
        },
    )
