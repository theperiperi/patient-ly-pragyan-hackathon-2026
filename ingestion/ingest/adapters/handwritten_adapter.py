"""Handwritten notes adapter - uses VLM to extract clinical data from images."""

from __future__ import annotations

import base64
import os
from typing import Any

from ingest.core.base_adapter import BaseAdapter, PatientIdentity, AdapterResult
from ingest.core.fhir_helpers import (
    make_patient, make_document_reference, make_condition,
    make_observation_vital, make_observation_bp,
)
from ingest import config as cfg
from ingest.api.vlm_client import VLMClient, MockVLMClient


SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}


class HandwrittenAdapter(BaseAdapter):

    def __init__(self, vlm_client: VLMClient | None = None):
        self._vlm = vlm_client or MockVLMClient()

    @property
    def source_type(self) -> str:
        return "handwritten_notes"

    def supports(self, input_data: Any) -> bool:
        if not isinstance(input_data, str) or not os.path.isfile(input_data):
            return False
        _, ext = os.path.splitext(input_data.lower())
        return ext in SUPPORTED_IMAGE_EXTENSIONS

    def parse(self, input_data: Any) -> AdapterResult:
        with open(input_data, "rb") as f:
            image_bytes = f.read()

        extracted = self._vlm.extract_from_image(image_bytes)

        identity = self._build_identity(extracted)
        patient = make_patient(identity)
        patient_ref = f"Patient/{patient.id}"
        resources = []

        # DocumentReference for the original image
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        _, ext = os.path.splitext(input_data.lower())
        content_type = {
            ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".png": "image/png", ".bmp": "image/bmp",
            ".tiff": "image/tiff", ".tif": "image/tiff",
            ".webp": "image/webp",
        }.get(ext, "image/png")
        doc_ref = make_document_reference(
            patient_ref, content_type, b64,
            f"Handwritten clinical note: {extracted.get('chief_complaint', 'unknown')}",
            doc_type_code="11488-4",
            doc_type_display="Consultation note",
            title=os.path.basename(input_data),
        )
        resources.append(doc_ref)

        # Conditions from diagnoses
        for dx in extracted.get("diagnoses", []):
            desc = dx.get("description", "")
            code = dx.get("code", "")
            if desc:
                system = cfg.ICD10_SYSTEM if code and code[0].isalpha() else cfg.SNOMED_SYSTEM
                resources.append(make_condition(patient_ref, code or "unknown", desc, system))

        # Vitals
        vitals = extracted.get("vitals", {})
        ts = "2026-02-14T12:00:00Z"

        hr = vitals.get("heart_rate")
        if hr is not None:
            resources.append(make_observation_vital(patient_ref, cfg.LOINC_HEART_RATE, float(hr), "beats/minute", cfg.UCUM_BPM, ts))

        spo2 = vitals.get("spo2")
        if spo2 is not None:
            resources.append(make_observation_vital(patient_ref, cfg.LOINC_SPO2, float(spo2), "%", cfg.UCUM_PERCENT, ts))

        sys_bp = vitals.get("blood_pressure_systolic")
        dia_bp = vitals.get("blood_pressure_diastolic")
        if sys_bp is not None and dia_bp is not None:
            resources.append(make_observation_bp(patient_ref, float(sys_bp), float(dia_bp), ts))

        rr = vitals.get("respiratory_rate")
        if rr is not None:
            resources.append(make_observation_vital(patient_ref, cfg.LOINC_RESP_RATE, float(rr), "breaths/minute", cfg.UCUM_BPM, ts))

        temp = vitals.get("temperature")
        if temp is not None:
            resources.append(make_observation_vital(patient_ref, cfg.LOINC_BODY_TEMP, float(temp), "degC", cfg.UCUM_CELSIUS, ts))

        return AdapterResult(
            patient_identity=identity, fhir_resources=resources,
            fhir_patient=patient, source_type=self.source_type,
            raw_metadata=extracted,
        )

    def _build_identity(self, extracted: dict) -> PatientIdentity:
        name = extracted.get("patient_name")
        given, family = None, None
        if name:
            parts = name.split()
            if len(parts) >= 2:
                given, family = parts[0], parts[-1]

        gender = extracted.get("gender")
        age_str = extracted.get("age", "")

        # Try to infer MRN from notes
        mrn = extracted.get("mrn")

        return PatientIdentity(
            source_id=f"handwritten_{name or 'unknown'}",
            source_system=self.source_type,
            full_name=name,
            given_name=given,
            family_name=family,
            gender=gender,
            mrn=mrn,
        )
