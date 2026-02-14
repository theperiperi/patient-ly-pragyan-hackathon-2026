"""FastAPI server for the FHIR ingestion pipeline."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from patiently.pipeline.ingestion import IngestionPipeline

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
    return {"status": "healthy", "service": "patiently-fhir-ingestion"}


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
