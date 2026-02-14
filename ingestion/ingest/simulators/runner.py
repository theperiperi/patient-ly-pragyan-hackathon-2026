"""Simulator runner - generates coherent sample data across all 6 sources.

Supports two modes:
  1. Static scenarios (original): pick from predefined clinical scenarios
  2. Dynamic Synthea mode: load Synthea FHIR bundles and extract realistic,
     randomized profiles/scenarios to drive the simulators
"""

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


ALL_SIMULATORS = [
    WearableSimulator,
    AmbulanceSimulator,
    EHRSimulator,
    HandwrittenSimulator,
    RealtimeVitalsSimulator,
    ScansLabsSimulator,
]


def _run_sims_for_patient(
    profile: PatientProfile,
    scenario: ClinicalScenario,
    output_dir: Path,
) -> list[Path]:
    """Run all 6 simulators for a single patient profile + scenario."""
    outputs = []
    for sim_cls in ALL_SIMULATORS:
        sim = sim_cls()
        name = sim.__class__.__name__
        print(f"  Running {name}...")
        try:
            result = sim.generate(profile, scenario, output_dir)
            outputs.append(result)
            print(f"    -> {result}")
        except Exception as e:
            print(f"    -> ERROR: {e}")
    return outputs


def run_simulators(
    scenario_name: str = "chest_pain",
    output_dir: str = "sample_data",
    patient_name: str | None = None,
    dob: str | None = None,
    gender: str | None = None,
) -> list[Path]:
    """Run all simulators for a given static scenario (original behavior)."""
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

    outputs = _run_sims_for_patient(profile, scenario, out)
    print(f"\nDone! Generated data for scenario '{scenario_name}' in {out}")
    return outputs


def run_synthea_simulators(
    synthea_paths: list[str | Path],
    output_dir: str = "sample_data",
    synthea_jar: str | None = None,
    population: int | None = None,
) -> list[Path]:
    """Generate dynamic data from Synthea FHIR bundles.

    Either loads pre-generated Synthea JSON files from synthea_paths,
    or runs Synthea JAR to generate them first (if synthea_jar is provided
    and population > 0).

    Each Synthea patient gets its own subdirectory with all 6 source types.
    """
    from ingest.simulators.synthea_generator import SyntheaGenerator

    generator = SyntheaGenerator(synthea_jar_path=synthea_jar)

    # If JAR is provided and population specified, generate fresh data
    if synthea_jar and population and population > 0:
        print(f"Running Synthea to generate {population} patients...")
        generated_files = generator.generate_with_synthea(
            population=population, output_dir=str(Path(output_dir) / "_synthea_raw")
        )
        synthea_paths = [str(f) for f in generated_files]
        print(f"  Generated {len(synthea_paths)} patient bundles")

    # Load bundles
    bundles = generator.load_from_files(*synthea_paths)
    if not bundles:
        print("No Synthea bundles found. Provide .json files or a directory.")
        return []

    print(f"Loaded {len(bundles)} Synthea patient bundle(s)")

    # Extract profiles and scenarios
    profiles_scenarios = generator.extract_profiles(bundles)
    print(f"Extracted {len(profiles_scenarios)} patient profile(s)")

    out = Path(output_dir)
    all_outputs = []

    for i, (profile, scenario) in enumerate(profiles_scenarios):
        safe_name = profile.name.replace(" ", "_").lower()
        patient_dir = out / f"{safe_name}_{i:03d}"
        patient_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n--- Patient {i+1}/{len(profiles_scenarios)}: "
              f"{profile.name} ({scenario.name}) ---")
        print(f"  DOB: {profile.dob} | Gender: {profile.gender}")
        print(f"  Chief complaint: {scenario.chief_complaint}")
        print(f"  Diagnoses: {len(scenario.diagnoses)} | Labs: {len(scenario.labs)} | "
              f"Meds: {len(scenario.medications)}")

        outputs = _run_sims_for_patient(profile, scenario, patient_dir)
        all_outputs.extend(outputs)

    print(f"\nDone! Generated data for {len(profiles_scenarios)} patient(s) in {out}")
    return all_outputs


def main():
    parser = argparse.ArgumentParser(
        description="Generate coherent sample data across all 6 sources.\n"
                    "Use --synthea to load Synthea FHIR bundles for dynamic generation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--scenario", "-s", default=None,
                      choices=list(SCENARIOS.keys()),
                      help="Static clinical scenario (default: chest_pain)")
    mode.add_argument("--synthea", nargs="+", metavar="PATH",
                      help="Synthea FHIR JSON file(s) or directory for dynamic generation")

    parser.add_argument("--output", "-o", default="sample_data",
                        help="Output directory (default: sample_data)")
    parser.add_argument("--patient-name", help="Override patient name (static mode only)")
    parser.add_argument("--dob", help="Override date of birth (static mode only)")
    parser.add_argument("--gender", help="Override gender (static mode only)")
    parser.add_argument("--synthea-jar", help="Path to Synthea JAR for live generation")
    parser.add_argument("--population", type=int,
                        help="Number of patients to generate with Synthea JAR")

    args = parser.parse_args()

    if args.synthea:
        run_synthea_simulators(
            synthea_paths=args.synthea,
            output_dir=args.output,
            synthea_jar=args.synthea_jar,
            population=args.population,
        )
    else:
        run_simulators(
            scenario_name=args.scenario or "chest_pain",
            output_dir=args.output,
            patient_name=args.patient_name,
            dob=args.dob,
            gender=args.gender,
        )


if __name__ == "__main__":
    main()
