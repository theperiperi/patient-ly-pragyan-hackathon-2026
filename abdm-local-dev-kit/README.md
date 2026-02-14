# ABDM Local Development Kit

Complete local development environment for ABDM (Ayushman Bharat Digital Mission) health information exchange.

## Quick Start

```bash
docker-compose up -d
```

## Services

- Gateway (8090) - Routes requests between HIPs, HIUs, and Consent Manager
- Consent Manager (8091) - Manages patient consent lifecycle
- HIP (8092) - Health Information Provider
- HIU (8093) - Health Information User  
- FHIR Validator (8094) - Validates FHIR bundles
- MongoDB (27017) - Database
- Swagger UI (8080) - API documentation

## Features

- ✅ Full consent flow implementation
- ✅ 100 realistic Indian patient records with ABHA numbers
- ✅ 60 sample FHIR bundles (DischargeSummary, Prescription, DiagnosticReport)
- ✅ Async callback pattern (202 Accepted)
- ✅ Patient discovery and matching
- ✅ OTP-based care context linking (simulated)
- ✅ Health information exchange

## Testing

All services include /health endpoints for status checks.

