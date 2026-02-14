# Patient.ly — Data Schema Reference

## Overview

Patient.ly does not use a traditional database. All data flows through an in-memory pipeline and is output as **FHIR R4 JSON** files (ABDM-compliant, NRCES India profiles). There are three schema layers:

1. **Internal Data Model** — Python dataclasses used during processing
2. **FHIR R4 Resources** — The output format (per-patient Transaction Bundles)
3. **Coding Systems** — Standardized medical vocabularies used across all resources

---

## Layer 1: Internal Data Model

### PatientIdentity

Extracted patient identifying info used for cross-source linking.

| Field | Type | Required | Description |
|---|---|---|---|
| `source_id` | `str` | **Yes** | Unique ID within the source system |
| `source_system` | `str` | **Yes** | Source identifier (e.g. `"apple_health"`, `"hospital_ehr"`) |
| `full_name` | `str \| None` | No | Full name (e.g. `"Rajesh Kumar"`) |
| `given_name` | `str \| None` | No | First/given name |
| `family_name` | `str \| None` | No | Last/family name |
| `birth_date` | `str \| None` | No | ISO format `YYYY-MM-DD` |
| `gender` | `str \| None` | No | `"male"` / `"female"` / `"other"` / `"unknown"` |
| `phone` | `str \| None` | No | Phone number |
| `email` | `str \| None` | No | Email address |
| `mrn` | `str \| None` | No | Medical Record Number |
| `abha_id` | `str \| None` | No | ABDM Health ID (Ayushman Bharat) |
| `address_line` | `str \| None` | No | Street address |
| `address_city` | `str \| None` | No | City |
| `address_state` | `str \| None` | No | State |
| `address_postal_code` | `str \| None` | No | PIN/postal code |

### AdapterResult

Standardized output from any source adapter.

| Field | Type | Required | Description |
|---|---|---|---|
| `patient_identity` | `PatientIdentity` | **Yes** | Extracted patient info |
| `fhir_resources` | `list[Resource]` | **Yes** | List of FHIR resources (can be empty) |
| `fhir_patient` | `FHIRPatient \| None` | No | Pre-built FHIR Patient resource |
| `source_type` | `str` | No | Source type identifier (defaults to `""`) |
| `raw_metadata` | `dict` | No | Additional metadata (defaults to `{}`) |

### LinkedPatient

A unified patient record aggregated from multiple sources after linking.

| Field | Type | Required | Description |
|---|---|---|---|
| `canonical_id` | `str` | **Yes** | Auto-generated UUID |
| `identities` | `list[PatientIdentity]` | **Yes** | All source identities for this patient |
| `fhir_patient` | `FHIRPatient \| None` | No | Merged FHIR Patient (most complete fields) |
| `all_resources` | `list[Resource]` | **Yes** | All FHIR resources from all sources |
| `source_types` | `set[str]` | **Yes** | Set of source types that contributed |

---

## Layer 2: FHIR R4 Resource Schemas

All output resources conform to the FHIR R4 specification. Fields marked **FHIR Required** are mandated by the spec; fields marked **Conditionally Included** are only present when the source data provides them.

### Patient

NRCES India profile: `https://nrces.in/ndhm/fhir/r4/StructureDefinition/Patient`

| Field | FHIR Required | Behavior |
|---|---|---|
| `resourceType` | Yes | Always `"Patient"` |
| `id` | Yes | Auto-generated UUID |
| `meta.profile` | No | Always set to NRCES Patient profile |
| `identifier` (MRN) | No | Conditionally included — only if MRN exists |
| `identifier` (ABHA) | No | Conditionally included — only if ABHA ID exists |
| `name` | No | Conditionally included — only if any name part exists |
| `gender` | No | Conditionally included — only if gender is known |
| `birthDate` | No | Conditionally included — only if DOB is known |
| `telecom` (phone) | No | Conditionally included — only if phone exists |
| `address` | No | Conditionally included — only if any address part exists |

### Observation (vital-signs)

| Field | FHIR Required | Behavior |
|---|---|---|
| `resourceType` | Yes | Always `"Observation"` |
| `id` | Yes | Auto-generated UUID |
| `status` | Yes | Always `"final"` |
| `category` | No | Always `"vital-signs"` |
| `code.coding` | Yes | LOINC code (e.g. `8867-4` for heart rate) |
| `subject` | No | Always set — reference to Patient |
| `effectiveDateTime` | No | Always set from source data |
| `valueQuantity.value` | No | Numeric vital sign value |
| `valueQuantity.unit` | No | Display unit (e.g. `"beats/minute"`) |
| `valueQuantity.system` | No | Always `http://unitsofmeasure.org` |
| `valueQuantity.code` | No | UCUM code (e.g. `"/min"`) |

### Observation (blood pressure)

Uses component-based structure per FHIR BP panel profile.

