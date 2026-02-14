# Synthea Dynamic Data Generation

## Overview

The pipeline uses [Synthea](https://github.com/synthetichealth/synthea) to generate realistic synthetic patient populations. Synthea produces FHIR R4 transaction bundles per patient, which are then used in two ways:

1. **Direct ingestion** — the `SyntheaAdapter` feeds raw bundles into the FHIR pipeline
2. **Multi-source simulation** — patient demographics and clinical data are extracted and used to drive 6 format-specific simulators (wearables, ambulance, EHR, handwritten notes, bedside vitals, scans/labs)

Every run produces **different patients** with unique names, demographics, conditions, medications, and lab values. All data for a given patient is internally coherent across all 6 output formats.

---

## Synthea FHIR Bundle (input)

Each Synthea JSON file is a FHIR `Bundle` of type `transaction` representing one patient's full medical history.

| Resource Type         | Typical Count | Description                                    |
|-----------------------|---------------|------------------------------------------------|
| `Patient`             | 1             | Demographics, identifiers, address, telecom    |
| `Encounter`           | 17–393        | Ambulatory visits, emergency, inpatient stays  |
| `Condition`           | 20–50         | Active/resolved diagnoses (SNOMED coded)       |
| `Observation`         | 93–6545       | Vitals, labs, social history, surveys          |
| `Procedure`           | 45–1035       | Surgeries, screenings, therapies               |
| `MedicationRequest`   | 1–637         | Prescribed medications (RxNorm coded)          |
| `DiagnosticReport`    | 33–1032       | Lab panels, imaging reports                    |
| `Immunization`        | 5–30          | Vaccination records                            |
| `DocumentReference`   | 17–393        | Clinical document references                   |
| `Claim`               | 19–927        | Insurance claims                               |
| `ExplanationOfBenefit`| 19–927        | Claim adjudication results                     |

### Patient Resource Fields

| Field         | Example                                       | Source              |
|---------------|-----------------------------------------------|---------------------|
| `id`          | `d7777ad5-012d-b235-4ecb-6e9f46f525ab`        | Synthea UUID        |
| `name`        | `Reid278 Eichmann909`                          | Synthea randomized  |
| `gender`      | `male`                                         | Synthea randomized  |
| `birthDate`   | `1966-03-06`                                   | Synthea randomized  |
| `address`     | `594 Pfannerstill Lane, Chelsea, MA 02150`     | Synthea geo-aware   |
| `telecom`     | `555-XXX-XXXX`                                 | Synthea randomized  |
| `identifier`  | MRN, SSN, DL, Passport                         | Synthea generated   |
| `maritalStatus` | `S` / `M` / `D`                             | Synthea randomized  |
| `communication` | `en-US`, `es`                                | Synthea demographic |

---

## Extracted Profile & Scenario

The generator bridges Synthea data into the simulator framework by extracting:

### PatientProfile (demographics)

| Field          | Description                              | Example                              |
|----------------|------------------------------------------|--------------------------------------|
| `name`         | Full name from Patient resource          | `Reid278 Eichmann909`                |
| `given_name`   | First given name                         | `Reid278`                            |
| `family_name`  | Family name                              | `Eichmann909`                        |
| `dob`          | Birth date (ISO)                         | `1966-03-06`                         |
| `gender`       | `male` / `female`                        | `male`                               |
| `mrn`          | Medical record number from identifiers   | `d7777ad5-012d-b235-4ecb-...`        |
| `abha_id`      | Deterministic ABHA ID from patient UUID  | `ABHA-33-2705-6471-1262`            |
| `phone`        | Phone from telecom, or generated +91 number | `555-344-4434`                    |
| `address`      | Concatenated address line + city + state | `594 Pfannerstill Lane, Chelsea, MA` |

### ClinicalScenario (clinical data)

| Field              | Description                                                | Example                                     |
|--------------------|------------------------------------------------------------|---------------------------------------------|
| `name`             | Generated scenario ID                                      | `synthea_metabolic_4067`                    |
| `chief_complaint`  | From most recent Encounter reason or top Condition         | `Viral sinusitis (disorder)`                |
| `diagnoses`        | Top 5 Conditions, SNOMED-to-ICD-10 mapped                 | `[{code: "I10", display: "Essential hypertension"}]` |
| `baseline_hr`      | Heart rate (bpm), range depends on condition category      | `104.3`                                     |
| `baseline_bp_sys`  | Systolic BP (mmHg)                                         | `122.7`                                     |
| `baseline_bp_dia`  | Diastolic BP (mmHg)                                        | `61.5`                                      |
| `baseline_spo2`    | Oxygen saturation (%)                                      | `97.9`                                      |
| `baseline_temp`    | Temperature (C)                                            | `36.8`                                      |
| `baseline_rr`      | Respiratory rate (/min)                                    | `22.7`                                      |
| `vital_trend`      | `improving` or `stable`                                    | `improving`                                 |
| `labs`             | Up to 7 lab results with LOINC codes and reference ranges  | See table below                             |
| `medications`      | Up to 5 medication names from MedicationRequests           | `["Simvastatin 10 MG Oral Tablet", ...]`    |

### Vital Sign Ranges by Condition Category

The system classifies diagnoses into categories and selects clinically appropriate vital ranges:

| Category      | HR (bpm)  | BP Sys (mmHg) | BP Dia (mmHg) | SpO2 (%) | Temp (C)  | RR (/min) | Triggered by keywords                              |
|---------------|-----------|---------------|---------------|----------|-----------|-----------|-----------------------------------------------------|
| **Cardiac**   | 90-120    | 140-180       | 85-100        | 91-96    | 36.5-37.5 | 18-26     | myocardial, coronary, heart, atrial, angina         |
| **Respiratory**| 100-120  | 120-145       | 75-90         | 85-93    | 36.8-38.5 | 24-35     | asthma, copd, pneumonia, bronchitis, lung           |
| **Metabolic** | 95-120    | 90-130        | 55-80         | 95-99    | 36.5-38.0 | 20-30     | diabetes, hyperglycemia, ketoacidosis, thyroid      |
| **Trauma**    | 110-130   | 80-110        | 50-70         | 90-96    | 35.5-37.0 | 22-30     | fracture, concussion, injury, laceration            |
| **General**   | 70-90     | 110-135       | 65-85         | 96-99    | 36.4-37.2 | 14-20     | Default when no specific keywords match             |

### Lab Values

Labs are extracted from Synthea Observations when LOINC codes match, otherwise generated with condition-appropriate abnormalities.

| LOINC Code | Name              | Unit           | Reference Range | Notes                        |
|------------|-------------------|----------------|-----------------|------------------------------|
| `6598-7`   | Troponin T        | ng/mL          | 0.0-0.04        | Added for cardiac category   |
| `718-7`    | Hemoglobin        | g/dL           | 12.0-16.0       | Always included              |
| `6690-2`   | WBC               | 10*3/uL        | 4.5-11.0        | Always included              |
| `2345-7`   | Glucose           | mg/dL          | 70-100          | Added for metabolic category |
| `2160-0`   | Creatinine        | mg/dL          | 0.7-1.3         | Always included              |
| `2951-2`   | Sodium            | mmol/L         | 136-145         | Always included              |
| `2823-3`   | Potassium         | mmol/L         | 3.5-5.0         | Always included              |
| `2093-3`   | Total Cholesterol | mg/dL          | 0-200           | When present in Synthea      |
| `2085-9`   | HDL Cholesterol   | mg/dL          | 40-60           | When present in Synthea      |
| `13457-7`  | LDL Cholesterol   | mg/dL          | 0-100           | When present in Synthea      |
| `2571-8`   | Triglycerides     | mg/dL          | 0-150           | When present in Synthea      |
| `4548-4`   | HbA1c             | %              | 4.0-5.6         | Added for metabolic category |
| `33914-3`  | eGFR              | mL/min/1.73m2  | 60-120          | When present in Synthea      |
| `777-3`    | Platelet Count    | 10*3/uL        | 150-400         | When present in Synthea      |

---

## Simulator Outputs (per patient)

Each patient gets a dedicated directory with all 6 source types:

```
<patient_name>_NNN/
  wearables/
    sim_apple_health.xml        Apple HealthKit export (HR, SpO2, temp, RR)
    sim_google_fit.json         Google Fit data points (HR, SpO2)
  ambulance/
    sim_ems_run.xml             NEMSIS v3 EMS patient care report
  ehr/
    sim_admission.hl7           HL7 v2.5 ADT^A01 (demographics, vitals, diagnoses)
    sim_lab_results.hl7         HL7 v2.5 ORU^R01 (lab panel results)
  handwritten/
    sim_clinical_note.png       Simulated handwritten clinical note image
  realtime_vitals/
    sim_bedside_stream.json     Bedside monitor numeric readings (8 timepoints)
    sim_ecg_waveform.csv        ECG Lead II waveform (250 Hz, 2 sec)
  scans_labs/
    sim_chest_xray.dcm          DICOM chest X-ray (requires pydicom)
    sim_lab_report.pdf          PDF lab report (requires reportlab)
```

### Source Format Details

| Source             | Format      | Key Fields                                                          |
|--------------------|-------------|---------------------------------------------------------------------|
| Apple Health       | XML         | `HKQuantityTypeIdentifier*` records with timestamps, values, units  |
| Google Fit         | JSON        | `dataPoints[]` with `dataTypeName`, `timestamp`, `value`            |
| NEMSIS Ambulance   | XML         | Patient demographics, dispatch/arrival times, 3 vital sets          |
| EHR Admission      | HL7 v2.5    | `MSH`, `PID`, `PV1`, `DG1` (diagnoses), `OBX` (vitals)            |
| EHR Lab Results    | HL7 v2.5    | `MSH`, `PID`, `OBR`, `OBX` (lab values with reference ranges)      |
| Handwritten Note   | PNG image   | Patient name, MRN, chief complaint, vitals, assessment, plan        |
| Bedside Monitor    | JSON        | Device info, patient ID, 8 timestamped vital readings               |
| ECG Waveform       | CSV         | `timestamp`, `patient_id`, `ecg_lead_ii` at 250 Hz                 |
| Chest X-ray        | DICOM       | Patient metadata, 64x64 placeholder image                          |
| Lab Report         | PDF         | Formatted lab panel with reference ranges                           |

---

## Usage

```bash
# Generate N fresh patients with Synthea JAR, then simulate all sources
python -m ingest.simulators.runner \
  --synthea dummy \
  --synthea-jar tools/synthea-with-dependencies.jar \
  --population 10 \
  -o output/

# Use pre-generated Synthea JSON files
python -m ingest.simulators.runner \
  --synthea sample_data/synthea/ \
  -o output/

# Static mode (original hardcoded scenarios, still works)
python -m ingest.simulators.runner -s chest_pain -o output/

# Ingest any directory (auto-detects Synthea bundles + all other formats)
python -m ingest.pipeline.ingestion -i output/ -o fhir_output/
```

## Setup

Synthea requires Java 11+. The generator auto-detects brew-installed OpenJDK:

```bash
brew install openjdk@17
```

Download the Synthea JAR (one-time, ~170MB):

```bash
mkdir -p ingestion/tools
curl -L -o ingestion/tools/synthea-with-dependencies.jar \
  "https://github.com/synthetichealth/synthea/releases/download/master-branch-latest/synthea-with-dependencies.jar"
```
