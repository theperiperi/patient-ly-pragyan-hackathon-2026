# ABDM Resources Download Index

**Downloaded on:** 2026-02-14
**Downloaded by:** Automated script

This index documents all ABDM FHIR resources and API schemas that were successfully downloaded and organized into the `abdm-local-dev-kit` directory.

---

## 1. FHIR Resources from NRCES

### Source
All FHIR resources were downloaded from: https://www.nrces.in/ndhm/fhir/r4/

### 1.1 NPM Package
**Location:** `fhir-profiles/npm/package/`
**Source File:** `package.tgz` (6.6 MB)
**Status:** ✅ Successfully downloaded and extracted
**Contents:**
- 132+ FHIR profile definition files in JSON format
- CodeSystems, ValueSets, StructureDefinitions
- Package metadata in `package.json`
- Example resources in `example/` subdirectory
- XML representations in `xml/` subdirectory
- Additional resources in `other/` subdirectory

**Key Resources Include:**
- CodeSystem-ndhm-adjudication-reason.json
- CodeSystem-ndhm-benefit-type.json
- CodeSystem-ndhm-billing-codes.json
- CodeSystem-ndhm-claim-exclusion.json
- CodeSystem-ndhm-coverage-type.json
- CodeSystem-ndhm-identifier-type-code.json
- StructureDefinition profiles for ABDM-specific resources
- ValueSets for clinical terminology

### 1.2 Profile Definitions
**Location:** `fhir-profiles/definitions/`
**Source File:** `definitions.json.zip` (1.4 MB)
**Status:** ✅ Successfully downloaded and extracted
**Contents:**
- 132 FHIR profile definition files in JSON format
- Complete StructureDefinition resources
- CodeSystem and ValueSet definitions
- ABDM-specific extensions and profiles

**Resource Types:**
- CodeSystems (24 files)
- StructureDefinitions (80+ files)
- ValueSets (28+ files)

### 1.3 Example Bundles
**Location:** `fhir-samples/official/`
**Source File:** `examples.json.zip` (7.0 MB)
**Status:** ✅ Successfully downloaded and extracted
**Contents:**
- 276 example FHIR resource files in JSON format
- Clinical document bundles (DiagnosticReport, Discharge Summary, etc.)
- Claim and Coverage examples
- Insurance workflow examples

**Example Types Include:**
- AllergyIntolerance examples
- Appointment examples
- Binary resources (encoded documents)
- Bundle resources for various workflows:
  - Claim bundles (enhancement, preauthorization, settlement)
  - ClaimResponse bundles
  - CoverageEligibilityRequest bundles
  - CoverageEligibilityResponse bundles
  - DiagnosticReport bundles
  - DischargeSummary bundles
  - HealthDocumentRecord bundles
  - ImmunizationRecord bundles
  - OPConsultation bundles
  - Prescription bundles
  - WellnessRecord bundles

---

## 2. API Schemas

### Source
API schemas were obtained from multiple sources due to sandbox.abdm.gov.in being temporarily unavailable (503 errors). Alternative sources from official NHA-ABDM GitHub repositories were used.

### 2.1 ABDM Core APIs (from NHA-ABDM/ABDM-wrapper)

**Location:** `api-schemas/`
**Source Repository:** https://github.com/NHA-ABDM/ABDM-wrapper
**Status:** ✅ Successfully cloned and extracted

#### Downloaded Files:

1. **gateway.yaml** (171 KB)
   - ABDM Gateway API specification
   - Source: `mock-gateway/src/main/resources/abdm-gateway.yaml`
   - OpenAPI specification for gateway services

2. **wrapper.yaml** (54 KB)
   - ABDM Wrapper API specification
   - Source: `mock-gateway/src/main/resources/wrapper.yaml`
   - Wrapper interface definitions

3. **wrapper-v1.yaml** (35 KB)
   - ABDM Wrapper API v1 specification
   - Source: `docs/wrapperV1.yaml`
   - Version 1 wrapper documentation

4. **wrapper-v3.yaml** (38 KB)
   - ABDM Wrapper API v3 specification
   - Source: `docs/wrapperV3.yaml`
   - Version 3 wrapper documentation (Milestone 3)

5. **hip.yaml** (19 KB)
   - Health Information Provider (HIP) facade API
   - Source: `sample-hip/specs/hip-facade.yaml`
   - HIP integration endpoints

6. **hip-v3.yaml** (33 KB)
   - Health Information Provider (HIP) v3 facade API
   - Source: `sample-hip/specs/hip-v3-facade.yaml`
   - HIP Milestone 3 specifications

7. **hiu.yaml** (9.5 KB)
   - Health Information User (HIU) facade API
   - Source: `sample-hiu/specs/hiu-facade.yaml`
   - HIU integration endpoints

