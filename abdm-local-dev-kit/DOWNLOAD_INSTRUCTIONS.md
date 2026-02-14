# How to Download Complete ABDM Resources

This guide shows you how to download all official ABDM FHIR profiles, examples, and API schemas.

## Official NRCES FHIR Resources

### Download Complete Package

Visit: https://www.nrces.in/ndhm/fhir/r4/downloads.html

Download the following files:

#### 1. NPM Package (Recommended for Validation)
```bash
# Download package.tgz
wget https://www.nrces.in/ndhm/fhir/r4/package.tgz

# Extract
tar -xzf package.tgz -C ./abdm-local-dev-kit/fhir-profiles/
```

Contains all value sets, profiles, and implementation guide metadata.

#### 2. Profile Definitions

**JSON Format** (recommended):
```bash
wget https://www.nrces.in/ndhm/fhir/r4/definitions.json.zip
unzip definitions.json.zip -d ./abdm-local-dev-kit/fhir-profiles/json/
```

**XML Format**:
```bash
wget https://www.nrces.in/ndhm/fhir/r4/definitions.xml.zip
unzip definitions.xml.zip -d ./abdm-local-dev-kit/fhir-profiles/xml/
```

#### 3. Example Bundles

**JSON Format**:
```bash
wget https://www.nrces.in/ndhm/fhir/r4/examples.json.zip
unzip examples.json.zip -d ./abdm-local-dev-kit/fhir-samples/official/
```

**XML Format**:
```bash
wget https://www.nrces.in/ndhm/fhir/r4/examples.xml.zip
unzip examples.xml.zip -d ./abdm-local-dev-kit/fhir-samples/official-xml/
```

## API Swagger Specifications

### Download All Swagger Files

```bash
cd abdm-local-dev-kit/api-schemas/

# Gateway APIs
curl -o gateway.yaml https://sandbox.abdm.gov.in/swagger/ndhm-gateway.yaml
curl -o consent-manager.yaml https://sandbox.abdm.gov.in/swagger/ndhm-cm.yaml
curl -o dev-service.yaml https://sandbox.abdm.gov.in/swagger/ndhm-devservice.yaml

# HIP/HIU APIs
curl -o hip.yaml https://sandbox.abdm.gov.in/swagger/ndhm-hip.yaml
curl -o hiu.yaml https://sandbox.abdm.gov.in/swagger/ndhm-hiu.yaml
curl -o bridge.yaml https://sandbox.abdm.gov.in/swagger/ndhm-bridge.yaml

# ABHA Service
curl -o phr-app-login.yaml https://sandbox.abdm.gov.in/swagger/ndhm-phr-app2.yaml
curl -o phr-app-consent.yaml https://sandbox.abdm.gov.in/swagger/ndhm-phr-app.yaml
curl -o link-token-service.yaml https://sandbox.abdm.gov.in/swagger/HIECM-LinkTokenService.yaml

# Health ID (if accessible)
curl -o health-id.json https://sandbox.abdm.gov.in/swagger/ndhm-healthid.json
```

**Note**: Some swagger files may return 503 errors if the sandbox is under maintenance. Try again later or check the official documentation.

## Individual FHIR Example Downloads

You can download individual examples directly from NRCES:

### Discharge Summary
```bash
curl -o discharge-summary-example-04.json \
  "https://www.nrces.in/ndhm/fhir/r4/Bundle-DischargeSummary-example-04.json.html" \
  | grep -A 10000 '"resourceType": "Bundle"' > discharge-summary.json
```

### Prescription
```bash
curl -o prescription-example-06.json \
  "https://www.nrces.in/ndhm/fhir/r4/Bundle-Prescription-example-06.json.html" \
  | grep -A 10000 '"resourceType": "Bundle"' > prescription.json
```

### Diagnostic Report (Lab)
```bash
curl -o diagnostic-lab-example-03.json \
  "https://www.nrces.in/ndhm/fhir/r4/Bundle-DiagnosticReport-Lab-example-03.json.html" \
  | grep -A 10000 '"resourceType": "Bundle"' > diagnostic-lab.json
```

### OP Consultation
```bash
curl -o op-consult-example-05.json \
  "https://www.nrces.in/ndhm/fhir/r4/Bundle-OPConsultNote-example-05.json.html" \
  | grep -A 10000 '"resourceType": "Bundle"' > op-consult.json
```

### Wellness Record
```bash
curl -o wellness-example-01.json \
  "https://nrces.in/ndhm/fhir/r4/Bundle-WellnessRecord-example-01.json.html" \
  | grep -A 10000 '"resourceType": "Bundle"' > wellness.json
```

### Patient Resource
```bash
curl -o patient-example-01.json \
  "https://nrces.in/ndhm/fhir/r4/Patient-example-01.json.html" \
  | grep -A 100 '"resourceType": "Patient"' > patient.json
```

## GitHub Repositories

### HL7 India ABDM Samples

```bash
# Clone the repository
git clone https://github.com/HL7India/Connectathon2021.git

# Navigate to ABDM samples
cd Connectathon2021/abdmImplementation/ABDM_HI_Types_Sample_code/

# Files include:
# - DiagnosticReportRecordABDMTrackUsecase.json
# - OPConsultNote_for_ABDMTrack_usecase.json
# - Java implementation files
```

