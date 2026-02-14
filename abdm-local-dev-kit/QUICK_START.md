# Quick Start Guide - ABDM Local Dev Kit

This guide helps you quickly get started with the ABDM resources downloaded in this kit.

## What's Available

### 1. FHIR Resources (65 MB total)
- **132 Profile Definitions** - ABDM-specific FHIR profiles
- **276 Example Bundles** - Real-world clinical document examples
- **NPM Package** - Complete FHIR implementation guide package

### 2. API Schemas (1.2 MB total)
- **15 OpenAPI/Swagger specifications** covering:
  - ABDM Core (Gateway, Wrapper, HIP, HIU)
  - UHI (Universal Health Interface)
  - DHP (Decentralized Health Protocol)
  - FHIR Mapper service

## Quick Access

### View FHIR Profile Definitions
```bash
cd fhir-profiles/definitions/
ls -lh *.json
```

Common profiles:
- `StructureDefinition-*.json` - FHIR resource profiles
- `CodeSystem-*.json` - Terminology code systems
- `ValueSet-*.json` - Value set definitions

### Browse Example Clinical Documents
```bash
cd fhir-samples/official/
ls -lh Bundle-*.json
```

Example types:
- `Bundle-DiagnosticReportRecord-*.json` - Lab reports
- `Bundle-DischargeSummary-*.json` - Discharge summaries
- `Bundle-Prescription-*.json` - Prescriptions
- `Bundle-OPConsultation-*.json` - OP consultation records

### Explore API Schemas
```bash
cd api-schemas/
ls -lh *.yaml
```

Key APIs:
- `gateway.yaml` - ABDM Gateway (171 KB)
- `hip.yaml` / `hip-v3.yaml` - Health Information Provider APIs
- `hiu.yaml` - Health Information User API
- `uhi-gateway.yaml` - Universal Health Interface Gateway (299 KB)

## Common Use Cases

### 1. Validate FHIR Resources

```bash
# Install FHIR validator
# Use any JSON FHIR resource from fhir-samples/official/

# Example: Validate a discharge summary
fhir-validator Bundle-DischargeSummary-example-01.json \
  --profile fhir-profiles/definitions/
```

### 2. Generate API Client Code

Using OpenAPI Generator:
```bash
# Install openapi-generator-cli
npm install -g @openapitools/openapi-generator-cli

# Generate Python client for HIP API
openapi-generator-cli generate \
  -i api-schemas/hip-v3.yaml \
  -g python \
  -o ./generated/hip-client-python

# Generate TypeScript client for Gateway
openapi-generator-cli generate \
  -i api-schemas/gateway.yaml \
  -g typescript-axios \
  -o ./generated/gateway-client-ts
```

### 3. Set Up Mock API Server

Using Prism:
```bash
# Install Prism
npm install -g @stoplight/prism-cli

# Start mock HIP server
prism mock api-schemas/hip-v3.yaml

# Start mock Gateway server
prism mock api-schemas/gateway.yaml
```

### 4. Import into Postman

1. Open Postman
2. Click "Import"
3. Select any `.yaml` file from `api-schemas/`
4. Choose "OpenAPI 3.0"
5. Start testing APIs

### 5. View API Documentation

Using Swagger UI:
```bash
# Install swagger-ui
npm install -g swagger-ui-dist

# Serve API documentation
npx serve-swagger-ui api-schemas/gateway.yaml
```

Or use online viewers:
- https://editor.swagger.io/ (paste YAML content)
- https://redocly.github.io/redoc/ (for Redoc view)

## Resource Categories

### Clinical Documents (fhir-samples/official/)
| Category | Example Files | Use Case |
|----------|--------------|----------|
| Lab Reports | `Bundle-DiagnosticReportRecord-*.json` | Diagnostic test results |
| Discharge Summaries | `Bundle-DischargeSummary-*.json` | Hospital discharge records |
| Prescriptions | `Bundle-Prescription-*.json` | Medication orders |
| OP Consultations | `Bundle-OPConsultation-*.json` | Outpatient visits |
| Immunization | `Bundle-ImmunizationRecord-*.json` | Vaccination records |
| Wellness | `Bundle-WellnessRecord-*.json` | Health checkup records |
| Health Documents | `Bundle-HealthDocumentRecord-*.json` | General health documents |

### Insurance Workflows (fhir-samples/official/)
| Category | Example Files | Use Case |
|----------|--------------|----------|
| Claims | `Bundle-ClaimBundle-*.json` | Insurance claims |
| Claim Responses | `Bundle-ClaimResponseBundle-*.json` | Claim processing results |
| Eligibility Checks | `Bundle-CoverageEligibilityRequest-*.json` | Check coverage eligibility |
| Coverage | `Coverage-*.json` | Insurance coverage details |

