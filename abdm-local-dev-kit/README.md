# ABDM Local Development Kit

Local development environment for ABDM (Ayushman Bharat Digital Mission) health information exchange. Provides a complete simulation of the ABDM ecosystem with patient discovery, consent management, and FHIR-based health record exchange.

## Quick Start

```bash
docker-compose up -d
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Gateway | 8090 | Routes requests between HIPs, HIUs, and Consent Manager |
| Consent Manager | 8091 | Manages patient consent lifecycle |
| HIP | 8092 | Health Information Provider - serves patient records |
| HIU | 8093 | Health Information User - requests patient records |
| FHIR Validator | 8094 | Validates FHIR bundles against NRCES India profiles |
| MongoDB | 27017 | Database for all services |
| Swagger UI | 8080 | Interactive API documentation |

## Features

- Full consent flow implementation (request, approve, deny, revoke)
- 111 realistic Indian patient records with ABHA numbers
- FHIR bundles (DischargeSummary, Prescription, DiagnosticReport)
- Async callback pattern (202 Accepted) matching production ABDM
- Patient discovery and matching by ABHA number/address
- OTP-based care context linking (simulated)
- Health information exchange between HIPs and HIUs

## Data

### Patient Records

- `data/seed/patients.json` - Index of 111 patients with ABHA numbers, demographics
- `data/seed/fhir_bundles/` - Per-patient FHIR R4 bundles

### FHIR Profiles

- `fhir-profiles/` - NRCES India FHIR R4 structure definitions
- `fhir-samples/` - 100+ example FHIR resources (core and official)

### Python SDK

- `sdk/python/abdm_client/` - Python client for interacting with ABDM services

## Directory Structure

```
abdm-local-dev-kit/
├── docker-compose.yml          # All services orchestration
├── .env.example                # Environment variable template
├── QUICK_START.md              # Detailed setup guide
├── api-schemas/                # OpenAPI schemas for all services
├── data/
│   ├── seed/
│   │   ├── patients.json       # 111 patient index
│   │   └── fhir_bundles/       # Per-patient FHIR bundles
│   └── generators/             # Data generation scripts
├── docs/                       # Architecture and API docs
├── fhir-profiles/
│   ├── definitions/            # NRCES India structure definitions
│   └── npm/                    # FHIR npm packages
├── fhir-samples/
│   ├── core-resources/         # Core FHIR R4 resource examples
│   └── official/               # Official FHIR example resources
├── scripts/                    # Setup and utility scripts
├── sdk/
│   └── python/abdm_client/     # Python SDK
├── services/
│   ├── gateway/                # ABDM Gateway service
│   ├── consent_manager/        # Consent lifecycle service
│   ├── hip/                    # Health Information Provider
│   ├── hiu/                    # Health Information User
│   └── fhir_validator/         # FHIR bundle validator
└── tests/                      # Integration tests
```

## ABDM Workflow

```
Patient arrives → ABHA card scanned
    │
    ▼
HIU (your app) → Gateway → HIP (other hospitals)
    │                           │
    ▼                           ▼
Request consent ←── Consent Manager ──→ Patient approves
    │
    ▼
Fetch health records (FHIR bundles)
    │
    ▼
Parse + display in triage UI
```

## Testing

All services include `/health` endpoints for status checks:

```bash
curl http://localhost:8090/health  # Gateway
curl http://localhost:8091/health  # Consent Manager
curl http://localhost:8092/health  # HIP
curl http://localhost:8093/health  # HIU
```

See `QUICK_START.md` for detailed setup and testing instructions.
