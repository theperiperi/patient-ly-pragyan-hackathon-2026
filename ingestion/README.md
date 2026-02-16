# Ingestion Pipeline

FHIR R4 data ingestion pipeline that converts heterogeneous medical data from 7 source types into standardized, ABDM-compliant FHIR R4 JSON bundles. Uses in-memory processing with cross-source patient linking and outputs per-patient Transaction Bundles.

## How It Works

```
                         Ingestion Pipeline
  =====================================================================

  INPUT FILES              ADAPTERS              LINKER         OUTPUT
  ===========              ========              ======         ======

  apple_health.xml  ──► WearableAdapter ──┐
  google_fit.json   ──► WearableAdapter ──┤
  nemsis_ems.xml    ──► AmbulanceAdapter ─┤                  ┌─────────┐
  hl7_message.hl7   ──► EHRAdapter ───────┤  ┌───────────┐   │ patient_ │
  notes.png         ──► HandwrittenAdapter┼─►│ Patient   ├──►│ 001.json │
  vitals.json       ──► RealtimeVitals ───┤  │ Linker    │   │ patient_ │
  scan.dcm          ──► ScansLabsAdapter ─┤  │ (4-tier)  │   │ 002.json │
  synthea.json      ──► SyntheaAdapter ───┘  └───────────┘   │ ...      │
                                                              └─────────┘
                                                          FHIR R4 Bundles
```

Each adapter parses a specific medical data format, extracts patient identity information and clinical data, and produces FHIR R4 resources. The patient linker then matches patients across sources using a 4-tier deterministic algorithm, and the bundler creates one FHIR Transaction Bundle per patient.

## Setup

```bash
cd ingestion
pip install -r requirements.txt
```

### Environment Variables (optional)

- `GOOGLE_API_KEY` - For Gemini VLM (handwritten note extraction)
- `TOGETHER_API_KEY` - Fallback VLM provider

## Usage

### CLI

```bash
# Process all files in a directory
python -m patiently.pipeline.ingestion --input sample_data --output output/

# Files are auto-routed to the correct adapter based on format detection
```

### API Server

```bash
uvicorn patiently.api.server:app --reload --port 8000
```

