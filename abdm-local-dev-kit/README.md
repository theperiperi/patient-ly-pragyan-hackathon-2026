# ABDM Local Development Kit

A comprehensive, self-hostable development sandbox for building applications in the ABDM (Ayushman Bharat Digital Mission) ecosystem without needing sandbox approval.

## What's Included

This kit provides everything you need to develop ABDM-compliant applications locally:

- **Complete FHIR Profiles & Schemas** - All ABDM FHIR R4 profiles (v6.5.0)
- **Sample Health Records** - JSON examples for all Health Information Types
- **API Specifications** - Swagger/OpenAPI schemas for all ABDM services
- **Mock Data** - Synthetic patient data conforming to ABDM standards
- **Documentation** - Comprehensive guides on standards, APIs, and integration
- **Testing Tools** - Validators, converters, and simulation scripts

## Directory Structure

```
abdm-local-dev-kit/
├── docs/                      # Comprehensive documentation
│   ├── ABDM_OVERVIEW.md      # ABDM ecosystem overview
│   ├── FHIR_GUIDE.md         # FHIR implementation guide
│   ├── API_REFERENCE.md      # Complete API documentation
│   ├── TERMINOLOGY.md        # SNOMED-CT, LOINC, ICD-10 mappings
│   └── INTEGRATION_GUIDE.md  # Step-by-step integration guide
├── fhir-samples/             # Sample FHIR bundles
│   ├── discharge-summaries/
│   ├── prescriptions/
│   ├── diagnostic-reports/
│   ├── op-consultations/
│   ├── immunization-records/
│   ├── wellness-records/
│   └── health-documents/
├── api-schemas/              # OpenAPI/Swagger specifications
│   ├── gateway.yaml
│   ├── consent-manager.yaml
│   ├── hip.yaml
│   ├── hiu.yaml
│   └── abha-service.yaml
├── mock-data/                # Synthetic patient data
│   ├── patients/
│   ├── practitioners/
│   ├── organizations/
│   └── conditions/
├── scripts/                  # Utility scripts
│   ├── validators/
│   ├── converters/
│   └── generators/
└── tools/                    # Development tools
    ├── fhir-validator/
    └── mock-server/
```

## Quick Start

### 1. Validate FHIR Resources

```bash
cd scripts/validators
python validate_fhir.py ../../fhir-samples/discharge-summaries/example-01.json
```

### 2. Generate Synthetic Data

```bash
cd scripts/generators
python generate_patients.py --count 100 --output ../../mock-data/patients/
```

### 3. Run Mock ABDM Server

```bash
cd tools/mock-server
docker-compose up
```

## Key Resources

### Official ABDM Resources
- **NRCES FHIR Implementation Guide**: https://nrces.in/ndhm/fhir/r4/
- **ABDM Sandbox**: https://sandbox.abdm.gov.in/
- **Documentation**: https://kiranma72.github.io/abdm-docs/

### This Kit's Resources
- [Complete API Reference](./docs/API_REFERENCE.md)
- [FHIR Implementation Guide](./docs/FHIR_GUIDE.md)
- [Sample Data Index](./fhir-samples/INDEX.md)
- [Mock Server Setup](./tools/mock-server/README.md)

## For Your Hackathon

This kit is specifically designed to help you build an **AI-Powered Smart Patient Triage System** without waiting for ABDM sandbox approval:

1. **Load Health Documents** - Use sample FHIR bundles from `fhir-samples/`
2. **Extract Patient Data** - Parse discharge summaries, lab reports, prescriptions
3. **Train Your Model** - Use synthetic data from `mock-data/`
4. **Test Integration** - Validate against ABDM schemas in `api-schemas/`

## Standards Covered

- **FHIR R4** - All 7 Health Information Types + 31 core profiles
- **SNOMED-CT** - Clinical terminology for conditions/procedures
- **LOINC** - Laboratory observation codes
- **ICD-10** - Disease classification codes

## License & Attribution

This development kit compiles publicly available ABDM standards and documentation. All FHIR profiles and schemas are copyright of National Resource Centre for EHR Standards (NRCeS) and HL7 India.

**For Educational & Development Use Only**

---

*Last Updated: 2026-02-14*
*ABDM FHIR IG Version: 6.5.0*
