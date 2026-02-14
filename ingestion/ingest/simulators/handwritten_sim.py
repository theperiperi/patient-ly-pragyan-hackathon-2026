"""Handwritten clinical note simulator - generates a PNG image + metadata sidecar."""

from __future__ import annotations

import json
from pathlib import Path

from ingest.simulators.base_simulator import BaseSimulator, PatientProfile, ClinicalScenario


class HandwrittenSimulator(BaseSimulator):

    def generate(self, profile: PatientProfile, scenario: ClinicalScenario, output_dir: Path) -> Path:
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            raise ImportError("Pillow is required. Install: pip install Pillow")

        hw_dir = output_dir / "handwritten"
        hw_dir.mkdir(parents=True, exist_ok=True)

        width, height = 800, 600
        img = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(img)

        for y in range(40, height, 28):
            draw.line([(60, y), (width - 40, y)], fill="#cccccc", width=1)
        draw.line([(55, 0), (55, height)], fill="#ffcccc", width=1)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except (OSError, IOError):
            font = ImageFont.load_default()

        age_str = ""
        if profile.dob:
            age_str = f"{2026 - int(profile.dob[:4])}y"
        gender_short = "M" if profile.gender == "male" else "F" if profile.gender == "female" else "O"

        lines = [
            f"Patient: {profile.name}, {gender_short}, {age_str}",
            f"MRN: {profile.mrn}",
            "Date: 14/02/2026",
            "",
            f"C/C: {scenario.chief_complaint}",
            "",
            "Vitals:",
            f"  HR: {scenario.baseline_hr:.0f} bpm  |  BP: {scenario.baseline_bp_sys:.0f}/{scenario.baseline_bp_dia:.0f} mmHg",
            f"  SpO2: {scenario.baseline_spo2:.0f}%    |  Temp: {scenario.baseline_temp}C",
            f"  RR: {scenario.baseline_rr:.0f}/min",
            "",
            "Assessment:",
        ]
        for dx in scenario.diagnoses:
            lines.append(f"  - {dx['display']}")
        lines.append("")
        lines.append("Plan:")
        for med in scenario.medications:
            lines.append(f"  - {med}")

        y = 48
        for line in lines:
            draw.text((65, y), line, fill="black", font=font)
            y += 28

        filepath = hw_dir / "sim_clinical_note.png"
        img.save(str(filepath))

        # Write sidecar metadata so MockVLMClient can return correct patient info
        sidecar = {
            "patient_name": profile.name,
            "age": f"{2026 - int(profile.dob[:4])}y" if profile.dob else None,
            "gender": profile.gender,
            "mrn": profile.mrn,
            "chief_complaint": scenario.chief_complaint,
            "vitals": {
                "heart_rate": scenario.baseline_hr,
                "blood_pressure_systolic": scenario.baseline_bp_sys,
                "blood_pressure_diastolic": scenario.baseline_bp_dia,
                "spo2": scenario.baseline_spo2,
                "temperature": scenario.baseline_temp,
                "respiratory_rate": scenario.baseline_rr,
            },
            "diagnoses": [
                {"code": dx["code"], "description": dx["display"]}
                for dx in scenario.diagnoses
            ],
            "medications": scenario.medications,
            "notes": f"Clinical note for {profile.name}",
        }
        (hw_dir / "sim_clinical_note.meta.json").write_text(json.dumps(sidecar, indent=2))

        return filepath
