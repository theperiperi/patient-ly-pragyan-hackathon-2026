"""Simulator runner - generates coherent sample data across all 6 sources."""

from __future__ import annotations

import argparse
from pathlib import Path

from ingest.simulators.base_simulator import PatientProfile, ClinicalScenario, SCENARIOS
from ingest.simulators.wearable_sim import WearableSimulator
from ingest.simulators.ambulance_sim import AmbulanceSimulator
from ingest.simulators.ehr_sim import EHRSimulator
from ingest.simulators.handwritten_sim import HandwrittenSimulator
from ingest.simulators.realtime_vitals_sim import RealtimeVitalsSimulator
from ingest.simulators.scans_labs_sim import ScansLabsSimulator


def run_simulators(
    scenario_name: str = "chest_pain",
    output_dir: str = "sample_data",
    patient_name: str | None = None,
    dob: str | None = None,
    gender: str | None = None,
) -> list[Path]:
    """Run all simulators for a given scenario."""
    scenario = SCENARIOS.get(scenario_name)
    if scenario is None:
        available = ", ".join(SCENARIOS.keys())
        raise ValueError(f"Unknown scenario '{scenario_name}'. Available: {available}")

    profile = PatientProfile()
    if patient_name:
        profile.name = patient_name
        parts = patient_name.split()
        if len(parts) >= 2:
            profile.given_name = parts[0]
            profile.family_name = parts[-1]
    if dob:
        profile.dob = dob
    if gender:
        profile.gender = gender

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    simulators = [
        WearableSimulator(),
        AmbulanceSimulator(),
        EHRSimulator(),
        HandwrittenSimulator(),
        RealtimeVitalsSimulator(),
        ScansLabsSimulator(),
    ]

    outputs = []
    for sim in simulators:
        name = sim.__class__.__name__
        print(f"  Running {name}...")
        try:
            result = sim.generate(profile, scenario, out)
            outputs.append(result)
            print(f"    -> {result}")
        except Exception as e:
            print(f"    -> ERROR: {e}")

    print(f"\nDone! Generated data for scenario '{scenario_name}' in {out}")
    return outputs


def main():
    parser = argparse.ArgumentParser(description="Generate coherent sample data across all 6 sources")
    parser.add_argument("--scenario", "-s", default="chest_pain",
                        choices=list(SCENARIOS.keys()),
                        help="Clinical scenario (default: chest_pain)")
    parser.add_argument("--output", "-o", default="sample_data",
                        help="Output directory (default: sample_data)")
    parser.add_argument("--patient-name", help="Override patient name")
    parser.add_argument("--dob", help="Override date of birth (YYYY-MM-DD)")
    parser.add_argument("--gender", help="Override gender (male/female)")
    args = parser.parse_args()

    run_simulators(args.scenario, args.output, args.patient_name, args.dob, args.gender)


if __name__ == "__main__":
    main()
