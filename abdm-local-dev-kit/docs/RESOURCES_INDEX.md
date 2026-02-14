# ABDM Resources Index

Complete index of all ABDM documentation, specifications, sample data, and tools discovered through extensive research.

## Official ABDM/NRCES Resources

### FHIR Implementation Guides

#### Current Version (v6.5.0)
- **Home Page**: https://nrces.in/ndhm/fhir/r4/
- **Downloads Page**: https://www.nrces.in/ndhm/fhir/r4/downloads.html
- **Profiles List**: https://www.nrces.in/ndhm/fhir/r4/profiles.html

#### Available Downloads
- **NPM Package**: `package.tgz` - Contains all value sets, profiles, pages, and URLs
- **Profiles (XML)**: `definitions.xml.zip`
- **Profiles (JSON)**: `definitions.json.zip`
- **Examples (XML)**: `examples.xml.zip`
- **Examples (JSON)**: `examples.json.zip`

#### Previous Versions
- **v7.0.0 (Preview)**: https://nrces.in/preview/ndhm/fhir/r4/
- **v5.0.0**: https://nrces.in/ndhm/fhir/r4/5.0.0/
- **v4.0.0**: https://nrces.in/ndhm/fhir/r4/4.0.0/
- **v3.0.1**: https://nrces.in/ndhm/fhir/r4/3.0.1/

### Implementation Guides (PDF)
- **FHIR Adoption Guide**: https://www.nrces.in/download/files/pdf/Implementation_Guide_for_Adoption_of_FHIR_in_ABDM_and_NHCX.pdf
- **Introduction to FHIR**: https://www.nrces.in/download/files/pdf/nrces_Brief%20Introduction%20to%20FHIR%20&%20Walkthrough%20to%20FHIR%20Implementation%20Guide%20for%20ABDM.pdf
- **LOINC Usage Guide**: https://www.nrces.in/download/files/pdf/Guide%20for%20using%20LOINC%20in%20ABDM%20FHIR%20Resources.pdf
- **Terminology Server Setup**: https://www.nrces.in/download/files/pdf/Guide_to_Setup_FHIR_Terminology_Server.pdf

## API Specifications (Swagger/OpenAPI)

### Gateway APIs
- **ABDM Gateway**: https://sandbox.abdm.gov.in/swagger/ndhm-gateway.yaml
- **Consent Manager**: https://sandbox.abdm.gov.in/swagger/ndhm-cm.yaml
- **Dev Service**: https://sandbox.abdm.gov.in/swagger/ndhm-devservice.yaml

### Health Information Provider/User APIs
- **HIP APIs**: https://sandbox.abdm.gov.in/swagger/ndhm-hip.yaml
- **HIU APIs**: https://sandbox.abdm.gov.in/swagger/ndhm-hiu.yaml
- **Bridge Service**: https://sandbox.abdm.gov.in/swagger/ndhm-bridge.yaml

### ABHA (Health ID) Service
- **ABHA Service**: https://app.swaggerhub.com/apis-docs/abdm.abha/abha-service/1.0
- **PHR App (Login/Registration)**: https://sandbox.abdm.gov.in/swagger/ndhm-phr-app2.yaml
- **PHR App (Consent)**: https://sandbox.abdm.gov.in/swagger/ndhm-phr-app.yaml
- **Health ID**: https://sandbox.abdm.gov.in/swagger/ndhm-healthid.json

### Registry Services
- **Health Facility Registry (HFR)**: https://facilitysbx.abdm.gov.in/swagger-ui.html
- **Healthcare Professional Registry (HPR)**: https://hpridsbx.abdm.gov.in/api/swagger-ui.html
- **Link Token Service**: https://sandbox.abdm.gov.in/swagger/HIECM-LinkTokenService.yaml

## FHIR Sample Bundles (JSON)

### Discharge Summary
- **Example 04**: https://www.nrces.in/ndhm/fhir/r4/Bundle-DischargeSummary-example-04.json.html
- **Profile Definition**: https://nrces.in/ndhm/fhir/r4/StructureDefinition-DischargeSummaryRecord.html

### Prescription Records
- **Example 06**: https://www.nrces.in/ndhm/fhir/r4/Bundle-Prescription-example-06.json.html
- **Example 06 (v3.0.1)**: https://nrces.in/ndhm/fhir/r4/3.0.1/Bundle-Prescription-example-06.json.html

### Diagnostic Reports (Lab)
- **Example 03**: https://www.nrces.in/ndhm/fhir/r4/Bundle-DiagnosticReport-Lab-example-03.json.html
- **Example 01**: https://nrces.in/ndhm/fhir/r4/DiagnosticReport-Lab-example-01.json.html
- **Profile Definition**: https://nrces.in/ndhm/fhir/r4/StructureDefinition-DiagnosticReportLab.html

