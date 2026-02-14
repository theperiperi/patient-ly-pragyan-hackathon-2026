"""Hospital EHR data simulator - generates HL7 v2 messages."""

from __future__ import annotations

from pathlib import Path

from ingest.simulators.base_simulator import BaseSimulator, PatientProfile, ClinicalScenario


class EHRSimulator(BaseSimulator):

    def generate(self, profile: PatientProfile, scenario: ClinicalScenario, output_dir: Path) -> Path:
        ehr_dir = output_dir / "ehr"
        ehr_dir.mkdir(parents=True, exist_ok=True)

        dob_hl7 = profile.dob.replace("-", "")
        gender_code = "M" if profile.gender == "male" else "F"
        ts = "20260214120000"

        adt = (
            f"MSH|^~\\&|HIS|AIIMS_DELHI|PATIENTLY|FHIR|{ts}||ADT^A01|SIM_ADT001|P|2.5\r"
            f"EVN|A01|{ts}\r"
            f"PID|||{profile.mrn}||{profile.family_name}^{profile.given_name}||{dob_hl7}|{gender_code}|||{profile.address}||{profile.phone}\r"
            f"PV1||E|ED^^^AIIMS||||DR001^Sharma^Anita|||||||||||VN_SIM001|||||||||||||||||||||||||{ts}\r"
        )
        for i, dx in enumerate(scenario.diagnoses, 1):
            system = "I10" if dx["code"][0].isalpha() else "SCT"
            adt += f"DG1|{i}||{dx['code']}^{dx['display']}^{system}|||A\r"
        vitals = [
            ("8867-4", "Heart rate", f"{scenario.baseline_hr:.0f}", "/min", "60-100"),
            ("8480-6", "Systolic blood pressure", f"{scenario.baseline_bp_sys:.0f}", "mm[Hg]", "90-140"),
            ("8462-4", "Diastolic blood pressure", f"{scenario.baseline_bp_dia:.0f}", "mm[Hg]", "60-90"),
            ("2708-6", "Oxygen saturation", f"{scenario.baseline_spo2:.0f}", "%", "95-100"),
            ("8310-5", "Body temperature", f"{scenario.baseline_temp:.1f}", "Cel", "36.5-37.5"),
            ("9279-1", "Respiratory rate", f"{scenario.baseline_rr:.0f}", "/min", "12-20"),
        ]
        for j, (code, display, val, unit, ref) in enumerate(vitals, 1):
            adt += f"OBX|{j}|NM|{code}^{display}^LN||{val}|{unit}|{ref}||||F\r"
        (ehr_dir / "sim_admission.hl7").write_text(adt)

        oru = (
            f"MSH|^~\\&|LAB|AIIMS_DELHI|PATIENTLY|FHIR|{ts}||ORU^R01|SIM_ORU001|P|2.5\r"
            f"PID|||{profile.mrn}||{profile.family_name}^{profile.given_name}||{dob_hl7}|{gender_code}\r"
            f"OBR|1||SIM_LAB001|24331-1^Comprehensive metabolic panel^LN|||{ts}\r"
        )
        for k, lab in enumerate(scenario.labs, 1):
            oru += f"OBX|{k}|NM|{lab['code']}^{lab['name']}^LN||{lab['value']}|{lab['unit']}|{lab['ref_low']}-{lab['ref_high']}||||F\r"
        (ehr_dir / "sim_lab_results.hl7").write_text(oru)

        return ehr_dir