8. **fhir-mapper.yaml** (30 KB)
   - FHIR Mapper API specification
   - Source: `fhir-mapper/fhir-mapper.yaml`
   - FHIR transformation service

### 2.2 UHI (Universal Health Interface) APIs (from NHA-ABDM/UHI)

**Location:** `api-schemas/`
**Source Repository:** https://github.com/NHA-ABDM/UHI
**Status:** ✅ Successfully cloned and extracted

#### Downloaded Files:

9. **uhi-core.yml** (80 KB)
   - UHI Core Protocol specification
   - Source: `specification/core.yml`
   - Core UHI protocol definitions

10. **uhi-gateway.yaml** (299 KB)
    - UHI Gateway API v1.0.6
    - Source: `src/gateway/Gateway/src/main/resources/static/swagger-docs/v1.0.6/Gateway.yaml`
    - UHI network gateway endpoints

11. **uhi-registry.yaml** (4.8 KB)
    - UHI Network Registry API v1.0.0
    - Source: `src/network_registry/regsitry-app/src/main/resources/static/swagger-docs/v1.0.0/registry.yaml`
    - Network participant registry

12. **uhi-hspa.yaml** (81 KB)
    - Health Service Provider Application (HSPA) API v1.0.0
    - Source: `src/apps/backend/hspa-backend/hspaAdapter/HSPA/src/main/resources/static/swagger-docs/v1.0.0/Hspa.yaml`
    - Provider application endpoints

13. **uhi-eua.yml** (191 KB)
    - End User Application (EUA) Client API v1.0.0
    - Source: `src/apps/backend/eua-backend/euaService/EUAclient/src/main/resources/static/swagger-docs/v1.0.0/EUA.yml`
    - User application client endpoints

14. **uhi-booking-service.yaml** (31 KB)
    - UHI Booking Service API v1.0.0
    - Source: `src/apps/backend/eua-backend/euaBookingservice/EUA-BookingService/src/main/resources/static/swagger-docs/v1.0.0/BookingService.yaml`
    - Appointment booking service

### 2.3 DHP (Decentralized Health Protocol) APIs (from NHA-ABDM/DHP-Specs)

**Location:** `api-schemas/`
**Source Repository:** https://github.com/NHA-ABDM/DHP-Specs
**Status:** ✅ Successfully cloned and extracted

#### Downloaded Files:

15. **dhp-core.yaml** (79 KB)
    - DHP Core Protocol v0 specification
    - Source: `protocol-specifications/core/v0/api/core.yaml`
    - Decentralized Health Protocol core APIs

---

## 3. Failed Downloads

The following resources could not be downloaded due to sandbox.abdm.gov.in returning 503 errors:

### From sandbox.abdm.gov.in (All returned 503 Service Unavailable):
- ❌ `https://sandbox.abdm.gov.in/swagger/ndhm-gateway.yaml`
- ❌ `https://sandbox.abdm.gov.in/swagger/ndhm-cm.yaml` (Consent Manager)
- ❌ `https://sandbox.abdm.gov.in/swagger/ndhm-devservice.yaml` (Dev Service)
- ❌ `https://sandbox.abdm.gov.in/swagger/ndhm-phr-app2.yaml` (PHR App)
- ❌ `https://sandbox.abdm.gov.in/swagger/ndhm-hiu.yaml` (HIU)
- ❌ `https://sandbox.abdm.gov.in/static/media/ABHA_APIs_Swagger.b101c687.yaml` (ABHA APIs)
- ❌ `https://sandbox.abdm.gov.in/swagger/abha_enrollment_api.yaml` (ABHA Enrollment v3)

### Resources Not Found:
The following resources mentioned in the original request were not found in available sources:
- ❌ `bridge.yaml` - Bridge API schema (not found in repositories)
- ❌ `phr-app-login.yaml` - PHR App Login (specific endpoint not available)
- ❌ `phr-app-consent.yaml` - PHR App Consent (specific endpoint not available)
- ❌ `link-token-service.yaml` - Link Token Service (not found)
- ❌ `health-id.json` - Health ID API (JSON format not found)

**Note:** The sandbox.abdm.gov.in site appears to be experiencing service disruptions. The API schemas obtained from official NHA-ABDM GitHub repositories (ABDM-wrapper, UHI, DHP-Specs) are authoritative sources and represent the most up-to-date specifications for ABDM integration.

---

## 4. Summary Statistics

### Successfully Downloaded:
- **FHIR Profile Definitions:** 132 files
- **FHIR Example Resources:** 276 files
- **API Schema Files:** 15 files
- **Total Size:** ~20 MB (compressed), ~40 MB (extracted)

### Coverage by Category:

#### FHIR Resources:
- ✅ NPM Package (complete)
- ✅ Profile Definitions (complete)
- ✅ Example Bundles (complete)

