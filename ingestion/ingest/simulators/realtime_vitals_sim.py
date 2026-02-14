"""Real-time vitals simulator - generates bedside monitor JSON + ECG CSV."""

from __future__ import annotations

import csv
import json
import math
from datetime import datetime, timedelta
from pathlib import Path

from ingest.simulators.base_simulator import BaseSimulator, PatientProfile, ClinicalScenario


class RealtimeVitalsSimulator(BaseSimulator):

    def generate(self, profile: PatientProfile, scenario: ClinicalScenario, output_dir: Path) -> Path:
        vitals_dir = output_dir / "realtime_vitals"
        vitals_dir.mkdir(parents=True, exist_ok=True)
        self._generate_numeric(profile, scenario, vitals_dir)
        self._generate_waveform(profile, scenario, vitals_dir)
        return vitals_dir

    def _generate_numeric(self, profile, scenario, out_dir):
        base = datetime(2026, 2, 14, 10, 35, 0)
        readings = []
        for i in range(8):
            ts = base + timedelta(minutes=5 * i)
            factor = 1.0 - (i * 0.03) if scenario.vital_trend == "improving" else 1.0
            readings.append({
                "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "heart_rate": round(scenario.baseline_hr * factor),
                "spo2": min(100, round(scenario.baseline_spo2 + i * 0.3)),
                "bp_sys": round(scenario.baseline_bp_sys * factor),
                "bp_dia": round(scenario.baseline_bp_dia * factor),
                "resp_rate": max(12, round(scenario.baseline_rr * factor)),
                "temp": round(scenario.baseline_temp - i * 0.02, 1),
            })
        output = {
            "device": "Philips IntelliVue MX800",
            "patient_id": profile.mrn,
            "patient_name": profile.name,
            "location": "ED Bed 3",
            "readings": readings,
        }
        (out_dir / "sim_bedside_stream.json").write_text(json.dumps(output, indent=2))

    def _generate_waveform(self, profile, scenario, out_dir):
        filepath = out_dir / "sim_ecg_waveform.csv"
        sample_rate = 250
        duration_sec = 2.0
        num_samples = int(sample_rate * duration_sec)
        hr = scenario.baseline_hr
        beat_period = 60.0 / hr
        base_time = datetime(2026, 2, 14, 10, 35, 0)

        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "patient_id", "ecg_lead_ii"])
            for i in range(num_samples):
                t = i / sample_rate
                ts = base_time + timedelta(seconds=t)
                phase = (t % beat_period) / beat_period
                ecg = _pqrst(phase)
                writer.writerow([
                    ts.strftime("%Y-%m-%dT%H:%M:%S.") + f"{int(t*1000)%1000:03d}Z",
                    profile.mrn,
                    f"{ecg:.3f}",
                ])


def _pqrst(phase: float) -> float:
    """Generate a simplified PQRST ECG waveform value given phase (0-1)."""
    if phase < 0.10:
        return 0.15 * math.sin(math.pi * phase / 0.10)
    elif phase < 0.16:
        return 0.0
    elif phase < 0.20:
        return -0.15 * math.sin(math.pi * (phase - 0.16) / 0.04)
    elif phase < 0.28:
        return 1.2 * math.sin(math.pi * (phase - 0.20) / 0.08)
    elif phase < 0.34:
        return -0.3 * math.sin(math.pi * (phase - 0.28) / 0.06)
    elif phase < 0.44:
        return 0.05
    elif phase < 0.60:
        return 0.25 * math.sin(math.pi * (phase - 0.44) / 0.16)
    else:
        return 0.0