| Field | FHIR Required | Behavior |
|---|---|---|
| `code.coding` | Yes | `85354-9` (Blood pressure panel) |
| `component[0].code` | No | `8480-6` (Systolic) |
| `component[0].valueQuantity` | No | Systolic value in `mm[Hg]` |
| `component[1].code` | No | `8462-4` (Diastolic) |
| `component[1].valueQuantity` | No | Diastolic value in `mm[Hg]` |

### Observation (laboratory)

| Field | FHIR Required | Behavior |
|---|---|---|
| `category` | No | Always `"laboratory"` |
| `code.coding` | Yes | LOINC code for the lab test |
| `valueQuantity` | No | Numeric result with unit |
| `referenceRange` | No | Conditionally included — only if reference range exists |
| `referenceRange[0].low` | No | Lower bound of normal range |
| `referenceRange[0].high` | No | Upper bound of normal range |

### Observation (SampledData — ECG waveform)

| Field | FHIR Required | Behavior |
|---|---|---|
| `code.coding` | Yes | LOINC code (e.g. `131328` for ECG lead II) |
| `valueSampledData.origin` | No | Baseline value and unit (e.g. `0.0 mV`) |
| `valueSampledData.period` | No | Sampling interval in ms (e.g. `4.0` = 250Hz) |
| `valueSampledData.dimensions` | No | Number of channels (e.g. `1`) |
| `valueSampledData.data` | No | Space-separated sample values |

### Encounter

| Field | FHIR Required | Behavior |
|---|---|---|
| `resourceType` | Yes | Always `"Encounter"` |
| `id` | Yes | Auto-generated UUID |
| `status` | Yes | `"finished"` or `"in-progress"` |
| `class` | Yes | `EMER` / `IMP` / `AMB` from source data |
| `subject` | No | Always set — reference to Patient |
| `period.start` | No | Always set (falls back to `2026-01-01T00:00:00Z`) |
| `period.end` | No | Conditionally included — only if end time exists |

### Condition

| Field | FHIR Required | Behavior |
|---|---|---|
| `resourceType` | Yes | Always `"Condition"` |
| `id` | Yes | Auto-generated UUID |
| `clinicalStatus` | Yes | Always `"active"` |
| `verificationStatus` | No | Always `"confirmed"` |
| `category` | No | Always `"encounter-diagnosis"` |
| `code.coding` | Yes | ICD-10 or SNOMED-CT code from source |
| `subject` | No | Always set — reference to Patient |
| `onsetDateTime` | No | Conditionally included — only if onset date exists |

### DocumentReference

Used for handwritten notes (PNG), lab PDFs, and DICOM files.

| Field | FHIR Required | Behavior |
|---|---|---|
| `resourceType` | Yes | Always `"DocumentReference"` |
| `id` | Yes | Auto-generated UUID |
| `status` | Yes | Always `"current"` |
| `docStatus` | No | Always `"final"` |
| `type` | No | LOINC document type code |
| `subject` | No | Always set — reference to Patient |
| `date` | No | Always set to ingestion timestamp |
| `description` | No | Human-readable description |
| `content[0].attachment.contentType` | Yes | MIME type (e.g. `"image/png"`, `"application/pdf"`, `"application/dicom"`) |
| `content[0].attachment.data` | No | Base64-encoded file content |
| `content[0].attachment.title` | No | File title |

### ImagingStudy

| Field | FHIR Required | Behavior |
|---|---|---|
| `resourceType` | Yes | Always `"ImagingStudy"` |
| `id` | Yes | Auto-generated UUID |
| `status` | Yes | Always `"available"` |
| `subject` | Yes | Always set — reference to Patient |
| `numberOfSeries` | No | Always `1` |
| `numberOfInstances` | No | Always `1` |
| `description` | No | Conditionally included — from DICOM StudyDescription |
| `started` | No | Conditionally included — from DICOM StudyDate |
| `series[0].uid` | No | DICOM Series Instance UID |
| `series[0].modality` | No | DICOM modality code (e.g. `"CR"`, `"CT"`, `"MR"`) |
| `series[0].bodySite` | No | Conditionally included — SNOMED body site |

### DiagnosticReport

| Field | FHIR Required | Behavior |
|---|---|---|
| `resourceType` | Yes | Always `"DiagnosticReport"` |
| `id` | Yes | Auto-generated UUID |
| `status` | Yes | Always `"final"` |
| `category` | No | Always `"LAB"` / `"Laboratory"` |
| `code.coding` | Yes | LOINC code from OBR segment |
| `subject` | No | Always set — reference to Patient |
| `effectiveDateTime` | No | Conditionally included |
| `result` | No | Conditionally included — list of Observation references |
| `conclusion` | No | Conditionally included — text summary |

### Bundle (Transaction) — Final Output

| Field | Required | Behavior |
|---|---|---|
| `resourceType` | Yes | Always `"Bundle"` |
| `type` | Yes | Always `"transaction"` |
| `entry[0].resource` | Yes | Always the Patient resource |
| `entry[0].fullUrl` | Yes | `urn:uuid:<uuid>` |
| `entry[0].request.method` | Yes | Always `"POST"` |
| `entry[0].request.url` | Yes | Resource type (e.g. `"Patient"`) |
| `entry[1..n]` | Yes | All other resources (Observations, Encounters, etc.) |