### Diagnostic Reports (Imaging/DICOM)
- **Example 01 (v4.0.0)**: https://nrces.in/ndhm/fhir/r4/4.0.0/Bundle-DiagnosticReport-Imaging-DCM-example-01.json.html
- **Example 01 (v6.5.0)**: https://www.nrces.in/preview/ndhm/fhir/r4/Bundle-DiagnosticReport-Imaging-DCM-example-01.json.html

### OP Consultation Records
- **Example 05**: https://www.nrces.in/ndhm/fhir/r4/Bundle-OPConsultNote-example-05.json.html
- **Example 05 (v3.0.0)**: https://nrces.in/ndhm/fhir/r4/3.0.0/Bundle-OPConsultNote-example-05.json.html
- **Profile Definition**: https://www.nrces.in/ndhm/fhir/r4/StructureDefinition-OPConsultRecord.html

### Wellness Records
- **Example 01 (v6.5.0)**: https://nrces.in/ndhm/fhir/r4/Bundle-WellnessRecord-example-01.json.html
- **Example 01 (v4.0.0)**: https://nrces.in/ndhm/fhir/r4/4.0.0/Bundle-WellnessRecord-example-01.json.html

### Immunization Records
Available in the FHIR Implementation Guide under Health Information Types

### Individual Resource Examples

#### Patient Resources
- **Patient Example 01**: https://nrces.in/ndhm/fhir/r4/Patient-example-01.json.html
- **Patient Profile (JSON Schema)**: https://nrces.in/ndhm/fhir/r4/StructureDefinition-Patient.profile.json.html

#### Observation Resources
- **Observation Finding Example 01**: https://www.nrces.in/ndhm/fhir/r4/Observation-finding-example-01.json.html
- **Observation Example 17**: https://nrces.in/ndhm/fhir/r4/Observation-example-17.json.html
- **Observation Example 32**: https://www.nrces.in/ndhm/fhir/r4/Observation-example-32.json.html
- **Observation Example 35**: https://www.nrces.in/ndhm/fhir/r4/Observation-example-35.json.html
- **Lab Observation Example 01**: https://www.nrces.in/ndhm/fhir/r4/Observation-lab-example-01.html

#### Medication Resources
- **Medication Example 01**: https://nrces.in/ndhm/fhir/r4/Medication-example-01.json.html
- **Medication Example 03**: https://nrces.in/ndhm/fhir/r4/Medication-example-03.json.html

#### Practitioner Resources
- **Practitioner Profile**: https://www.nrces.in/ndhm/fhir/r4/StructureDefinition-Practitioner.profile.json.html
- **PractitionerRole Example 01**: https://nrces.in/ndhm/fhir/r4/PractitionerRole-example-01.json.html

#### Other Resources
- **DocumentReference Example 02**: https://www.nrces.in/ndhm/fhir/r4/DocumentReference-example-02.json.html
- **Binary Example 01**: https://www.nrces.in/ndhm/fhir/r4/Binary-example-01.json.html

## GitHub Repositories & Code Samples

### Official Repositories
- **ABDM Wrapper (NHA)**: https://github.com/NHA-ABDM/ABDM-wrapper
- **HL7 India Connectathon 2021**: https://github.com/HL7India/Connectathon2021/tree/main/abdmImplementation
- **ABDM HI Types Sample Code**: https://github.com/HL7India/Connectathon2021/tree/main/abdmImplementation/ABDM_HI_Types_Sample_code

### Community Repositories
- **ABDM Wrapper (Community)**: https://github.com/imvpathak/ABDM-Wrapper
- **ABDM Gateway SDK**: https://github.com/Technoculture/ABDM-Gateway-SDK
- **Bahmni India Package (Docker)**: https://github.com/BahmniIndiaDistro/bahmni-india-package
- **ABDM SDK**: https://github.com/atulai-sg/abdm-sdk
- **Fidelius CLI (Encryption)**: https://github.com/mgrmtech/fidelius-cli

## Documentation Portals

### Community Documentation
- **ABDM Sandbox Documentation**: https://kiranma72.github.io/abdm-docs/
- **CoronaSafe ABDM Documentation**: https://docs.coronasafe.network/abdm-documentation/
- **OHC Network Docs**: https://docs.ohc.network/docs/care/abdm/

### Middleware/Connector Documentation
- **EHR.Network ABDMc APIs**: https://docs.ehr.network/apidocs/abdmc.html
- **Eka Care ABDM Connect**: https://developer.eka.care/abdm-connect

### HL7 India Resources
- **ABDM Implementation Track**: https://confluence.hl7.org/spaces/HIN/pages/79510872/ABDM+Implementation+Track
- **Terminology Track**: https://confluence.hl7.org/display/HIN/Terminology+Track

## FHIR Validation Tools

### Validators
- **Official FHIR Validator**: https://validator.fhir.org/
- **HAPI FHIR Validator**: Documentation in hapi-fhir-validation module
- **Inferno Resource Validator**: http://inferno.healthit.gov/validator/

### Command Line Validation
```bash
java -jar validator_cli.jar resource.json -version 4.0.1 -ig https://nrces.in/ndhm/fhir/r4/
```

## FHIR Conversion Tools

