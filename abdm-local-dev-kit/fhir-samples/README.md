# FHIR Sample Data

This directory contains sample FHIR R4 bundles conforming to ABDM (Ayushman Bharat Digital Mission) profiles.

## Directory Structure

```
fhir-samples/
├── discharge-summaries/    # Hospital discharge summary documents
├── prescriptions/           # Medication prescription records
├── diagnostic-reports/      # Lab and imaging reports
│   ├── lab/                # Laboratory test reports
│   └── imaging/            # Radiology and imaging reports
├── op-consultations/        # Outpatient consultation notes
├── immunization-records/    # Vaccination records
├── wellness-records/        # Vital signs and wellness data
├── health-documents/        # Unstructured health documents
└── core-resources/          # Individual FHIR resources
    ├── patients/
    ├── practitioners/
    ├── organizations/
    ├── observations/
    ├── conditions/
    └── medications/
```

## Health Information Types

ABDM defines 7 core Health Information (HI) Types:

### 1. Discharge Summary (SNOMED: 373942005)
**File**: `discharge-summaries/example-discharge-summary-01.json`

Hospital discharge summaries containing:
- Chief complaints and medical history
- Physical examination findings
- Investigations and procedures
- Discharge medications
- Follow-up care plans

**Profile**: https://nrces.in/ndhm/fhir/r4/StructureDefinition/DischargeSummaryRecord

---

### 2. Prescription Record (SNOMED: 440545006)
**File**: `prescriptions/example-prescription-01.json`

Medication prescriptions including:
- Patient and practitioner details
- Medication requests with dosage instructions
- Diagnosis/conditions
- Valid dates and refills

**Profile**: https://nrces.in/ndhm/fhir/r4/StructureDefinition/PrescriptionRecord

---

### 3. Diagnostic Report (SNOMED: 721981007)
**Files**:
- `diagnostic-reports/lab/example-lab-report-01.json` (Blood work)
- `diagnostic-reports/imaging/example-xray-01.json` (Radiology)

Laboratory and imaging reports with:
- Test panels and individual observations
- LOINC-coded tests
- Reference ranges and interpretations
- Specimen details

**Profile**: https://nrces.in/ndhm/fhir/r4/StructureDefinition/DiagnosticReportLab

---

### 4. OP Consultation (SNOMED: 371530004)
**File**: `op-consultations/example-op-consult-01.json`

Outpatient visit records containing:
- Chief complaints
- Clinical findings
- Assessment and diagnosis
- Treatment plan
- Medications administered

**Profile**: https://nrces.in/ndhm/fhir/r4/StructureDefinition/OPConsultRecord

---

### 5. Immunization Record (SNOMED: 41000179103)
**File**: `immunization-records/example-immunization-01.json`

Vaccination records with:
- Vaccine details
- Administration date and route
- Dose number in series
- Adverse reactions if any

**Profile**: https://nrces.in/ndhm/fhir/r4/StructureDefinition/ImmunizationRecord

---

### 6. Wellness Record
**File**: `wellness-records/example-wellness-01.json`

Regular wellness monitoring data:
- Vital signs (BP, pulse, temperature, SpO2)
- Physical measurements (height, weight, BMI)
- Blood glucose
- Physical activity

**Profile**: https://nrces.in/ndhm/fhir/r4/StructureDefinition/WellnessRecord

---

### 7. Health Document Record (SNOMED: 419891008)
**File**: `health-documents/example-health-document-01.json`

Unstructured historical records:
- Scanned documents
- Legacy health records
- PDF attachments

**Profile**: https://nrces.in/ndhm/fhir/r4/StructureDefinition/HealthDocumentRecord

---

## Common FHIR Bundle Structure

All ABDM Health Information Types use FHIR Document Bundles:

```json
{
  "resourceType": "Bundle",
  "type": "document",
  "entry": [
    {
      "fullUrl": "urn:uuid:composition-id",
      "resource": {
        "resourceType": "Composition",
        "status": "final",
        "type": {...},
        "subject": {...},
        "section": [...]
      }
    },
    {
      "fullUrl": "urn:uuid:patient-id",
      "resource": {"resourceType": "Patient", ...}
    },
    ...
  ]
}
```

## Indian Context Specifics

### ABHA Number Format
- **Health ID Number**: 14-digit format `22-7225-4829-5255`
- **Health ID**: Username format `username@abdm`

### Common Terminologies

**SNOMED-CT Codes** (Indian Diseases):
- Diabetes Mellitus: `73211009`
- Type 2 Diabetes: `44054006`
- Essential Hypertension: `59621000`
- Tuberculosis: `56717001`
- Dengue: `38362002`

**LOINC Codes** (Lab Tests):
- Lipid Panel: `24331-1`
- Cholesterol: `2093-3`
- HbA1c: `4548-4`
- CBC: `58410-2`
- Glucose (Fasting): `1558-6`

## Source Attribution

All samples are based on official NRCES FHIR Implementation Guide for ABDM v6.5.0:
- **Official Source**: https://nrces.in/ndhm/fhir/r4/
- **Downloads**: https://www.nrces.in/ndhm/fhir/r4/downloads.html

To get the complete official sample set, download:
- `examples.json.zip` from the NRCES downloads page

## Validation

Validate bundles using the FHIR validator with ABDM profiles:

```bash
java -jar validator_cli.jar bundle.json \
  -version 4.0.1 \
  -ig https://nrces.in/ndhm/fhir/r4/
```

## Usage for Hackathon

For the AI-Powered Smart Patient Triage Hackathon:

1. **Parse Discharge Summaries**: Extract conditions, procedures, medications
2. **Analyze Lab Reports**: Get vital lab values (glucose, cholesterol, etc.)
3. **Extract Prescriptions**: Identify current medications
4. **Combine Data**: Build comprehensive patient profiles for triage ML model

---

*Last Updated: 2026-02-14*
*FHIR Version: R4*
*ABDM IG Version: 6.5.0*