### API Categories (api-schemas/)
| Category | Files | Description |
|----------|-------|-------------|
| ABDM Core | `gateway.yaml`, `wrapper*.yaml` | Core ABDM integration APIs |
| Health Providers | `hip.yaml`, `hip-v3.yaml` | HIP (provider) interfaces |
| Health Consumers | `hiu.yaml` | HIU (consumer) interfaces |
| FHIR Services | `fhir-mapper.yaml` | FHIR transformation |
| UHI | `uhi-*.yaml` (6 files) | Universal Health Interface |
| DHP | `dhp-core.yaml` | Decentralized Health Protocol |

## Development Workflows

### Building a Health Information Provider (HIP)

1. **Review HIP API spec:**
   ```bash
   cat api-schemas/hip-v3.yaml
   ```

2. **Study example bundles:**
   ```bash
   # Look at DiagnosticReportRecord examples
   ls fhir-samples/official/Bundle-DiagnosticReportRecord-*.json
   ```

3. **Check FHIR profiles:**
   ```bash
   # Find DiagnosticReport profile
   grep -l "DiagnosticReport" fhir-profiles/definitions/*.json
   ```

4. **Generate client code** (see above)

5. **Implement endpoints** according to spec

### Building a Health Information User (HIU)

1. **Review HIU API spec:**
   ```bash
   cat api-schemas/hiu.yaml
   ```

2. **Study consent workflows:**
   ```bash
   cat api-schemas/gateway.yaml | grep -A 10 "consent"
   ```

3. **Test with mock server** (see above)

### Integrating with UHI

1. **Review UHI core protocol:**
   ```bash
   cat api-schemas/uhi-core.yml
   ```

2. **Choose integration type:**
   - EUA (End User App): `uhi-eua.yml`
   - HSPA (Health Service Provider): `uhi-hspa.yaml`

3. **Study booking flow:**
   ```bash
   cat api-schemas/uhi-booking-service.yaml
   ```

## Testing & Validation

### FHIR Resource Validation

```bash
# Online validators:
# - https://validator.fhir.org/
# - https://inferno.healthit.gov/validator/

# Upload any file from fhir-samples/official/
```

### API Schema Validation

```bash
# Install openapi-validator
npm install -g @ibm/openapi-validator

# Validate a schema
openapi-validator api-schemas/gateway.yaml
```

## Tips & Best Practices

1. **Start with examples:** Before building, study the example bundles in `fhir-samples/official/`

2. **Use profiles correctly:** Always validate against the StructureDefinitions in `fhir-profiles/definitions/`

3. **Mock first:** Set up mock APIs before building real implementations

4. **Test incrementally:** Start with simple GET endpoints before complex POST operations

5. **Follow ABDM standards:** All implementations must comply with NRCES FHIR profiles

## Common FHIR Profiles

Located in `fhir-profiles/definitions/`:

- `StructureDefinition-DiagnosticReportRecord.json` - Lab reports
- `StructureDefinition-DischargeSummary.json` - Discharge summaries
- `StructureDefinition-Prescription.json` - Prescriptions
- `StructureDefinition-OPConsultRecord.json` - OP consultations
- `StructureDefinition-Patient.json` - Patient demographics
- `StructureDefinition-Practitioner.json` - Healthcare providers
- `StructureDefinition-Organization.json` - Healthcare facilities

## Key Code Systems

Located in `fhir-profiles/definitions/`:

- `CodeSystem-ndhm-identifier-type-code.json` - Identifier types (ABHA, etc.)
- `CodeSystem-ndhm-billing-codes.json` - Billing and procedure codes
- `CodeSystem-ndhm-supportinginfo-code.json` - Supporting information types

## Getting Help

### Official Resources
- **NRCES Website:** https://www.nrces.in/
- **ABDM Sandbox:** https://sandbox.abdm.gov.in/ (when available)
- **ABDM Documentation:** https://kiranma72.github.io/abdm-docs/
- **ABDM Forum:** https://devforum.abdm.gov.in/

### GitHub Repositories
- **ABDM Wrapper:** https://github.com/NHA-ABDM/ABDM-wrapper
- **UHI:** https://github.com/NHA-ABDM/UHI
- **DHP Specs:** https://github.com/NHA-ABDM/DHP-Specs

### Documentation in This Kit
- `DOWNLOAD_INDEX.md` - Complete inventory of downloaded resources
- `README.md` - Overview of the dev kit
- `RESEARCH_SUMMARY.md` - Research findings on ABDM integration

## Next Steps

1. ✅ **Explore the resources** - Browse through FHIR examples and API schemas
2. ✅ **Set up development environment** - Install validators and mock servers
3. ✅ **Choose your integration type** - HIP, HIU, PHR, or UHI
4. ✅ **Generate client SDKs** - Use OpenAPI Generator
5. ✅ **Build and test** - Start with mock APIs, then integrate with sandbox
6. ✅ **Validate compliance** - Test against NRCES profiles

---

**Last Updated:** 2026-02-14

For detailed information about what was downloaded and sources, see `DOWNLOAD_INDEX.md`.
