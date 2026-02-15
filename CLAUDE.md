# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Patient.ly** is a FHIR R4 data ingestion pipeline for healthcare data. It converts heterogeneous medical data from 6 different source types into standardized FHIR R4 JSON bundles (ABDM-compliant, NRCES India profiles). The system uses in-memory processing with cross-source patient linking and outputs per-patient Transaction Bundles.

## Repository Structure

This is a monorepo structured as follows:

```
patient-ly-pragyan-hackathon-2026/
├── ingestion/                    # FHIR data ingestion pipeline (Python)
│   ├── patiently/               # Main Python package
│   │   ├── adapters/            # 6 source-specific adapters
│   │   ├── api/                 # FastAPI server + VLM client
│   │   ├── core/                # Core pipeline logic (bundler, linker, base adapter)
│   │   ├── pipeline/            # Pipeline orchestrator + CLI entry point
│   │   └── simulators/          # Test data generators for 6 sources
│   ├── sample_data/             # Example medical data files
│   ├── tests/                   # Pytest test suite
│   ├── requirements.txt         # Python dependencies
│   └── schema.md               # COMPREHENSIVE schema reference (read this first!)
├── definitions.json/            # FHIR resource definitions (reference)
├── examples.json/               # FHIR example resources (reference)
└── synthea_sample_data_fhir_latest/  # Synthea-generated FHIR data (reference)
```

## Development Commands

### Setup
```bash
cd ingestion
pip install -r requirements.txt
```

### Run Pipeline (CLI)
```bash
# Process all files in a directory and output FHIR bundles
python -m patiently.pipeline.ingestion --input sample_data --output output/

# Or using the direct module path
python -m patiently.pipeline --input sample_data --output output/
```

### Run API Server
```bash
cd ingestion
uvicorn patiently.api.server:app --reload --port 8000

# Test endpoints:
# GET  /health
# POST /ingest          (multi-file upload, returns per-patient bundles)
# POST /ingest/file     (single file, returns parsed resources)
```

### Run Tests
```bash
cd ingestion
pytest                          # Run all tests
pytest -v                       # Verbose output
pytest tests/test_pipeline.py   # Run specific test file
pytest -k test_name            # Run tests matching pattern
```

### Generate Sample Data
```bash
cd ingestion
python -m patiently.simulators.runner --scenario chest_pain --output sample_data
```

## Architecture

### Core Pipeline Flow

1. **Adapters** (`patiently/adapters/`) — Parse source-specific formats into FHIR resources
   - Each adapter implements `BaseAdapter` interface with `parse()`, `supports()`, and `source_type`
   - Returns `AdapterResult` containing `PatientIdentity` + list of FHIR resources
   - 6 adapters: `WearableAdapter`, `AmbulanceAdapter`, `EHRAdapter`, `HandwrittenAdapter`, `RealtimeVitalsAdapter`, `ScansLabsAdapter`

2. **Patient Linker** (`patiently/core/patient_linker.py`) — Cross-source patient matching
   - Uses 4-tier deterministic matching: (1) MRN, (2) ABHA ID, (3) Name+DOB, (4) Phone/Email
   - Merges patient identities into `LinkedPatient` records
   - Consolidates FHIR resources from all sources for each patient

3. **Bundler** (`patiently/core/bundler.py`) — Creates per-patient FHIR Transaction Bundles
   - First entry is always the merged Patient resource
   - All other resources (Observations, Encounters, Conditions, etc.) reference the Patient via `fullUrl`
   - Output conforms to FHIR R4 Bundle type="transaction"

4. **Pipeline Orchestrator** (`patiently/pipeline/ingestion.py`) — Coordinates the full flow
   - `ingest_file()` — Route single file to appropriate adapter
   - `ingest_directory()` — Process all files in directory → link patients → create bundles
   - `run()` — Full pipeline with file I/O (input dir → output FHIR JSON files)

### Source Type to Adapter Mapping

| Source | Format | Adapter | FHIR Resources Produced |
|--------|--------|---------|------------------------|
| Wearables (Apple Health, Google Fit) | XML, JSON | `WearableAdapter` | `Observation` (vital-signs) |
| Ambulance (108 EMS) | NEMSIS XML | `AmbulanceAdapter` | `Encounter` + `Observation` |
| Hospital EHR | HL7 v2 (pipe-delimited) | `EHRAdapter` | `Encounter` + `Observation` + `Condition` + `DiagnosticReport` |
| Handwritten Notes | PNG/JPG images | `HandwrittenAdapter` | `DocumentReference` + extracted `Condition`/`Observation` (via VLM) |
| Real-Time Vitals | JSON (numeric) + CSV (waveform) | `RealtimeVitalsAdapter` | `Observation` (vital-signs + SampledData for ECG) |
| Scans & Lab Reports | DICOM + PDF | `ScansLabsAdapter` | `ImagingStudy` + `DiagnosticReport` + `DocumentReference` + `Observation` |