All `entry[].resource.subject.reference` values point back to the Patient's `fullUrl`.

---

## Layer 3: Coding Systems

| System | URI | Used For |
|---|---|---|
| LOINC | `http://loinc.org` | Vital signs, lab tests, document types |
| SNOMED-CT | `http://snomed.info/sct` | Clinical conditions, body sites |
| ICD-10 | `http://hl7.org/fhir/sid/icd-10` | Diagnosis codes |
| UCUM | `http://unitsofmeasure.org` | Units of measurement |
| NRCES India | `https://nrces.in/ndhm/fhir/r4/StructureDefinition/Patient` | ABDM Patient profile |
| ABDM Health ID | `https://healthid.abdm.gov.in` | ABHA identifier system |
| HL7 v2-0203 | `http://terminology.hl7.org/CodeSystem/v2-0203` | Identifier types (MR) |
| HL7 v3-ActCode | `http://terminology.hl7.org/CodeSystem/v3-ActCode` | Encounter class (EMER/IMP/AMB) |
| HL7 Obs Category | `http://terminology.hl7.org/CodeSystem/observation-category` | vital-signs / laboratory |
| HL7 Condition Clinical | `http://terminology.hl7.org/CodeSystem/condition-clinical` | active / resolved |
| HL7 Condition Verification | `http://terminology.hl7.org/CodeSystem/condition-ver-status` | confirmed / provisional |
| DICOM Ontology | `http://dicom.nema.org/resources/ontology/DCM` | Imaging modality codes |

### LOINC Codes Used

| Code | Display | Used For |
|---|---|---|
| `8867-4` | Heart rate | HR from all sources |
| `2708-6` | Oxygen saturation (pulse oximetry) | SpO2 |
| `85354-9` | Blood pressure panel | BP (with components) |
| `8480-6` | Systolic blood pressure | BP systolic component |
| `8462-4` | Diastolic blood pressure | BP diastolic component |
| `8310-5` | Body temperature | Temperature |
| `9279-1` | Respiratory rate | RR |
| `29463-7` | Body weight | Weight |
| `8302-2` | Body height | Height |
| `39156-5` | Body mass index | BMI |
| `6598-7` | Troponin T | Cardiac marker lab |
| `718-7` | Hemoglobin | CBC lab |
| `6690-2` | WBC count | CBC lab |
| `2345-7` | Glucose | BMP lab |
| `2160-0` | Creatinine | Renal lab |
| `2951-2` | Sodium | Electrolyte lab |
| `2823-3` | Potassium | Electrolyte lab |
| `131328` | MDC ECG lead II | ECG waveform |

### UCUM Unit Codes

| Code | Display | Used With |
|---|---|---|
| `/min` | per minute | Heart rate, respiratory rate |
| `%` | percent | SpO2 |
| `mm[Hg]` | millimeters of mercury | Blood pressure |
| `Cel` | degrees Celsius | Body temperature |
| `kg` | kilograms | Body weight |
| `cm` | centimeters | Body height |
| `kg/m2` | kg per square meter | BMI |
| `mV` | millivolts | ECG waveform |

---

## Patient Linking Tiers

The patient linker matches identities across sources using these tiers (in priority order). A match only fires when **both** sides have the relevant field:

| Priority | Match Criteria | Example |
|---|---|---|
| 1 | Exact MRN match | `MRN-2024-001234` == `MRN-2024-001234` |
| 2 | Exact ABHA ID match | Same ABDM Health ID |
| 3 | Exact normalized name + DOB | `"kumar rajesh"` + `1975-08-15` |
| 4 | Phone or email match | Same phone digits / same lowercase email |
| — | No match | Creates a new separate patient |

---

## Source Type to FHIR Resource Mapping

| Source | Adapter | Input Format(s) | FHIR Resources Produced |
|---|---|---|---|
| Wearables | `WearableAdapter` | Apple Health XML, Google Fit JSON | `Observation` (vital-signs) |
| Ambulance (108 EMS) | `AmbulanceAdapter` | NEMSIS XML | `Encounter` + `Observation` (vital-signs) |
| Hospital EHR | `EHRAdapter` | HL7 v2 (pipe-delimited) | `Encounter` + `Observation` + `Condition` + `DiagnosticReport` |
| Handwritten Notes | `HandwrittenAdapter` | Images (PNG/JPG) | `DocumentReference` + `Condition` + `Observation` |
| Real-Time Vitals | `RealtimeVitalsAdapter` | JSON (numeric) + CSV (waveform) | `Observation` (vital-signs + SampledData) |
| Scans & Lab Reports | `ScansLabsAdapter` | DICOM + PDF | `ImagingStudy` + `DiagnosticReport` + `DocumentReference` + `Observation` |