#### API Schemas:
- ✅ ABDM Core APIs (HIP, HIU, Gateway, Wrapper) - from GitHub
- ✅ UHI APIs (Gateway, Registry, HSPA, EUA, Booking) - from GitHub
- ✅ DHP APIs (Core Protocol) - from GitHub
- ⚠️ ABHA/Health ID APIs - unavailable (sandbox down)
- ⚠️ PHR App APIs - unavailable (sandbox down)
- ⚠️ Consent Manager API - unavailable (sandbox down)

---

## 5. Alternative Sources

For the resources that could not be downloaded from sandbox.abdm.gov.in, here are alternative sources:

### Official GitHub Repositories:
1. **NHA-ABDM/ABDM-wrapper** - https://github.com/NHA-ABDM/ABDM-wrapper
   - HIP/HIU implementation reference
   - Mock gateway specifications
   - Wrapper API documentation

2. **NHA-ABDM/UHI** - https://github.com/NHA-ABDM/UHI
   - Universal Health Interface specifications
   - Gateway, Registry, and application APIs
   - Complete UHI protocol implementation

3. **NHA-ABDM/DHP-Specs** - https://github.com/NHA-ABDM/DHP-Specs
   - Decentralized Health Protocol specifications
   - Open API specifications for DHP

### Documentation Sites:
1. **ABDM Sandbox Documentation** - https://kiranma72.github.io/abdm-docs/
   - Community-maintained documentation
   - API guides and examples

2. **SwaggerHub** - https://app.swaggerhub.com/apis-docs/abdm.abha/abha-service/1.0
   - ABHA Service API documentation
   - Interactive API explorer

### When sandbox.abdm.gov.in becomes available:
The following endpoints should be checked for updates:
- Consent Manager API
- Dev Service API
- PHR App APIs
- ABHA Enrollment APIs
- Health ID APIs

---

## 6. Directory Structure

```
abdm-local-dev-kit/
├── fhir-profiles/
│   ├── npm/
│   │   └── package/          # 132 FHIR resources + examples
│   │       ├── *.json        # Profile definitions
│   │       ├── example/      # Example resources
│   │       ├── xml/          # XML representations
│   │       └── other/        # Additional resources
│   └── definitions/          # 132 FHIR profile definitions
│       └── *.json
│
├── fhir-samples/
│   └── official/             # 276 example FHIR bundles
│       └── *.json
│
├── api-schemas/              # 15 API specification files
│   ├── gateway.yaml          # ABDM Gateway API
│   ├── wrapper.yaml          # Wrapper API
│   ├── wrapper-v1.yaml       # Wrapper API v1
│   ├── wrapper-v3.yaml       # Wrapper API v3
│   ├── hip.yaml              # HIP Facade API
│   ├── hip-v3.yaml           # HIP Facade API v3
│   ├── hiu.yaml              # HIU Facade API
│   ├── fhir-mapper.yaml      # FHIR Mapper API
│   ├── uhi-core.yml          # UHI Core Protocol
│   ├── uhi-gateway.yaml      # UHI Gateway API
│   ├── uhi-registry.yaml     # UHI Registry API
│   ├── uhi-hspa.yaml         # UHI HSPA API
│   ├── uhi-eua.yml           # UHI EUA Client API
│   ├── uhi-booking-service.yaml  # UHI Booking Service
│   └── dhp-core.yaml         # DHP Core Protocol
│
└── DOWNLOAD_INDEX.md         # This file
```

---

## 7. Recommended Next Steps

1. **Monitor sandbox.abdm.gov.in** for when services are restored to download missing schemas
2. **Validate API schemas** using OpenAPI validators
3. **Cross-reference** FHIR profiles with API requirements
4. **Set up local testing** environment using downloaded resources
5. **Generate client SDKs** from OpenAPI specifications
6. **Create mock servers** using the API schemas for local development

---

## 8. Additional Notes

- All FHIR resources follow FHIR R4 specification
- API schemas use OpenAPI 3.0 (OAS3) specification format
- Some files use `.yaml` extension while others use `.yml` - both are valid YAML files
- The UHI repository contains extensive example code and implementations
- FHIR Mapper service can transform between different FHIR profile versions

---

## 9. Version Information

- **NRCES FHIR Profiles:** Last updated May 8, 2025 (based on file timestamps)
- **ABDM Wrapper:** Latest version from GitHub (cloned 2026-02-14)
- **UHI:** Latest version from GitHub (cloned 2026-02-14)
- **DHP-Specs:** Latest version from GitHub (cloned 2026-02-14)

---

**Disclaimer:** This download was performed autonomously with error handling. All successfully downloaded resources are from official NHA-ABDM sources and NRCES. Resources that could not be accessed due to server unavailability have been documented and alternative sources have been provided.
