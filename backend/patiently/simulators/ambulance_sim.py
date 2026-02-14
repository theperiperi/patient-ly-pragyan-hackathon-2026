"""Ambulance/EMS data simulator - generates NEMSIS-like XML."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree

from patiently.simulators.base_simulator import BaseSimulator, PatientProfile, ClinicalScenario


class AmbulanceSimulator(BaseSimulator):

    def generate(self, profile: PatientProfile, scenario: ClinicalScenario, output_dir: Path) -> Path:
        amb_dir = output_dir / "ambulance"
        amb_dir.mkdir(parents=True, exist_ok=True)

        ns = "http://www.nemsis.org/media/nemsis_v3/release-3.5.0/XSDs/NEMSIS_NAT_XSD/NEMSIS_NAT_v3.5.0.250403_20250403_XSD/"
        root = Element(f"{{{ns}}}EMSDataSet")
        pcr = SubElement(root, f"{{{ns}}}PatientCareReport")

        ep = SubElement(pcr, f"{{{ns}}}ePatient")
        png = SubElement(ep, f"{{{ns}}}ePatient.PatientNameGroup")
        SubElement(png, f"{{{ns}}}ePatient.01").text = profile.family_name
        SubElement(png, f"{{{ns}}}ePatient.02").text = profile.given_name
        SubElement(ep, f"{{{ns}}}ePatient.13").text = "9906001" if profile.gender == "male" else "9906003"
        SubElement(ep, f"{{{ns}}}ePatient.15").text = profile.abha_id
        SubElement(ep, f"{{{ns}}}ePatient.17").text = profile.dob
        SubElement(ep, f"{{{ns}}}ePatient.MRN").text = profile.mrn

        ist = timezone(timedelta(hours=5, minutes=30))
        dispatch = datetime(2026, 2, 14, 9, 45, 0, tzinfo=ist)
        arrival = dispatch + timedelta(minutes=45)

        times = SubElement(pcr, f"{{{ns}}}eTimes")
        SubElement(times, f"{{{ns}}}eTimes.01").text = dispatch.isoformat()
        SubElement(times, f"{{{ns}}}eTimes.07").text = arrival.isoformat()

        evitals = SubElement(pcr, f"{{{ns}}}eVitals")
        offsets = [5, 20, 40]
        hr_offsets = [8, 4, 0]

        for j, offset_min in enumerate(offsets):
            ts = dispatch + timedelta(minutes=offset_min)
            vg = SubElement(evitals, f"{{{ns}}}eVitals.VitalGroup")
            SubElement(vg, f"{{{ns}}}eVitals.01").text = ts.isoformat()
            SubElement(vg, f"{{{ns}}}eVitals.06").text = f"{scenario.baseline_bp_sys + 4 - j*2:.0f}"
            SubElement(vg, f"{{{ns}}}eVitals.07").text = f"{scenario.baseline_bp_dia + 2 - j:.0f}"
            SubElement(vg, f"{{{ns}}}eVitals.10").text = f"{scenario.baseline_hr + hr_offsets[j]:.0f}"
            SubElement(vg, f"{{{ns}}}eVitals.12").text = f"{scenario.baseline_spo2 - 1 + j*0.5:.0f}"
            SubElement(vg, f"{{{ns}}}eVitals.14").text = f"{scenario.baseline_rr + 2 - j:.0f}"
            if j < 2:
                SubElement(vg, f"{{{ns}}}eVitals.24").text = f"{scenario.baseline_temp:.1f}"

        filepath = amb_dir / "sim_ems_run.xml"
        ElementTree(root).write(str(filepath), encoding="unicode", xml_declaration=True)
        return filepath