### FHIR Connector
- **CDAC FHIR Connector**: https://ndhmexchange.uat.dcservices.in/FHIRConnector/
  - Converts simple JSON to ABDM FHIR Profile Bundles
  - Supports all 7 Health Information Types

## Terminology Resources

### SNOMED-CT Codes for Indian Context
- **Diabetes Mellitus**: 73211009
- **Type 2 Diabetes**: 44054006
- **Essential Hypertension**: 59621000
- **Tuberculosis**: 56717001
- **Dengue**: 38362002

### LOINC Codes (Common Lab Tests)
- **Lipid Panel**: 24331-1
- **Cholesterol**: 2093-3
- **Glucose (Blood)**: 2339-0
- **HbA1c**: 4548-4
- **Glucose Mean (from HbA1c)**: 27353-2

### References
- **SNOMED-CT Browser**: https://snomedbrowser.com/
- **LOINC Database**: https://loinc.org/
- **NRCeS SNOMED-CT**: https://www.nrces.in/standards/snomed-ct

## Postman Collections

### Official
- **ABDM Sandbox Postman**: https://sandbox.abdm.gov.in/docs/postman_collections

### Community
- **M2-M3 Workshop**: https://www.postman.com/mgrm-tech/abdm-m2-m3-workshop/overview

## Encryption & Security

### Encryption Documentation
- **ECDH with Curve25519**: Used for health data encryption
- **Encryption Guidelines**: https://github.com/mgrmtech/fidelius-cli/blob/main/abdm/Encryption%20and%20Decryption%20Implementation%20Guidelines%20for%20FHIR%20data%20in%20ABDM.md
- **Encoding & RSA**: https://sandbox.abdm.gov.in/abdm-docs/EncodingAndEncryption

### Security Standards
- **Web App Security**: CERT-IN empaneled agency audit required for production
- **Authentication**: JWT tokens via `/v0.5/sessions` endpoint
- **Transport**: HTTPS with TLS

## Synthetic Data Generation

### Tools
- **Synthea**: https://synthetichealth.github.io/synthea/
  - Generates FHIR R4 compliant synthetic patient data
  - Downloads: https://synthea.mitre.org/downloads
  - GitHub: https://github.com/synthetichealth/synthea

### SDV (Synthetic Data Vault)
- General-purpose synthetic data generation for tabular metadata

## Testing & Sandbox

### Sandbox Environments
- **Main Sandbox Portal**: https://sandbox.abdm.gov.in/
- **PHR App Sandbox**: https://phrsbx.abdm.gov.in/
- **EMR Sandbox**: https://emrsbx.ndhm.gov.in/

### Webhook Testing
- **Webhook.site**: https://webhook.site/ (for testing async callbacks)

## Python Libraries

### FHIR Libraries
- **fhir.resources**: Python library for FHIR R4 resources
- **ABDM PyPI**: https://pypi.org/project/abdm/

### Validation
- **hapi-fhir-validation**: FHIR resource validation

## Middleware Solutions

### EHR.Network
- **ABDMc (ABDM Connect)**: Simplifies async APIs to sync REST
- **ABDMmw (ABDM Middleware)**: Data format conversion
- OpenAPI 3.0 specs available

### ABDM Wrapper
- **Purpose**: Abstracts M2 (HIP) and M3 (HIU) workflows
- **Stack**: Spring Boot + MongoDB
- **Docker**: Compose files for local deployment

## Forum & Community Support

### Official Forums
- **ABDM Sandbox Forum**: https://devforum.abdm.gov.in/

### Community Resources
- **LOINC India Mapping**: https://github.com/kiranma72/loinc-india

## Reference Implementations

### Bahmni
- **ABDM Integration**: https://bahmni.atlassian.net/wiki/spaces/BAH/pages/2901114904/Bahmni+as+Health+Information+Provider+ABDM+NDHM
- **Docker Setup**: https://bahmni.atlassian.net/wiki/spaces/BAH/pages/3148087297/Running+Bahmni+with+ABDM+Integration+on+Docker
- **HI Types Support**: https://bahmni.atlassian.net/wiki/spaces/BAH/pages/3162079253/Support+for+Health+Information+Types

## Health Information Types (SNOMED Codes)

### All 7 ABDM HI Types
1. **Prescription Record**: 440545006
2. **Diagnostic Report**: 721981007
3. **OP Consultation**: 371530004
4. **Discharge Summary**: 373942005
5. **Immunization Record**: 41000179103
6. **Health Document Record**: 419891008
7. **Wellness Record**: (defined in wellness profile)

## Purpose of Use Codes

- **CAREMGT**: Care Management
- **BTG**: Break the Glass (emergencies)
- **PUBHLTH**: Public Health
- **HPAYMT**: Healthcare Payment
- **DSRCH**: Disease-specific research
- **PATRQT**: Patient self-requested

---

**Compilation Date**: 2026-02-14
**ABDM Version**: 6.5.0
**Compiled By**: Extensive web research across 40+ sources
