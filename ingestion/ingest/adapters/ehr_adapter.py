"""Hospital EHR adapter - parses HL7 v2 pipe-delimited messages into FHIR R4."""

from __future__ import annotations

import os
from typing import Any

import hl7

from ingest.core.base_adapter import BaseAdapter, PatientIdentity, AdapterResult
from ingest.core.fhir_helpers import (
    make_patient, make_observation_vital, make_observation_lab,
    make_encounter, make_condition, make_diagnostic_report,
)
from ingest import config as cfg


class EHRAdapter(BaseAdapter):
    """Parses HL7 v2 messages (ADT, ORU) into FHIR resources."""

    @property
    def source_type(self) -> str:
        return "hospital_ehr"

    def supports(self, input_data: Any) -> bool:
        if isinstance(input_data, str) and os.path.isfile(input_data):
            if input_data.endswith(".hl7"):
                return True
            try:
                with open(input_data, "r") as f:
                    return f.readline().startswith("MSH|")
            except Exception:
                return False
        if isinstance(input_data, str) and input_data.strip().startswith("MSH|"):
            return True
        return False

    def parse(self, input_data: Any) -> AdapterResult:
        if isinstance(input_data, str) and os.path.isfile(input_data):
            with open(input_data, "r") as f:
                raw = f.read()
        else:
            raw = input_data

        # HL7 v2 uses \r as segment separator; normalize from \n if needed
        if "\r" not in raw and "\n" in raw:
            raw = raw.replace("\n", "\r")

        msg = hl7.parse(raw)
        resources = []

        identity = self._parse_pid(msg)
        fhir_patient = make_patient(identity)
        patient_ref = f"Patient/{fhir_patient.id}"

        # PV1 -> Encounter
        try:
            pv1 = msg.segment("PV1")
            patient_class = str(pv1[2]) if len(pv1) > 2 else "E"
            class_map = {
                "I": ("IMP", "inpatient"),
                "O": ("AMB", "ambulatory"),
                "E": ("EMER", "emergency"),
            }
            cls_code, cls_display = class_map.get(patient_class, ("AMB", "ambulatory"))
            admit_dt = str(pv1[44]) if len(pv1) > 44 and str(pv1[44]) else None
            start = self._parse_hl7_datetime(admit_dt) if admit_dt else "2026-01-01T00:00:00Z"
            enc = make_encounter(patient_ref, cls_code, cls_display, start)
            resources.append(enc)
        except (KeyError, IndexError):
            pass

        # OBX -> Observations
        try:
            for seg in msg.segments("OBX"):
                obs = self._parse_obx(seg, patient_ref)
                if obs:
                    resources.append(obs)
        except (KeyError, IndexError):
            pass

        # DG1 -> Conditions
        try:
            for seg in msg.segments("DG1"):
                cond = self._parse_dg1(seg, patient_ref)
                if cond:
                    resources.append(cond)
        except (KeyError, IndexError):
            pass

        # OBR + OBX -> DiagnosticReport
        try:
            obr = msg.segment("OBR")
            obr_code = str(obr[4][0][0]) if len(obr) > 4 else ""
            obr_display = str(obr[4][0][1]) if len(obr) > 4 and len(obr[4][0]) > 1 else "Lab Report"
            obs_refs = [
                f"Observation/{r.id}"
                for r in resources
                if r.get_resource_type() == "Observation"
            ]
            if obs_refs:
                dr = make_diagnostic_report(
                    patient_ref, "LAB", "Laboratory", (obr_code, obr_display),
                    result_refs=obs_refs,
                )
                resources.append(dr)
        except (KeyError, IndexError):
            pass

        return AdapterResult(
            patient_identity=identity,
            fhir_resources=resources,
            fhir_patient=fhir_patient,
            source_type=self.source_type,
        )

    def _parse_pid(self, msg) -> PatientIdentity:
        try:
            pid = msg.segment("PID")
        except KeyError:
            return PatientIdentity(source_id="unknown", source_system=self.source_type)

        mrn = str(pid[3]) if len(pid) > 3 else None
        if mrn and "^" in mrn:
            mrn = mrn.split("^")[0]

        name_field = str(pid[5]) if len(pid) > 5 else ""
        parts = name_field.split("^")
        family = parts[0] if parts else None
        given = parts[1] if len(parts) > 1 else None

        dob = str(pid[7]) if len(pid) > 7 else None
        if dob and len(dob) >= 8:
            dob = f"{dob[:4]}-{dob[4:6]}-{dob[6:8]}"

        gender_raw = str(pid[8]) if len(pid) > 8 else None
        gender_map = {"M": "male", "F": "female", "O": "other", "U": "unknown"}
        gender = gender_map.get(gender_raw, "unknown") if gender_raw else None

        phone = str(pid[13]) if len(pid) > 13 and str(pid[13]) else None

        return PatientIdentity(
            source_id=mrn or "unknown",
            source_system=self.source_type,
            family_name=family,
            given_name=given,
            full_name=f"{given} {family}" if given and family else family,
            birth_date=dob,
            gender=gender,
            mrn=mrn,
            phone=phone,
        )

    def _parse_obx(self, seg, patient_ref: str):
        try:
            value_type = str(seg[2]) if len(seg) > 2 else ""
            code_field = str(seg[3])
            code_parts = code_field.split("^")
            code = code_parts[0]
            display = code_parts[1] if len(code_parts) > 1 else code
            code_system = code_parts[2] if len(code_parts) > 2 else cfg.LOINC_SYSTEM
            if code_system == "LN":
                code_system = cfg.LOINC_SYSTEM

            value = str(seg[5]) if len(seg) > 5 else None
            units = str(seg[6]) if len(seg) > 6 else ""
            ref_range = str(seg[7]) if len(seg) > 7 else ""

            if value_type == "NM" and value:
                loinc_map = {
                    cfg.LOINC_HEART_RATE[0]: (cfg.LOINC_HEART_RATE, "beats/minute", cfg.UCUM_BPM),
                    cfg.LOINC_SPO2[0]: (cfg.LOINC_SPO2, "%", cfg.UCUM_PERCENT),
                    cfg.LOINC_BODY_TEMP[0]: (cfg.LOINC_BODY_TEMP, "degC", cfg.UCUM_CELSIUS),
                    cfg.LOINC_RESP_RATE[0]: (cfg.LOINC_RESP_RATE, "breaths/minute", cfg.UCUM_BPM),
                }
                if code in loinc_map:
                    loinc, unit_display, ucum = loinc_map[code]
                    return make_observation_vital(
                        patient_ref, loinc, float(value), unit_display, ucum,
                        "2026-02-14T12:00:00Z",
                    )
                else:
                    ref_low, ref_high = None, None
                    if ref_range and "-" in ref_range:
                        rr_parts = ref_range.split("-")
                        try:
                            ref_low = float(rr_parts[0])
                            ref_high = float(rr_parts[1])
                        except ValueError:
                            pass
                    return make_observation_lab(
                        patient_ref, (code, display), float(value),
                        units, units, "2026-02-14T12:00:00Z",
                        reference_range_low=ref_low, reference_range_high=ref_high,
                    )
        except Exception:
            return None

    def _parse_dg1(self, seg, patient_ref: str):
        try:
            code_field = str(seg[3]) if len(seg) > 3 else ""
            parts = code_field.split("^")
            code = parts[0]
            display = parts[1] if len(parts) > 1 else code
            system_id = parts[2] if len(parts) > 2 else ""
            system = cfg.ICD10_SYSTEM if system_id in ("I10", "ICD10") else cfg.SNOMED_SYSTEM
            return make_condition(patient_ref, code, display, system)
        except Exception:
            return None

    @staticmethod
    def _parse_hl7_datetime(dt_str: str) -> str:
        if not dt_str or len(dt_str) < 8:
            return "2026-01-01T00:00:00Z"
        dt_str = dt_str.strip()
        y, m, d = dt_str[:4], dt_str[4:6], dt_str[6:8]
        h = dt_str[8:10] if len(dt_str) > 9 else "00"
        mi = dt_str[10:12] if len(dt_str) > 11 else "00"
        s = dt_str[12:14] if len(dt_str) > 13 else "00"
        return f"{y}-{m}-{d}T{h}:{mi}:{s}Z"
