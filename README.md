# Patient.ly

AI-powered patient triage system built on India's ABDM (Ayushman Bharat Digital Mission) health data infrastructure. Converts heterogeneous medical data from 7 source types into standardized FHIR R4 bundles, then uses AI to make real-time triage decisions (ESI 1-5) with full clinical context.

## Architecture

```
                                   Patient.ly System
 ============================================================================================

  DATA SOURCES                    INGESTION PIPELINE                    AI TRIAGE
  ============                    ==================                    =========

  Apple Health XML  ─┐
  Google Fit JSON   ─┤
  NEMSIS XML (EMS)  ─┤            ┌──────────────┐
  HL7 v2 Messages   ─┼──────────►│  7 Adapters   │
  Handwritten Notes ─┤            │  (parse any   │     ┌─────────────┐     ┌──────────────┐
  Bedside Monitors  ─┤            │   format)     ├────►│  Patient     ├────►│ FHIR R4      │
  DICOM / PDF Labs  ─┤            └──────────────┘     │  Linker      │     │ Bundles      │
  Synthea Bundles   ─┘                                  │  (4-tier     │     │ (per-patient) │
                                                        │   matching)  │     └──────┬───────┘
                                                        └─────────────┘            │
                                                                                    ▼
  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────────────────┐
  │  Next.js     │◄───►│  Triage API  │◄───►│  MCP Server  │◄────│  111 ABDM Patient        │
  │  Frontend    │     │  (Claude AI) │     │  (9 tools)   │     │  Bundles                 │
  │              │     │              │     │              │     └──────────────────────────┘
  │  - Intake    │     │  - ESI 1-5   │     │  - Search    │
  │  - Queue     │     │  - SBAR      │     │  - Snapshot  │     ┌──────────────────────────┐
  │  - Triage    │     │  - Bay assign │     │  - History   │     │  ML Models (XGBoost)     │
  │  - Dashboard │     │  - Protocols │     │  - Drug check│     │  87% accuracy ESI pred   │
  └──────────────┘     └──────────────┘     └──────────────┘     └──────────────────────────┘
```

## Components

| Directory | What it does | Tech |
|-----------|-------------|------|
| [`ingestion/`](ingestion/) | FHIR R4 data ingestion pipeline - parses 7 medical data formats into standardized FHIR bundles with cross-source patient linking | Python, FastAPI, fhir.resources |
| [`frontend/`](frontend/) | Triage UI - patient intake (with voice), queue management, triage view, analytics dashboard | Next.js 16, React 19, Tailwind, Shadcn/ui |
| [`mcp_triage_server/`](mcp_triage_server/) | MCP server exposing 9 clinical data tools for AI agents to query patient records | Python, MCP protocol |
| [`models/`](models/) | ML pipeline for ESI prediction from FHIR data - XGBoost achieves 87% accuracy | XGBoost, scikit-learn, pandas |
| [`abdm-local-dev-kit/`](abdm-local-dev-kit/) | Local ABDM development environment with gateway, consent manager, HIP/HIU services | Docker, FastAPI, MongoDB |
| [`ui-experiments/`](ui-experiments/) | UI research and 4 prototype concepts for triage interfaces | Documentation, wireframes |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (for ABDM dev kit)

### 1. Ingestion Pipeline

```bash
cd ingestion
pip install -r requirements.txt

# Process medical data files into FHIR bundles
python -m patiently.pipeline.ingestion --input sample_data --output output/

# Or run as API server
uvicorn patiently.api.server:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

### 3. Triage Agent

```bash
# Interactive triage session using Claude Agent SDK
python triage_agent.py

# Or triage a specific patient
python triage_agent.py "ganesh.bhat6117@abdm"

# Or run as API server
python triage_agent_api.py serve
```

### 4. MCP Triage Server

```bash
cd mcp_triage_server
pip install -e .
python -m mcp_triage_server.server
```

### 5. ABDM Dev Kit

```bash
cd abdm-local-dev-kit
docker-compose up -d
# Gateway: http://localhost:8090
# Swagger UI: http://localhost:8080
```

## Data Flow

**Ingestion** (offline, batch):
```
Raw medical files (XML, JSON, HL7, DICOM, PDF, images)
  → 7 source adapters parse into FHIR resources
  → Patient linker matches identities across sources (MRN, ABHA, name+DOB, phone)
  → Bundler creates per-patient FHIR R4 Transaction Bundles
  → Output: JSON files, one per patient
```

**Triage** (real-time, per patient):
```
Patient arrives at ED
  → Nurse enters complaint via voice or form (frontend /intake)
  → Frontend calls Triage API with patient ID + complaint
  → Triage agent queries MCP server for ABDM medical history
  → AI assigns ESI level, bay, specialists, protocols, SBAR handoff
  → Frontend displays triage decision in /triage view
  → Patient enters /queue ordered by acuity
```

## FHIR Compliance

All output conforms to:
- **FHIR R4** specification
- **NRCES India** profiles (ABDM-compliant)
- **ABHA** (Ayushman Bharat Health Account) identifier system

Coding systems used: LOINC, SNOMED-CT, ICD-10, UCUM, HL7 v2/v3.

See [`ingestion/schema.md`](ingestion/schema.md) for the complete FHIR schema reference.

## Project Structure

```
patient-ly-pragyan-hackathon-2026/
├── ingestion/                  # FHIR data ingestion pipeline (Python)
│   ├── ingest/
│   │   ├── adapters/           #   7 source-specific parsers
│   │   ├── api/                #   FastAPI server + VLM client
│   │   ├── core/               #   Base adapter, linker, bundler, helpers
│   │   ├── pipeline/           #   Pipeline orchestrator + CLI
│   │   ├── config.py           #   FHIR coding constants (LOINC, SNOMED, etc.)
│   │   └── simulators/         #   Test data generators
│   ├── tests/                  #   13 test files (pytest)
│   ├── sample_data/            #   Example medical data files
│   ├── schema.md               #   FHIR schema reference
│   └── requirements.txt
├── frontend/                   # Next.js triage UI
│   ├── app/                    #   Pages: intake, queue, triage, dashboard
│   ├── components/             #   Triage + Shadcn/ui components
│   ├── lib/                    #   Types, hooks, voice API client
│   └── voice/                  #   Voice processing (STT, extraction)
├── mcp_triage_server/          # MCP server for AI agent access
│   ├── tools/                  #   9 MCP tool implementations
│   ├── data/                   #   FHIR bundle loading + extraction
│   └── server.py               #   MCP server entry point
├── models/                     # ML models for ESI prediction
│   ├── data/                   #   Preprocessing, labeling, feature eng.
│   └── baseline/               #   Trained models (XGBoost, RF, etc.)
├── abdm-local-dev-kit/         # Local ABDM dev environment
│   ├── services/               #   Gateway, consent mgr, HIP, HIU
│   ├── fhir-profiles/          #   NRCES India FHIR profiles
│   └── fhir-samples/           #   100+ example FHIR resources
├── ui-experiments/             # UI research & prototypes
├── triage_agent.py             # Interactive triage agent (Claude SDK)
├── triage_agent_api.py         # Triage API server (FastAPI + Claude)
├── CLAUDE.md                   # AI coding assistant instructions
└── LICENSE
```

## Testing

```bash
# Ingestion pipeline tests
cd ingestion && pytest -v

# Frontend
cd frontend && npm run build
```

## Deployment

The frontend is configured for Vercel deployment (`frontend/vercel.json`) with rewrites for voice API and health endpoints. The ingestion API and triage API run as separate FastAPI services.

## License

See [LICENSE](LICENSE).
