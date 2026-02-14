"""Ambulance/EMS adapter - parses NEMSIS-like XML into FHIR Encounter + Observations."""

from __future__ import annotations

import os
from typing import Any
from xml.etree import ElementTree as ET

from ingest.core.base_adapter import BaseAdapter, PatientIdentity, AdapterResult
from ingest.core.fhir_helpers import (
    make_patient, make_observation_vital, make_observation_bp, make_encounter,
)
from ingest import config as cfg


class AmbulanceAdapter(BaseAdapter):

    @property
    def source_type(self) -> str:
        return "ambulance_ems"

    def supports(self, input_data: Any) -> bool:
        if not isinstance(input_data, str) or not os.path.isfile(input_data):
            return False
        if not input_data.endswith(".xml"):
            return False
        try:
            tree = ET.parse(input_data)
            root = tree.getroot()
            tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
            return tag in ("EMSDataSet", "NEMSISDataSet", "EMSRecord")
        except Exception:
            return False

    def parse(self, input_data: Any) -> AdapterResult:
        tree = ET.parse(input_data)
        root = tree.getroot()
        ns = ""
        if "}" in root.tag:
            ns = root.tag.split("}")[0] + "}"

        identity = self._parse_patient(root, ns)
        patient = make_patient(identity)
        patient_ref = f"Patient/{patient.id}"
        resources = []

        dispatch = self._txt(root, f".//{ns}eTimes/{ns}eTimes.01")
        hospital = self._txt(root, f".//{ns}eTimes/{ns}eTimes.07")
        period_start = dispatch or "2026-01-01T00:00:00Z"

        enc = make_encounter(
            patient_ref, "EMER", "emergency", period_start, hospital,
            status="finished" if hospital else "in-progress",
        )
        resources.append(enc)

        for vg in root.findall(f".//{ns}eVitals/{ns}eVitals.VitalGroup"):
            ts = self._txt(vg, f"{ns}eVitals.01") or period_start
            hr = self._num(vg, f"{ns}eVitals.10")
            if hr is not None:
                resources.append(make_observation_vital(patient_ref, cfg.LOINC_HEART_RATE, hr, "beats/minute", cfg.UCUM_BPM, ts))
            sys_bp = self._num(vg, f"{ns}eVitals.06")
            dia_bp = self._num(vg, f"{ns}eVitals.07")
            if sys_bp is not None and dia_bp is not None:
                resources.append(make_observation_bp(patient_ref, sys_bp, dia_bp, ts))
            spo2 = self._num(vg, f"{ns}eVitals.12")
            if spo2 is not None:
                resources.append(make_observation_vital(patient_ref, cfg.LOINC_SPO2, spo2, "%", cfg.UCUM_PERCENT, ts))
            rr = self._num(vg, f"{ns}eVitals.14")
            if rr is not None:
                resources.append(make_observation_vital(patient_ref, cfg.LOINC_RESP_RATE, rr, "breaths/minute", cfg.UCUM_BPM, ts))
            temp = self._num(vg, f"{ns}eVitals.24")
            if temp is not None:
                resources.append(make_observation_vital(patient_ref, cfg.LOINC_BODY_TEMP, temp, "degC", cfg.UCUM_CELSIUS, ts))

        return AdapterResult(
            patient_identity=identity, fhir_resources=resources,
            fhir_patient=patient, source_type=self.source_type,
        )

    def _parse_patient(self, root, ns: str) -> PatientIdentity:
        family = self._txt(root, f".//{ns}ePatient/{ns}ePatient.PatientNameGroup/{ns}ePatient.01")
        given = self._txt(root, f".//{ns}ePatient/{ns}ePatient.PatientNameGroup/{ns}ePatient.02")
        dob = self._txt(root, f".//{ns}ePatient/{ns}ePatient.17")
        gc = self._txt(root, f".//{ns}ePatient/{ns}ePatient.13")
        gender = {"9906001": "male", "9906003": "female"}.get(gc, gc) if gc else None
        mrn = self._txt(root, f".//{ns}ePatient/{ns}ePatient.MRN")
        return PatientIdentity(
            source_id=self._txt(root, f".//{ns}ePatient/{ns}ePatient.15") or "ems-unknown",
            source_system=self.source_type,
            full_name=f"{given} {family}" if given and family else (given or family),
            given_name=given, family_name=family,
            birth_date=dob, gender=gender, mrn=mrn,
        )

    @staticmethod
    def _txt(root, path: str) -> str | None:
        el = root.find(path)
        return el.text.strip() if el is not None and el.text else None

    @staticmethod
    def _num(root, path: str) -> float | None:
        el = root.find(path)
        if el is not None and el.text:
            try:
                return float(el.text.strip())
            except ValueError:
                return None
        return None
