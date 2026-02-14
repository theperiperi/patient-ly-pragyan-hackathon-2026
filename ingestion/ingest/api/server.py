"""FastAPI server for the FHIR ingestion pipeline."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ingest.pipeline.ingestion import IngestionPipeline
from ingest.simulators.synthea_generator import SyntheaGenerator
from ingest.simulators.runner import _run_sims_for_patient

app = FastAPI(
    title="Patient.ly FHIR Ingestion API",
    description="Multi-source health data ingestion pipeline that converts to FHIR R4",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = IngestionPipeline()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ingest-fhir-ingestion"}


@app.post("/ingest")
async def ingest_files(files: list[UploadFile] = File(...)):
    """Ingest multiple files, link patients, return per-patient FHIR Bundles."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save uploaded files to temp directory
        for upload in files:
            filepath = Path(tmpdir) / upload.filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            content = await upload.read()
            filepath.write_bytes(content)

        # Run pipeline
        local_pipeline = IngestionPipeline()
        bundles = local_pipeline.ingest_directory(tmpdir)

        # Serialize bundles
        result = []
        for bundle in bundles:
            bundle_dict = json.loads(bundle.json())
            patient_name = "Unknown"
            if bundle.entry and bundle.entry[0].resource:
                patient = bundle.entry[0].resource
                if hasattr(patient, 'name') and patient.name:
                    n = patient.name[0]
                    parts = []
                    if n.given:
                        parts.extend(n.given)
                    if n.family:
                        parts.append(n.family)
                    patient_name = " ".join(parts)

            result.append({
                "patient_name": patient_name,
                "entry_count": len(bundle.entry),
                "bundle": bundle_dict,
            })

        return JSONResponse(content={
            "patients": len(result),
            "bundles": result,
        })


@app.post("/ingest/file")
async def ingest_single_file(file: UploadFile = File(...)):
    """Ingest a single file, return parsed FHIR resources (no patient linking)."""
    with tempfile.NamedTemporaryFile(suffix=f"_{file.filename}", delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp.flush()

        result = pipeline.ingest_file(tmp.name)

    if result is None:
        return JSONResponse(
            status_code=400,
            content={"error": f"No adapter found for file: {file.filename}"},
        )

    resources = []
    for r in result.fhir_resources:
        resources.append(json.loads(r.json()))

    patient_dict = json.loads(result.fhir_patient.json()) if result.fhir_patient else None

    return JSONResponse(content={
        "source_type": result.source_type,
        "patient_identity": {
            "full_name": result.patient_identity.full_name,
            "birth_date": result.patient_identity.birth_date,
            "gender": result.patient_identity.gender,
            "mrn": result.patient_identity.mrn,
        },
        "patient_resource": patient_dict,
        "resources_count": len(resources),
        "resources": resources,
    })


# Path to Synthea JAR — configurable via env var
SYNTHEA_JAR = os.environ.get(
    "SYNTHEA_JAR",
    str(Path(__file__).parent.parent.parent / "tools" / "synthea-with-dependencies.jar"),
)


@app.post("/generate")
async def generate_patient(population: int = Query(default=1, ge=1, le=20)):
    """Generate synthetic patient(s) via Synthea and run the full round-trip.

    1. Synthea JAR → FHIR R4 transaction bundles
    2. Extract PatientProfile + ClinicalScenario
    3. 6 simulators → native source files (HL7, XML, DICOM, PNG, PDF, CSV, JSON)
    4. Ingestion pipeline reads those source files back → consolidated FHIR bundles

    Returns the final FHIR bundles produced by the ingestion pipeline.
    """
    jar_path = SYNTHEA_JAR
    if not Path(jar_path).exists():
        return JSONResponse(
            status_code=500,
            content={"error": f"Synthea JAR not found at {jar_path}. Set SYNTHEA_JAR env var."},
        )

    with tempfile.TemporaryDirectory(prefix="synthea_gen_") as tmpdir:
        tmpdir = Path(tmpdir)

        # Step 1: Run Synthea JAR → FHIR bundles
        generator = SyntheaGenerator(synthea_jar_path=jar_path)
        generated_files = generator.generate_with_synthea(
            population=population,
            output_dir=str(tmpdir / "_synthea_raw"),
        )
        bundles_raw = generator.load_from_files(*generated_files)
        profiles_scenarios = generator.extract_profiles(bundles_raw)

        if not profiles_scenarios:
            return JSONResponse(
                status_code=500,
                content={"error": "Synthea generated no valid patient bundles"},
            )

        # Step 2 & 3: Run 6 simulators per patient → source files
        source_dir = tmpdir / "sources"
        for i, (profile, scenario) in enumerate(profiles_scenarios):
            safe_name = profile.name.replace(" ", "_").lower()
            patient_dir = source_dir / f"{safe_name}_{i:03d}"
            patient_dir.mkdir(parents=True, exist_ok=True)
            _run_sims_for_patient(profile, scenario, patient_dir)

        # Step 4: Ingest source files back through the pipeline → FHIR
        local_pipeline = IngestionPipeline()
        fhir_bundles = local_pipeline.ingest_directory(str(source_dir))

        # Serialize response
        result = []
        for bundle in fhir_bundles:
            bundle_dict = json.loads(bundle.json())
            patient_name = "Unknown"
            if bundle.entry and bundle.entry[0].resource:
                patient = bundle.entry[0].resource
                if hasattr(patient, "name") and patient.name:
                    n = patient.name[0]
                    parts = []
                    if n.given:
                        parts.extend(n.given)
                    if n.family:
                        parts.append(n.family)
                    patient_name = " ".join(parts)

            result.append({
                "patient_name": patient_name,
                "entry_count": len(bundle.entry),
                "bundle": bundle_dict,
            })

        return JSONResponse(content={
            "generated": len(profiles_scenarios),
            "ingested_bundles": len(result),
            "bundles": result,
        })