Endpoints:

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/ingest` | Multi-file upload, returns per-patient FHIR bundles |
| `POST` | `/ingest/file` | Single file upload, returns parsed FHIR resources |

### Generate Sample Data

```bash
python -m patiently.simulators.runner --scenario chest_pain --output sample_data
```

## Adapters

Each adapter implements the `BaseAdapter` interface (`supports()`, `parse()`, `source_type`).

| Adapter | Source | Input Formats | FHIR Resources Produced |
|---------|--------|---------------|------------------------|
| `WearableAdapter` | Apple Health, Google Fit | XML, JSON | `Observation` (vital-signs) |
| `AmbulanceAdapter` | 108 EMS (NEMSIS) | XML | `Encounter` + `Observation` |
| `EHRAdapter` | Hospital EHR | HL7 v2 (pipe-delimited) | `Encounter` + `Observation` + `Condition` + `DiagnosticReport` |
| `HandwrittenAdapter` | Clinical notes | PNG, JPG images | `DocumentReference` + `Condition` + `Observation` |
| `RealtimeVitalsAdapter` | Bedside monitors | JSON (numeric) + CSV (waveform) | `Observation` (vital-signs + SampledData ECG) |
| `ScansLabsAdapter` | Medical imaging, lab reports | DICOM, PDF | `ImagingStudy` + `DiagnosticReport` + `DocumentReference` + `Observation` |
| `SyntheaAdapter` | Synthea generator | FHIR JSON bundles | All standard FHIR resource types |

### HandwrittenAdapter (VLM)

Uses a Vision Language Model to extract structured clinical data from photos of handwritten notes:
- Primary: Google Gemini (`google-generativeai`)
- Fallback: Together AI
- Testing: `MockVLMClient` for deterministic tests

## Patient Linker

Matches patients across data sources using strict, deterministic 4-tier matching:

| Priority | Match Criteria | Example |
|----------|----------------|---------|
| 1 | Exact MRN | `MRN-2024-001234` |
| 2 | Exact ABHA ID | Same ABDM Health ID |
| 3 | Normalized name + DOB | `"kumar rajesh"` + `1975-08-15` |
| 4 | Phone or email | Same digits / same lowercase email |

A match only fires when **both sides** have the field populated. No match = new patient with a new UUID.

After linking, the linker merges patient records by taking the most complete field values across all sources.

## FHIR Bundle Output

Each output file is a FHIR R4 Transaction Bundle:

- First entry is always the merged `Patient` resource
- All other resources (`Observation`, `Encounter`, `Condition`, etc.) reference the patient via `fullUrl`
- All resources use NRCES India profiles where applicable
- Coding uses LOINC, SNOMED-CT, ICD-10, UCUM

See [`schema.md`](schema.md) for the complete schema reference.

## Directory Structure

```
ingestion/
├── ingest/
│   ├── adapters/                    # Source-specific parsers
│   │   ├── wearable_adapter.py      #   Apple Health XML + Google Fit JSON
│   │   ├── ambulance_adapter.py     #   NEMSIS XML (108 EMS)
│   │   ├── ehr_adapter.py           #   HL7 v2 pipe-delimited messages
│   │   ├── handwritten_adapter.py   #   Image → VLM → FHIR
│   │   ├── realtime_vitals_adapter.py #  JSON vitals + CSV waveforms
│   │   ├── scans_labs_adapter.py    #   DICOM + PDF
│   │   └── synthea_adapter.py       #   Synthea FHIR bundles
│   ├── api/
│   │   ├── server.py                # FastAPI ingestion server
│   │   └── vlm_client.py           # VLM client (Gemini + Together AI)
│   ├── core/
│   │   ├── base_adapter.py          # BaseAdapter ABC + data types
│   │   ├── patient_linker.py        # Cross-source patient matching
│   │   ├── bundler.py               # FHIR Transaction Bundle builder
│   │   └── fhir_helpers.py          # Helper functions for resource creation
│   ├── pipeline/
│   │   └── ingestion.py             # Pipeline orchestrator + CLI entry
│   ├── config.py                    # FHIR coding constants (LOINC, SNOMED, UCUM, etc.)
│   └── simulators/                  # Test data generators
│       ├── base_simulator.py        #   Base simulator class
│       ├── wearable_sim.py          #   Wearable data generator
│       ├── ambulance_sim.py         #   NEMSIS data generator
│       ├── ehr_sim.py               #   HL7 v2 message generator
│       ├── handwritten_sim.py       #   Clinical note image generator
│       ├── realtime_vitals_sim.py   #   Bedside monitor data generator
│       ├── scans_labs_sim.py        #   DICOM + PDF generator
│       ├── synthea_generator.py     #   Synthea bundle generator
│       └── runner.py                #   Scenario-based runner
├── tests/                           # Pytest test suite (13 files)
│   ├── conftest.py                  #   Fixtures + sample data paths
│   ├── test_wearable_adapter.py
│   ├── test_ambulance_adapter.py
│   ├── test_ehr_adapter.py
│   ├── test_handwritten_adapter.py
│   ├── test_realtime_vitals_adapter.py
│   ├── test_scans_labs_adapter.py
│   ├── test_synthea_adapter.py
│   ├── test_synthea_generator.py
│   ├── test_patient_linker.py
│   ├── test_bundler.py
│   └── test_pipeline.py            #   Full pipeline integration test
├── sample_data/                     # Example medical data files
├── schema.md                        # FHIR schema reference (read this!)
└── requirements.txt
```

## Key Data Types

Defined in `ingest/core/base_adapter.py`:

**`PatientIdentity`** - Extracted patient identifying info for linking:
- `source_id`, `source_system` (required)
- `full_name`, `given_name`, `family_name`, `birth_date`, `gender`
- `phone`, `email`, `mrn`, `abha_id`
- `address_line`, `address_city`, `address_state`, `address_postal_code`

**`AdapterResult`** - Output from any adapter:
- `patient_identity` - Extracted patient info
- `fhir_resources` - List of FHIR resources
- `fhir_patient` - Pre-built FHIR Patient resource (optional)
- `source_type`, `raw_metadata`

**`LinkedPatient`** - Unified patient after cross-source linking:
- `canonical_id` - Auto-generated UUID
- `identities` - All source identities
- `fhir_patient` - Merged Patient resource
- `all_resources` - All FHIR resources from all sources
- `source_types` - Set of contributing source types

## Testing

```bash
pytest                          # Run all tests
pytest -v                       # Verbose output
pytest tests/test_pipeline.py   # Integration test
pytest -k test_name             # Match pattern
```

## Adding a New Adapter

1. Create `ingest/adapters/my_adapter.py`
2. Subclass `BaseAdapter` from `ingest.core.base_adapter`
3. Implement `source_type` property, `supports(input_data)`, and `parse(input_data) -> AdapterResult`
4. Use helpers from `ingest.core.fhir_helpers` for resource creation
5. Register in `IngestionPipeline.__init__()` in `ingest/pipeline/ingestion.py`
6. Add tests in `tests/test_my_adapter.py`

## Dependencies

Key Python packages:
- `fhir.resources` - FHIR R4B Pydantic models
- `hl7` - HL7 v2 message parsing
- `pydicom` - DICOM file reading
- `lxml` - XML parsing
- `Pillow` - Image handling
- `pdfplumber` - PDF text extraction
- `google-generativeai` - Gemini VLM
- `together` - Together AI VLM (fallback)
- `fastapi` + `uvicorn` - API server