### ABDM Wrapper

```bash
# Clone official ABDM wrapper
git clone https://github.com/NHA-ABDM/ABDM-wrapper.git

cd ABDM-wrapper

# Contains:
# - Docker compose files
# - Sample HIP/HIU implementations
# - API documentation
# - Configuration examples
```

## Implementation Guides (PDFs)

```bash
cd abdm-local-dev-kit/docs/pdfs/

# FHIR Adoption Guide
curl -o FHIR_Adoption_Guide.pdf \
  "https://www.nrces.in/download/files/pdf/Implementation_Guide_for_Adoption_of_FHIR_in_ABDM_and_NHCX.pdf"

# Introduction to FHIR
curl -o FHIR_Introduction.pdf \
  "https://www.nrces.in/download/files/pdf/nrces_Brief%20Introduction%20to%20FHIR%20&%20Walkthrough%20to%20FHIR%20Implementation%20Guide%20for%20ABDM.pdf"

# LOINC Usage Guide
curl -o LOINC_Usage_Guide.pdf \
  "https://www.nrces.in/download/files/pdf/Guide%20for%20using%20LOINC%20in%20ABDM%20FHIR%20Resources.pdf"

# Terminology Server Setup
curl -o Terminology_Server_Setup.pdf \
  "https://www.nrces.in/download/files/pdf/Guide_to_Setup_FHIR_Terminology_Server.pdf"
```

## Terminology Downloads

### SNOMED-CT
Contact NRCeS for Indian extension licensing:
- **Website**: https://www.nrces.in/standards/snomed-ct
- **Email**: Contact through NRCES website

### LOINC
Download from official LOINC website:
- **URL**: https://loinc.org/downloads/
- **License**: Free for use

### ICD-10
Available from WHO:
- **URL**: https://www.who.int/standards/classifications/classification-of-diseases

## Synthea (Synthetic Data Generator)

```bash
# Download Synthea
wget https://github.com/synthetichealth/synthea/releases/latest/download/synthea-with-dependencies.jar

# Generate 100 synthetic patients (FHIR R4)
java -jar synthea-with-dependencies.jar -p 100 --exporter.fhir.export=true

# Output will be in ./output/fhir/
```

## FHIR Validator

```bash
# Download FHIR Validator
curl -L -o validator_cli.jar \
  https://github.com/hapifhir/org.hl7.fhir.core/releases/latest/download/validator_cli.jar

# Validate against ABDM profiles
java -jar validator_cli.jar your-bundle.json \
  -version 4.0.1 \
  -ig https://nrces.in/ndhm/fhir/r4/
```

## Verify Downloads

After downloading, verify your directory structure:

```bash
tree abdm-local-dev-kit/

# Expected structure:
# abdm-local-dev-kit/
# ├── api-schemas/          (Swagger YAML files)
# ├── docs/                 (Markdown documentation)
# │   └── pdfs/            (PDF guides)
# ├── fhir-profiles/       (NPM package, definitions)
# │   ├── json/
# │   └── xml/
# ├── fhir-samples/        (Example bundles)
# │   └── official/
# ├── mock-data/           (Synthetic data)
# ├── scripts/             (Utility scripts)
# └── tools/               (Validators, generators)
```

## Troubleshooting

### 503 Errors on Swagger Files
- The sandbox may be under maintenance
- Try again after a few hours
- Check ABDM forum: https://devforum.abdm.gov.in/

### Large File Downloads
- Use `-C -` with curl to resume interrupted downloads:
  ```bash
  curl -C - -o large-file.zip https://url/to/file.zip
  ```

### HTML Instead of JSON
- Some URLs return HTML wrappers around JSON
- Use `grep` or manual extraction to get pure JSON
- Or use browser "View Source" and save

## Quick Setup Script

```bash
#!/bin/bash
# quick-download.sh - Download essential ABDM resources

cd abdm-local-dev-kit/

# Create directories
mkdir -p {api-schemas,fhir-profiles/{json,xml},fhir-samples/official,docs/pdfs}

# Download FHIR resources
cd fhir-profiles/
wget https://www.nrces.in/ndhm/fhir/r4/package.tgz
wget https://www.nrces.in/ndhm/fhir/r4/definitions.json.zip
wget https://www.nrces.in/ndhm/fhir/r4/examples.json.zip
tar -xzf package.tgz
unzip definitions.json.zip -d json/
unzip examples.json.zip -d ../fhir-samples/official/

# Download API schemas
cd ../api-schemas/
for file in gateway consent-manager dev-service hip hiu bridge; do
  curl -o ${file}.yaml https://sandbox.abdm.gov.in/swagger/ndhm-${file}.yaml 2>/dev/null || echo "Failed: ${file}"
done

echo "Download complete! Check abdm-local-dev-kit/ directory."
```

Make executable and run:
```bash
chmod +x quick-download.sh
./quick-download.sh
```

---

*Last Updated: 2026-02-14*
*Ensure you have proper network access and sufficient disk space (~500MB)*