### Key Data Models

All internal data models are Python dataclasses defined in `patiently/core/base_adapter.py`:

- **`PatientIdentity`** — Extracted patient info for linking (source_id, source_system, name, DOB, MRN, ABHA ID, etc.)
- **`AdapterResult`** — Output from adapters (patient_identity, fhir_resources, fhir_patient, source_type, metadata)
- **`LinkedPatient`** — Unified patient from multiple sources (canonical_id, identities[], fhir_patient, all_resources[], source_types)

### FHIR Coding Systems

All FHIR resource coding is centralized in `patiently/config.py`:

- **LOINC** — Vital signs (HR, SpO2, BP, temp, RR), lab tests, document types
- **SNOMED-CT** — Clinical conditions, body sites
- **ICD-10** — Diagnosis codes
- **UCUM** — Units of measurement
- **NRCES India** — ABDM Patient profile
- **ABDM Health ID** — ABHA identifier system

See `ingestion/schema.md` for the complete schema reference including all LOINC codes, UCUM units, and FHIR resource structures.

## Important Implementation Notes

### Adding a New Adapter

1. Create new file in `patiently/adapters/` (e.g. `my_adapter.py`)
2. Subclass `BaseAdapter` from `patiently.core.base_adapter`
3. Implement three methods:
   - `source_type` property — Return unique string identifier
   - `supports(input_data: Any) -> bool` — Return True if adapter can handle the input
   - `parse(input_data: Any) -> AdapterResult` — Parse input and return FHIR resources + patient identity
4. Use helper functions from `patiently.core.fhir_helpers` to build FHIR resources
5. Add adapter to `IngestionPipeline.__init__()` in `patiently/pipeline/ingestion.py`
6. Write tests in `tests/test_my_adapter.py`

### FHIR Resource Construction

- Use `fhir.resources` library (Pydantic v2 models) — already included in requirements
- Import from `fhir.resources.R4B.*` (FHIR R4B is used throughout)
- Helper functions in `patiently/core/fhir_helpers.py` provide common patterns:
  - `make_patient()` — Create Patient resource from PatientIdentity
  - Other helpers for Observations, Encounters, etc.
- Always set `meta.profile` to NRCES India profiles where applicable (see `patiently/config.py`)

### Patient Linking Logic

The linker is deterministic and uses strict tier-based matching (see `patiently/core/patient_linker.py:_find_match()`):

- **Tier 1**: Exact MRN match (highest priority)
- **Tier 2**: Exact ABHA ID match
- **Tier 3**: Exact normalized name + DOB (name parts are lowercased, sorted, stripped)
- **Tier 4**: Phone match (digits only) or email match (case-insensitive)

A match only fires when **both sides have the field populated**. If no match is found, a new patient is created with a new UUID.

### VLM Integration

The `HandwrittenAdapter` uses a Vision Language Model (VLM) to extract structured data from handwritten clinical notes:

- Primary: Google Gemini (`google-generativeai` package)
- Fallback: Together AI API
- Mock client (`MockVLMClient`) available for testing
- VLM client interface defined in `patiently/api/vlm_client.py`

### Testing Philosophy

- All adapters have dedicated test files in `tests/`
- Test fixtures in `tests/conftest.py` provide sample data file paths
- Integration tests in `tests/test_pipeline.py` verify full pipeline with cross-source linking
- Sample data in `ingestion/sample_data/` includes real-world-like examples for all 6 sources

## Key Files to Read First

1. **`ingestion/schema.md`** — MUST READ. Comprehensive schema reference with all data models, FHIR resources, coding systems, and examples.
2. **`ingestion/patiently/core/base_adapter.py`** — Core interfaces and data types
3. **`ingestion/patiently/pipeline/ingestion.py`** — Pipeline orchestration logic
4. **`ingestion/patiently/config.py`** — All FHIR coding constants and mappings

## Git Workflow

- Main branch: `main`
- Current feature branch: `theperiperi/fhir-data-ingestion`
- Recent major changes:
  - Restructured as monorepo (moved `backend/` → `ingestion/`)
  - Added 6-source FHIR ingestion pipeline
  - Renamed project from "pragyan-26" to "patient-ly"
