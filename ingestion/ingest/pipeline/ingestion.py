"""Pipeline orchestrator: adapters -> patient linker -> FHIR bundler."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fhir.resources.R4B.bundle import Bundle

from ingest.core.base_adapter import BaseAdapter, AdapterResult
from ingest.core.patient_linker import PatientLinker
from ingest.core.bundler import FHIRBundler
from ingest.adapters.wearable_adapter import WearableAdapter
from ingest.adapters.ambulance_adapter import AmbulanceAdapter
from ingest.adapters.ehr_adapter import EHRAdapter
from ingest.adapters.handwritten_adapter import HandwrittenAdapter
from ingest.adapters.realtime_vitals_adapter import RealtimeVitalsAdapter
from ingest.adapters.scans_labs_adapter import ScansLabsAdapter
from ingest.api.vlm_client import MockVLMClient


class IngestionPipeline:
    """Orchestrates multi-source data ingestion into per-patient FHIR Bundles."""

    def __init__(self, adapters: list[BaseAdapter] | None = None):
        self.adapters = adapters or [
            EHRAdapter(),
            WearableAdapter(),
            AmbulanceAdapter(),
            RealtimeVitalsAdapter(),
            ScansLabsAdapter(),
            HandwrittenAdapter(vlm_client=MockVLMClient()),
        ]
        self.linker = PatientLinker()
        self.bundler = FHIRBundler()

    def ingest_file(self, filepath: str) -> AdapterResult | None:
        """Route a single file to the appropriate adapter."""
        for adapter in self.adapters:
            if adapter.supports(filepath):
                return adapter.parse(filepath)
        return None

    def ingest_directory(self, dirpath: str) -> list[Bundle]:
        """Process all files in a directory, link patients, create bundles."""
        results: list[AdapterResult] = []
        input_path = Path(dirpath)

        for file in sorted(input_path.rglob("*")):
            if not file.is_file():
                continue
            # Skip hidden files and __pycache__
            if any(part.startswith('.') or part == '__pycache__' for part in file.parts):
                continue

            result = self.ingest_file(str(file))
            if result:
                results.append(result)
                print(f"  Parsed: {file.name} ({result.source_type}) -> "
                      f"{len(result.fhir_resources)} resources")

        # Link patients
        for result in results:
            self.linker.ingest(result)

        linked = self.linker.get_all_patients()
        print(f"\n  Linked {len(results)} sources -> {len(linked)} patient(s)")

        # Create bundles
        bundles = []
        for lp in linked:
            bundle = self.bundler.create_patient_bundle(lp)
            bundles.append(bundle)
            name = "Unknown"
            if lp.fhir_patient and lp.fhir_patient.name:
                n = lp.fhir_patient.name[0]
                name = f"{n.given[0] if n.given else ''} {n.family or ''}".strip()
            print(f"  Bundle: {name} ({len(bundle.entry)} entries from {lp.source_types})")

        return bundles

    def run(self, input_dir: str, output_dir: str) -> list[str]:
        """Full pipeline: ingest -> link -> bundle -> write. Returns output file paths."""
        print(f"Ingesting from: {input_dir}")
        bundles = self.ingest_directory(input_dir)

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        output_files = []
        for i, bundle in enumerate(bundles):
            # Use patient name for filename
            name = f"patient_{i}"
            if bundle.entry and bundle.entry[0].resource:
                patient = bundle.entry[0].resource
                if hasattr(patient, 'name') and patient.name:
                    n = patient.name[0]
                    parts = []
                    if n.given:
                        parts.extend(n.given)
                    if n.family:
                        parts.append(n.family)
                    if parts:
                        name = "_".join(parts).lower().replace(" ", "_")

            filepath = output_path / f"{name}.fhir.json"
            filepath.write_text(bundle.json(indent=2))
            output_files.append(str(filepath))
            print(f"  Wrote: {filepath}")

        print(f"\nDone! {len(bundles)} patient bundle(s) written to {output_dir}")
        return output_files


def main():
    parser = argparse.ArgumentParser(description="Patient.ly FHIR Data Ingestion Pipeline")
    parser.add_argument("--input", "-i", required=True, help="Input directory with source data files")
    parser.add_argument("--output", "-o", required=True, help="Output directory for FHIR bundles")
    args = parser.parse_args()

    pipeline = IngestionPipeline()
    pipeline.run(args.input, args.output)


if __name__ == "__main__":
    main()
