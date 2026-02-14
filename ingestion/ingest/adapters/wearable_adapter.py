"""Wearable adapter - parses Apple Health XML and Google Fit JSON into FHIR Observations."""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any
from xml.etree import ElementTree as ET

from ingest.core.base_adapter import BaseAdapter, PatientIdentity, AdapterResult
from ingest.core.fhir_helpers import make_patient, make_observation_vital, make_observation_bp
from ingest import config as cfg


class WearableAdapter(BaseAdapter):

    @property
    def source_type(self) -> str:
        return "wearable"

    def supports(self, input_data: Any) -> bool:
        if not isinstance(input_data, str) or not os.path.isfile(input_data):
            return False
        if input_data.endswith(".xml"):
            try:
                tree = ET.parse(input_data)
                return tree.getroot().tag == "HealthData"
            except Exception:
                return False
        if input_data.endswith(".json"):
            try:
                with open(input_data, "r") as f:
                    data = json.load(f)
                return "dataPoints" in data or data.get("source_type") == "google_fit"
            except Exception:
                return False
        return False

    def parse(self, input_data: Any) -> AdapterResult:
        if input_data.endswith(".xml"):
            return self._parse_apple_health(input_data)
        return self._parse_google_fit(input_data)

    def _parse_apple_health(self, filepath: str) -> AdapterResult:
        tree = ET.parse(filepath)
        root = tree.getroot()

        identity = PatientIdentity(source_id="apple_health", source_system="apple_health")
        me = root.find(".//Me")
        if me is not None:
            dob = me.get("HKCharacteristicTypeIdentifierDateOfBirth")
            if dob:
                identity.birth_date = dob
            sex = me.get("HKCharacteristicTypeIdentifierBiologicalSex")
            if sex:
                identity.gender = {"HKBiologicalSexMale": "male", "HKBiologicalSexFemale": "female"}.get(sex, "unknown")
            name = me.get("HKCharacteristicTypeIdentifierName")
            if name:
                identity.full_name = name
                parts = name.split()
                if len(parts) >= 2:
                    identity.given_name, identity.family_name = parts[0], parts[-1]

        mrn_meta = root.find('.//MetadataEntry[@key="MRN"]')
        if mrn_meta is not None:
            identity.mrn = mrn_meta.get("value")

        patient = make_patient(identity)
        patient_ref = f"Patient/{patient.id}"
        resources = []

        for record in root.findall(".//Record"):
            rec_type = record.get("type", "")
            value_str = record.get("value")
            start_date = record.get("startDate", "")
            if rec_type not in cfg.HEALTHKIT_TO_LOINC or value_str is None:
                continue
            try:
                value = float(value_str)
            except (ValueError, TypeError):
                continue
            loinc = cfg.HEALTHKIT_TO_LOINC[rec_type]
            unit_display, ucum_code = cfg.HEALTHKIT_UNITS.get(rec_type, ("", ""))
            effective_dt = self._apple_date_to_iso(start_date)
            resources.append(make_observation_vital(patient_ref, loinc, value, unit_display, ucum_code, effective_dt))

        return AdapterResult(
            patient_identity=identity, fhir_resources=resources,
            fhir_patient=patient, source_type=self.source_type,
        )

    def _parse_google_fit(self, filepath: str) -> AdapterResult:
        with open(filepath, "r") as f:
            data = json.load(f)

        identity = PatientIdentity(source_id="google_fit", source_system="google_fit")
        profile = data.get("profile", {})
        if profile:
            identity.full_name = profile.get("name")
            identity.birth_date = profile.get("birthDate")
            identity.gender = profile.get("gender")
            identity.mrn = profile.get("mrn")
            if identity.full_name:
                parts = identity.full_name.split()
                if len(parts) >= 2:
                    identity.given_name, identity.family_name = parts[0], parts[-1]

        patient = make_patient(identity)
        patient_ref = f"Patient/{patient.id}"
        resources = []

        for dp in data.get("dataPoints", []):
            data_type = dp.get("dataTypeName", "")
            if data_type not in cfg.GOOGLE_FIT_TO_LOINC:
                continue
            loinc = cfg.GOOGLE_FIT_TO_LOINC[data_type]
            unit_display, ucum_code = cfg.GOOGLE_FIT_UNITS.get(data_type, ("", ""))
            ts = dp.get("timestamp", "2026-01-01T00:00:00Z")
            values = dp.get("value", [])
            if not values:
                continue
            if data_type == "com.google.blood_pressure" and len(values) >= 2:
                resources.append(make_observation_bp(patient_ref, values[0]["fpVal"], values[1]["fpVal"], ts))
            else:
                val = values[0].get("fpVal") or values[0].get("intVal", 0)
                resources.append(make_observation_vital(patient_ref, loinc, float(val), unit_display, ucum_code, ts))

        return AdapterResult(
            patient_identity=identity, fhir_resources=resources,
            fhir_patient=patient, source_type=self.source_type,
        )

    @staticmethod
    def _apple_date_to_iso(date_str: str) -> str:
        if not date_str:
            return "2026-01-01T00:00:00Z"
        try:
            dt = datetime.strptime(date_str.strip(), "%Y-%m-%d %H:%M:%S %z")
            return dt.isoformat()
        except ValueError:
            try:
                dt = datetime.strptime(date_str.strip()[:19], "%Y-%m-%d %H:%M:%S")
                return dt.isoformat() + "Z"
            except ValueError:
                return date_str
