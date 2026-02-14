"""Real-time vitals adapter - parses bedside monitor JSON and ECG waveform CSV."""

from __future__ import annotations

import csv
import json
import os
from typing import Any

from ingest.core.base_adapter import BaseAdapter, PatientIdentity, AdapterResult
from ingest.core.fhir_helpers import (
    make_patient, make_observation_vital, make_observation_bp, make_observation_sampled_data,
)
from ingest import config as cfg


class RealtimeVitalsAdapter(BaseAdapter):

    @property
    def source_type(self) -> str:
        return "realtime_vitals"

    def supports(self, input_data: Any) -> bool:
        if not isinstance(input_data, str) or not os.path.isfile(input_data):
            return False
        if input_data.endswith(".json"):
            try:
                with open(input_data, "r") as f:
                    data = json.load(f)
                return "readings" in data and "device" in data
            except Exception:
                return False
        if input_data.endswith(".csv"):
            try:
                with open(input_data, "r") as f:
                    header = f.readline().lower()
                return "ecg" in header or "waveform" in header or "lead" in header
            except Exception:
                return False
        return False

    def parse(self, input_data: Any) -> AdapterResult:
        if input_data.endswith(".json"):
            return self._parse_numeric(input_data)
        return self._parse_waveform(input_data)

    def _parse_numeric(self, filepath: str) -> AdapterResult:
        with open(filepath, "r") as f:
            data = json.load(f)

        pid = data.get("patient_id", "unknown")
        identity = PatientIdentity(
            source_id=pid, source_system=self.source_type,
            mrn=pid if pid.startswith("MRN") else None,
            full_name=data.get("patient_name"),
        )
        if identity.full_name:
            parts = identity.full_name.split()
            if len(parts) >= 2:
                identity.given_name, identity.family_name = parts[0], parts[-1]

        patient = make_patient(identity)
        patient_ref = f"Patient/{patient.id}"
        resources = []

        for r in data.get("readings", []):
            ts = r.get("timestamp", "2026-01-01T00:00:00Z")
            if r.get("heart_rate") is not None:
                resources.append(make_observation_vital(patient_ref, cfg.LOINC_HEART_RATE, float(r["heart_rate"]), "beats/minute", cfg.UCUM_BPM, ts))
            if r.get("spo2") is not None:
                resources.append(make_observation_vital(patient_ref, cfg.LOINC_SPO2, float(r["spo2"]), "%", cfg.UCUM_PERCENT, ts))
            if r.get("bp_sys") is not None and r.get("bp_dia") is not None:
                resources.append(make_observation_bp(patient_ref, float(r["bp_sys"]), float(r["bp_dia"]), ts))
            if r.get("resp_rate") is not None:
                resources.append(make_observation_vital(patient_ref, cfg.LOINC_RESP_RATE, float(r["resp_rate"]), "breaths/minute", cfg.UCUM_BPM, ts))
            if r.get("temp") is not None:
                resources.append(make_observation_vital(patient_ref, cfg.LOINC_BODY_TEMP, float(r["temp"]), "degC", cfg.UCUM_CELSIUS, ts))

        return AdapterResult(patient_identity=identity, fhir_resources=resources, fhir_patient=patient, source_type=self.source_type)

    def _parse_waveform(self, filepath: str) -> AdapterResult:
        identity = PatientIdentity(source_id="waveform", source_system=self.source_type)
        with open(filepath, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        if not rows:
            patient = make_patient(identity)
            return AdapterResult(patient_identity=identity, fhir_resources=[], fhir_patient=patient, source_type=self.source_type)

        first = rows[0]
        if "patient_id" in first:
            identity.source_id = first["patient_id"]
            if first["patient_id"].startswith("MRN"):
                identity.mrn = first["patient_id"]
        if "patient_name" in first and first["patient_name"]:
            identity.full_name = first["patient_name"]
            parts = first["patient_name"].split()
            if len(parts) >= 2:
                identity.given_name, identity.family_name = parts[0], parts[-1]

        patient = make_patient(identity)
        patient_ref = f"Patient/{patient.id}"

        ecg_values = []
        timestamps = []
        for row in rows:
            ecg_val = row.get("ecg_lead_ii") or row.get("ecg")
            if ecg_val is not None:
                try:
                    ecg_values.append(float(ecg_val))
                    timestamps.append(row.get("timestamp", ""))
                except ValueError:
                    pass

        resources = []
        if ecg_values:
            data_string = " ".join(str(v) for v in ecg_values)
            effective_dt = timestamps[0] if timestamps else "2026-01-01T00:00:00Z"
            ecg_loinc = ("131328", "MDC ECG lead II")
            resources.append(make_observation_sampled_data(patient_ref, ecg_loinc, data_string, 4.0, 1, effective_dt))

        return AdapterResult(patient_identity=identity, fhir_resources=resources, fhir_patient=patient, source_type=self.source_type)
