"""Wearable data simulator - generates Apple Health XML + Google Fit JSON."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree

from patiently.simulators.base_simulator import BaseSimulator, PatientProfile, ClinicalScenario


class WearableSimulator(BaseSimulator):

    def generate(self, profile: PatientProfile, scenario: ClinicalScenario, output_dir: Path) -> Path:
        wearables_dir = output_dir / "wearables"
        wearables_dir.mkdir(parents=True, exist_ok=True)
        self._generate_apple_health(profile, scenario, wearables_dir)
        self._generate_google_fit(profile, scenario, wearables_dir)
        return wearables_dir

    def _generate_apple_health(self, profile, scenario, out_dir):
        root = Element("HealthData", locale="en_IN")
        SubElement(root, "ExportDate", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S +0530"))
        SubElement(root, "Me", **{
            "HKCharacteristicTypeIdentifierName": profile.name,
            "HKCharacteristicTypeIdentifierDateOfBirth": profile.dob,
            "HKCharacteristicTypeIdentifierBiologicalSex": "HKBiologicalSexMale" if profile.gender == "male" else "HKBiologicalSexFemale",
        })
        SubElement(root, "MetadataEntry", key="MRN", value=profile.mrn)

        ist = timezone(timedelta(hours=5, minutes=30))
        base_time = datetime(2026, 2, 14, 10, 0, 0, tzinfo=ist)

        for i in range(24):
            ts = base_time - timedelta(minutes=30 * (23 - i))
            progress = i / 23.0
            hr = 72 + (scenario.baseline_hr - 72) * progress
            spo2 = 99 - (99 - scenario.baseline_spo2) * progress
            temp = 36.5 + (scenario.baseline_temp - 36.5) * progress
            rr = 14 + (scenario.baseline_rr - 14) * progress
            ts_str = ts.strftime("%Y-%m-%d %H:%M:%S %z")

            SubElement(root, "Record", type="HKQuantityTypeIdentifierHeartRate",
                       sourceName="Apple Watch", value=f"{hr:.0f}", unit="count/min",
                       startDate=ts_str, endDate=ts_str)
            if i % 3 == 0:
                SubElement(root, "Record", type="HKQuantityTypeIdentifierOxygenSaturation",
                           sourceName="Apple Watch", value=f"{spo2:.0f}", unit="%",
                           startDate=ts_str, endDate=ts_str)
            if i % 4 == 0:
                SubElement(root, "Record", type="HKQuantityTypeIdentifierBodyTemperature",
                           sourceName="Apple Watch", value=f"{temp:.1f}", unit="degC",
                           startDate=ts_str, endDate=ts_str)
            if i % 3 == 0:
                SubElement(root, "Record", type="HKQuantityTypeIdentifierRespiratoryRate",
                           sourceName="Apple Watch", value=f"{rr:.0f}", unit="count/min",
                           startDate=ts_str, endDate=ts_str)

        tree = ElementTree(root)
        tree.write(str(out_dir / "sim_apple_health.xml"), encoding="unicode", xml_declaration=True)

    def _generate_google_fit(self, profile, scenario, out_dir):
        base_time = datetime(2026, 2, 14, 10, 0, 0)
        data_points = []
        for i in range(12):
            ts = base_time - timedelta(hours=11 - i)
            progress = i / 11.0
            hr = 72 + (scenario.baseline_hr - 72) * progress
            spo2 = 99 - (99 - scenario.baseline_spo2) * progress
            data_points.append({
                "dataTypeName": "com.google.heart_rate.bpm",
                "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "value": [{"fpVal": round(hr, 1)}],
            })
            if i % 2 == 0:
                data_points.append({
                    "dataTypeName": "com.google.oxygen_saturation",
                    "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "value": [{"fpVal": round(spo2, 1)}],
                })
        output = {
            "source_type": "google_fit",
            "profile": {"name": profile.name, "birthDate": profile.dob, "gender": profile.gender},
            "dataPoints": data_points,
        }
        (out_dir / "sim_google_fit.json").write_text(json.dumps(output, indent=2))
