"""Synthea-powered dynamic patient data generator.

Downloads and runs Synthea to produce realistic, coherent FHIR patient bundles,
then extracts PatientProfile + ClinicalScenario to drive the existing 6 simulators.
Also supports loading pre-generated Synthea JSON files directly.
"""

from __future__ import annotations

import json
import os
import random
import subprocess
import tempfile
from pathlib import Path

from ingest.simulators.base_simulator import PatientProfile, ClinicalScenario


# SNOMED -> ICD-10 rough mappings for the scenarios we care about
_SNOMED_TO_ICD10 = {
    "22298006": ("I21.9", "Acute myocardial infarction, unspecified"),
    "53741008": ("I25.10", "Coronary artery disease"),
    "38341003": ("I10", "Essential hypertension"),
    "44054006": ("E11.9", "Type 2 diabetes mellitus"),
    "195967001": ("J45.9", "Asthma, unspecified"),
    "13645005": ("J44.1", "COPD with acute exacerbation"),
    "233604007": ("J18.9", "Pneumonia, unspecified"),
    "36971009": ("J00", "Acute nasopharyngitis"),
    "40055000": ("J06.9", "Upper respiratory infection"),
    "10509002": ("S06.0X0A", "Concussion"),
    "55822004": ("I48.91", "Atrial fibrillation"),
    "230690007": ("I63.9", "Cerebral infarction"),
    "73211009": ("E11.65", "Diabetes with hyperglycemia"),
    "431855005": ("J96.00", "Acute respiratory failure"),
    "698754002": ("F41.1", "Generalized anxiety disorder"),
    "370143000": ("F32.9", "Major depressive disorder"),
    "59621000": ("I10", "Essential hypertension"),
    "15777000": ("E78.5", "Hyperlipidemia"),
    "267036007": ("R07.9", "Chest pain, unspecified"),
    "185086009": ("Z00.00", "General examination"),
    "162673000": ("Z00.00", "General examination of patient"),
    "410429000": ("Z87.39", "Cardiac arrest"),
}

# Common lab LOINC codes with typical value ranges
_LAB_TEMPLATES = {
    "6598-7": {"name": "Troponin T", "unit": "ng/mL", "ref_low": 0.0, "ref_high": 0.04},
    "718-7": {"name": "Hemoglobin", "unit": "g/dL", "ref_low": 12.0, "ref_high": 16.0},
    "6690-2": {"name": "WBC", "unit": "10*3/uL", "ref_low": 4.5, "ref_high": 11.0},
    "2345-7": {"name": "Glucose", "unit": "mg/dL", "ref_low": 70, "ref_high": 100},
    "2160-0": {"name": "Creatinine", "unit": "mg/dL", "ref_low": 0.7, "ref_high": 1.3},
    "2951-2": {"name": "Sodium", "unit": "mmol/L", "ref_low": 136, "ref_high": 145},
    "2823-3": {"name": "Potassium", "unit": "mmol/L", "ref_low": 3.5, "ref_high": 5.0},
    "2093-3": {"name": "Total Cholesterol", "unit": "mg/dL", "ref_low": 0, "ref_high": 200},
    "2085-9": {"name": "HDL Cholesterol", "unit": "mg/dL", "ref_low": 40, "ref_high": 60},
    "13457-7": {"name": "LDL Cholesterol", "unit": "mg/dL", "ref_low": 0, "ref_high": 100},
    "2571-8": {"name": "Triglycerides", "unit": "mg/dL", "ref_low": 0, "ref_high": 150},
    "4548-4": {"name": "HbA1c", "unit": "%", "ref_low": 4.0, "ref_high": 5.6},
    "33914-3": {"name": "eGFR", "unit": "mL/min/1.73m2", "ref_low": 60, "ref_high": 120},
    "777-3": {"name": "Platelet Count", "unit": "10*3/uL", "ref_low": 150, "ref_high": 400},
}

# Vital sign ranges by condition category
_VITAL_PRESETS = {
    "cardiac": {
        "baseline_hr": (90, 120), "baseline_bp_sys": (140, 180),
        "baseline_bp_dia": (85, 100), "baseline_spo2": (91, 96),
        "baseline_temp": (36.5, 37.5), "baseline_rr": (18, 26),
    },
    "respiratory": {
        "baseline_hr": (100, 120), "baseline_bp_sys": (120, 145),
        "baseline_bp_dia": (75, 90), "baseline_spo2": (85, 93),
        "baseline_temp": (36.8, 38.5), "baseline_rr": (24, 35),
    },
    "metabolic": {
        "baseline_hr": (95, 120), "baseline_bp_sys": (90, 130),
        "baseline_bp_dia": (55, 80), "baseline_spo2": (95, 99),
        "baseline_temp": (36.5, 38.0), "baseline_rr": (20, 30),
    },
    "trauma": {
        "baseline_hr": (110, 130), "baseline_bp_sys": (80, 110),
        "baseline_bp_dia": (50, 70), "baseline_spo2": (90, 96),
        "baseline_temp": (35.5, 37.0), "baseline_rr": (22, 30),
    },
    "general": {
        "baseline_hr": (70, 90), "baseline_bp_sys": (110, 135),
        "baseline_bp_dia": (65, 85), "baseline_spo2": (96, 99),
        "baseline_temp": (36.4, 37.2), "baseline_rr": (14, 20),
    },
}

# Map condition keywords to vital preset categories
_CONDITION_CATEGORY_MAP = {
    "myocardial": "cardiac", "coronary": "cardiac", "heart": "cardiac",
    "atrial": "cardiac", "cardiac": "cardiac", "angina": "cardiac",
    "chest pain": "cardiac",
    "asthma": "respiratory", "copd": "respiratory", "pneumonia": "respiratory",
    "respiratory": "respiratory", "bronchitis": "respiratory", "lung": "respiratory",
    "diabetes": "metabolic", "hyperglycemia": "metabolic", "ketoacidosis": "metabolic",
    "metabolic": "metabolic", "thyroid": "metabolic",
    "fracture": "trauma", "concussion": "trauma", "injury": "trauma",
    "trauma": "trauma", "laceration": "trauma",
}


def _classify_conditions(conditions: list[dict]) -> str:
    """Classify conditions into a vital preset category using priority ordering.

    Scans ALL conditions and returns the highest-acuity match.
    Priority: cardiac > respiratory > trauma > metabolic > general
    """
    _CATEGORY_PRIORITY = ["cardiac", "respiratory", "trauma", "metabolic"]
    found = set()
    for cond in conditions:
        display = cond.get("display", "").lower()
        for keyword, category in _CONDITION_CATEGORY_MAP.items():
            if keyword in display:
                found.add(category)
    for cat in _CATEGORY_PRIORITY:
        if cat in found:
            return cat
    return "general"


def _detect_comorbidities(conditions: list[dict]) -> set[str]:
    """Detect clinically significant comorbidities from ALL conditions."""
    flags = set()
    for cond in conditions:
        display = cond.get("display", "").lower()
        if any(w in display for w in ("hypertension", "hypertensive")):
            flags.add("hypertension")
        if any(w in display for w in ("diabetes", "hyperglycemia", "prediabetes")):
            flags.add("diabetes")
        if any(w in display for w in ("heart failure", "ischemic heart", "coronary", "myocardial", "atrial")):
            flags.add("cardiac")
        if any(w in display for w in ("asthma", "copd", "emphysema", "bronchitis", "lung cancer", "respiratory")):
            flags.add("respiratory")
        if any(w in display for w in ("kidney disease", "renal failure", "renal disease")):
            flags.add("ckd")
        if any(w in display for w in ("anemia",)):
            flags.add("anemia")
    return flags


def _rand_in_range(low: float, high: float) -> float:
    return round(random.uniform(low, high), 1)


class SyntheaGenerator:
    """Generate dynamic patient data using Synthea FHIR bundles."""

    def __init__(self, synthea_jar_path: str | None = None):
        self._synthea_jar = synthea_jar_path

    @staticmethod
    def _java_works(path: str) -> bool:
        """Check if a Java binary actually runs."""
        try:
            r = subprocess.run(
                [path, "-version"], capture_output=True, text=True, timeout=10,
            )
            return r.returncode == 0 and "version" in (r.stderr + r.stdout).lower()
        except Exception:
            return False

    @classmethod
    def _find_java(cls) -> str:
        """Find a working Java executable (11+)."""
        candidates: list[str] = []

        # 1. Brew openjdk paths (macOS) - most reliable
        for version in ("@17", "@21", "@11", ""):
            for prefix in ("/opt/homebrew/opt", "/usr/local/opt"):
                p = f"{prefix}/openjdk{version}/bin/java"
                if Path(p).exists():
                    candidates.append(p)

        # 2. JAVA_HOME
        java_home = os.environ.get("JAVA_HOME")
        if java_home:
            p = str(Path(java_home) / "bin" / "java")
            if Path(p).exists():
                candidates.append(p)

        # 3. System java
        import shutil
        java = shutil.which("java")
        if java:
            candidates.append(java)

        # Return first one that actually works
        for candidate in candidates:
            if cls._java_works(candidate):
                return candidate

        raise FileNotFoundError(
            "Java 11+ not found. Install via: brew install openjdk@17"
        )

    def generate_with_synthea(
        self,
        population: int = 5,
        state: str = "Massachusetts",
        city: str | None = None,
        seed: int | None = None,
        output_dir: str | None = None,
    ) -> list[Path]:
        """Run Synthea JAR to generate FHIR bundles.

        Requires Java 11+ and the Synthea JAR on disk.
        Returns list of generated FHIR JSON file paths.
        """
        if not self._synthea_jar or not Path(self._synthea_jar).exists():
            raise FileNotFoundError(
                f"Synthea JAR not found at '{self._synthea_jar}'. "
                "Download from https://github.com/synthetichealth/synthea/releases "
                "or use load_from_files() with pre-generated Synthea JSON."
            )

        java_bin = self._find_java()
        out_dir = Path(output_dir or tempfile.mkdtemp(prefix="synthea_"))
        out_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            java_bin, "-jar", str(self._synthea_jar),
            "-p", str(population),
            "-s", str(seed or random.randint(1, 999999)),
            "--exporter.fhir.export=true",
            "--exporter.fhir.transaction_bundle=true",
            "--exporter.hospital.fhir.export=false",
            "--exporter.practitioner.fhir.export=false",
            "--exporter.baseDirectory=" + str(out_dir),
            state,
        ]
        if city:
            cmd.append(city)

        print(f"  Running: {' '.join(cmd[:4])} ... -p {population} {state}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            # Synthea prints progress to stderr, actual errors are rare
            stderr = result.stderr or ""
            if "Exception" in stderr and "NullPointerException" not in stderr:
                raise RuntimeError(f"Synthea failed: {stderr[:500]}")

        # Synthea outputs to <baseDirectory>/fhir/
        fhir_dir = out_dir / "fhir"
        if not fhir_dir.exists():
            # Some versions use output/fhir
            fhir_dir = out_dir / "output" / "fhir"

        if not fhir_dir.exists():
            raise FileNotFoundError(
                f"Synthea did not produce FHIR output. "
                f"Checked: {out_dir}/fhir and {out_dir}/output/fhir\n"
                f"Stderr: {(result.stderr or '')[:300]}"
            )

        # Filter out hospital/practitioner info files
        patient_files = [
            f for f in sorted(fhir_dir.glob("*.json"))
            if not f.name.startswith("hospitalInformation")
            and not f.name.startswith("practitionerInformation")
        ]
        return patient_files

    def load_from_files(self, *paths: str | Path) -> list[dict]:
        """Load pre-generated Synthea FHIR bundle JSON files."""
        bundles = []
        for p in paths:
            path = Path(p)
            if path.is_dir():
                for f in sorted(path.glob("*.json")):
                    with open(f) as fh:
                        bundles.append(json.load(fh))
            elif path.is_file():
                with open(path) as fh:
                    bundles.append(json.load(fh))
        return bundles

    def load_from_directory(self, directory: str | Path) -> list[dict]:
        """Load all Synthea FHIR JSON files from a directory."""
        return self.load_from_files(directory)

    def extract_profiles(self, bundles: list[dict]) -> list[tuple[PatientProfile, ClinicalScenario]]:
        """Extract PatientProfile and ClinicalScenario from Synthea bundles.

        This bridges Synthea output to the existing simulator framework,
        allowing all 6 simulators to generate coherent data for each patient.
        """
        results = []
        for bundle in bundles:
            entries = bundle.get("entry", [])
            profile, scenario = self._extract_single(entries)
            if profile:
                results.append((profile, scenario))
        return results

    def _extract_single(
        self, entries: list[dict]
    ) -> tuple[PatientProfile | None, ClinicalScenario]:
        """Extract profile + scenario from a single bundle's entries."""
        patient_resource = None
        conditions = []
        observations = []
        medications = []
        encounters = []

        for entry in entries:
            resource = entry.get("resource", {})
            rt = resource.get("resourceType")

            if rt == "Patient":
                patient_resource = resource
            elif rt == "Condition":
                conditions.append(resource)
            elif rt == "Observation":
                observations.append(resource)
            elif rt == "MedicationRequest":
                medications.append(resource)
            elif rt == "Encounter":
                encounters.append(resource)

        if not patient_resource:
            return None, ClinicalScenario()

        # Extract patient demographics
        profile = self._extract_patient_profile(patient_resource)

        # Build clinical scenario from conditions, observations, medications
        scenario = self._build_scenario(conditions, observations, medications, encounters)

        return profile, scenario

    def _extract_patient_profile(self, patient: dict) -> PatientProfile:
        """Extract PatientProfile from a Synthea Patient resource."""
        names = patient.get("name", [])
        given_name = ""
        family_name = ""
        full_name = ""
        for n in names:
            if n.get("use") == "official" or not given_name:
                given_parts = n.get("given", [])
                given_name = given_parts[0] if given_parts else ""
                family_name = n.get("family", "")
                full_name = f"{given_name} {family_name}".strip()

        gender = patient.get("gender", "unknown")
        birth_date = patient.get("birthDate", "1980-01-01")

        # Extract address
        addresses = patient.get("address", [])
        address = ""
        if addresses:
            addr = addresses[0]
            parts = []
            for line in addr.get("line", []):
                parts.append(line)
            if addr.get("city"):
                parts.append(addr["city"])
            if addr.get("state"):
                parts.append(addr["state"])
            address = ", ".join(parts)

        # Extract phone
        phone = ""
        for telecom in patient.get("telecom", []):
            if telecom.get("system") == "phone":
                phone = telecom.get("value", "")
                break

        # Extract MRN
        mrn = ""
        for ident in patient.get("identifier", []):
            id_type = ident.get("type", {})
            codings = id_type.get("coding", [])
            for c in codings:
                if c.get("code") == "MR":
                    mrn = ident.get("value", "")
                    break
            if mrn:
                break

        # Generate ABHA ID from patient UUID
        patient_id = patient.get("id", "")
        abha_digits = "".join(c for c in patient_id if c.isdigit() or c.isalpha())[:14]
        # Create a deterministic ABHA-like ID
        abha_num = hash(patient_id) % 10**14
        abha_str = f"{abha_num:014d}"
        abha_id = f"ABHA-{abha_str[:2]}-{abha_str[2:6]}-{abha_str[6:10]}-{abha_str[10:14]}"

        return PatientProfile(
            name=full_name,
            given_name=given_name,
            family_name=family_name,
            dob=birth_date,
            gender=gender,
            mrn=mrn or f"MRN-{patient_id[:8]}",
            abha_id=abha_id,
            phone=phone or f"+91{random.randint(7000000000, 9999999999)}",
            address=address or "General Hospital, New Delhi",
        )

    def _build_scenario(
        self,
        conditions: list[dict],
        observations: list[dict],
        medications: list[dict],
        encounters: list[dict],
    ) -> ClinicalScenario:
        """Build a ClinicalScenario from Synthea clinical data."""
        # Build raw condition display list from ALL conditions (for classification)
        raw_conditions = []
        for cond in conditions:
            code_obj = cond.get("code", {})
            codings = code_obj.get("coding", [])
            if codings:
                raw_conditions.append({"display": codings[0].get("display", ""), "code": codings[0].get("code", "")})

        # Extract diagnoses (mapped to ICD-10)
        diagnoses = []
        for cond in conditions:
            code_obj = cond.get("code", {})
            codings = code_obj.get("coding", [])
            for coding in codings:
                code = coding.get("code", "")
                display = coding.get("display", "")
                system = coding.get("system", "")
                if "snomed" in system.lower() and code in _SNOMED_TO_ICD10:
                    icd_code, icd_display = _SNOMED_TO_ICD10[code]
                    diagnoses.append({"code": icd_code, "display": icd_display})
                elif code:
                    diagnoses.append({"code": code, "display": display})
                break  # Take first coding only

        if not diagnoses:
            diagnoses = [{"code": "Z00.00", "display": "General adult medical examination"}]

        # Classify using ALL raw conditions, not just mapped diagnoses
        category = _classify_conditions(raw_conditions)
        comorbidities = _detect_comorbidities(raw_conditions)

        # Determine chief complaint from most recent encounter or first condition
        chief_complaint = ""
        if encounters:
            for enc in sorted(encounters, key=lambda e: e.get("period", {}).get("start", ""), reverse=True):
                reason = enc.get("reasonCode", [])
                if reason:
                    codings = reason[0].get("coding", [])
                    if codings:
                        chief_complaint = codings[0].get("display", "")
                        break
                enc_type = enc.get("type", [])
                if enc_type:
                    codings = enc_type[0].get("coding", [])
                    if codings:
                        chief_complaint = codings[0].get("display", "")
                        break

        if not chief_complaint and diagnoses:
            chief_complaint = diagnoses[0]["display"]

        # Extract lab values from observations — prefer most recent value per code
        lab_best: dict[str, dict] = {}  # loinc_code -> {value, datetime}
        for obs in observations:
            code_obj = obs.get("code", {})
            codings = code_obj.get("coding", [])
            obs_datetime = obs.get("effectiveDateTime", obs.get("issued", ""))
            for coding in codings:
                loinc_code = coding.get("code", "")
                if loinc_code in _LAB_TEMPLATES:
                    vq = obs.get("valueQuantity", {})
                    value = vq.get("value") if vq else None
                    if value is not None:
                        existing = lab_best.get(loinc_code)
                        if existing is None or obs_datetime > existing["datetime"]:
                            lab_best[loinc_code] = {"value": value, "datetime": obs_datetime}
                break

        labs = []
        for loinc_code, entry in lab_best.items():
            template = _LAB_TEMPLATES[loinc_code]
            labs.append({
                "name": template["name"],
                "code": loinc_code,
                "value": round(float(entry["value"]), 2),
                "unit": template["unit"],
                "ref_low": template["ref_low"],
                "ref_high": template["ref_high"],
            })

        # If no labs from observations, generate scenario-appropriate labs
        if not labs:
            labs = self._generate_default_labs(diagnoses, comorbidities)
        else:
            # Ensure disease-critical labs are present and coherent
            labs = self._ensure_coherent_labs(labs, comorbidities)

        # Extract medication names
        med_names = []
        for med in medications:
            med_code = med.get("medicationCodeableConcept", {})
            codings = med_code.get("coding", [])
            if codings:
                med_names.append(codings[0].get("display", "Unknown medication"))

        if not med_names:
            med_names = ["As prescribed by physician"]

        # Generate base vitals from category preset
        presets = _VITAL_PRESETS[category]
        bp_sys = _rand_in_range(*presets["baseline_bp_sys"])
        bp_dia = _rand_in_range(*presets["baseline_bp_dia"])
        hr = _rand_in_range(*presets["baseline_hr"])
        spo2 = _rand_in_range(*presets["baseline_spo2"])
        temp = _rand_in_range(*presets["baseline_temp"])
        rr = _rand_in_range(*presets["baseline_rr"])

        # Apply comorbidity adjustments to vitals
        if "hypertension" in comorbidities:
            bp_sys = max(bp_sys, _rand_in_range(140, 175))
            bp_dia = max(bp_dia, _rand_in_range(88, 100))
        if "cardiac" in comorbidities and category != "cardiac":
            hr = max(hr, _rand_in_range(92, 115))
        if "respiratory" in comorbidities and category != "respiratory":
            spo2 = min(spo2, _rand_in_range(88, 94))
            rr = max(rr, _rand_in_range(22, 28))

        vital_trend = random.choice(["improving", "stable"])
        scenario_name = f"synthea_{category}_{random.randint(1000, 9999)}"

        # Prioritize disease-critical labs when truncating to 7
        if len(labs) > 7:
            critical_codes = set()
            if "diabetes" in comorbidities:
                critical_codes |= {"2345-7", "4548-4"}
            if "cardiac" in comorbidities:
                critical_codes.add("6598-7")
            if "ckd" in comorbidities:
                critical_codes |= {"2160-0", "33914-3"}
            if "anemia" in comorbidities:
                critical_codes.add("718-7")
            critical = [l for l in labs if l["code"] in critical_codes]
            rest = [l for l in labs if l["code"] not in critical_codes]
            labs = (critical + rest)[:7]

        return ClinicalScenario(
            name=scenario_name,
            chief_complaint=chief_complaint,
            diagnoses=diagnoses[:5],
            baseline_hr=hr,
            baseline_bp_sys=bp_sys,
            baseline_bp_dia=bp_dia,
            baseline_spo2=spo2,
            baseline_temp=temp,
            baseline_rr=rr,
            vital_trend=vital_trend,
            labs=labs,
            medications=med_names[:5],
        )

    def _generate_default_labs(self, diagnoses: list[dict], comorbidities: set[str] | None = None) -> list[dict]:
        """Generate default lab values based on diagnosis category and comorbidities."""
        category = _classify_conditions(diagnoses)
        comorbidities = comorbidities or set()

        base_labs = [
            {"name": "Hemoglobin", "code": "718-7", "unit": "g/dL",
             "ref_low": 12.0, "ref_high": 16.0},
            {"name": "WBC", "code": "6690-2", "unit": "10*3/uL",
             "ref_low": 4.5, "ref_high": 11.0},
            {"name": "Creatinine", "code": "2160-0", "unit": "mg/dL",
             "ref_low": 0.7, "ref_high": 1.3},
            {"name": "Sodium", "code": "2951-2", "unit": "mmol/L",
             "ref_low": 136, "ref_high": 145},
            {"name": "Potassium", "code": "2823-3", "unit": "mmol/L",
             "ref_low": 3.5, "ref_high": 5.0},
        ]

        # Add category-specific labs
        if category == "cardiac" or "cardiac" in comorbidities:
            base_labs.insert(0, {"name": "Troponin T", "code": "6598-7",
                                 "unit": "ng/mL", "ref_low": 0.0, "ref_high": 0.04})
        if category == "metabolic" or "diabetes" in comorbidities:
            base_labs.insert(0, {"name": "Glucose", "code": "2345-7",
                                 "unit": "mg/dL", "ref_low": 70, "ref_high": 100})
            base_labs.append({"name": "HbA1c", "code": "4548-4",
                              "unit": "%", "ref_low": 4.0, "ref_high": 5.6})

        # Generate values — disease-aware
        for lab in base_labs:
            lab["value"] = round(random.uniform(lab["ref_low"], lab["ref_high"]), 2)

        # Apply comorbidity-specific abnormal values
        self._apply_comorbidity_lab_adjustments(base_labs, comorbidities)

        return base_labs

    def _ensure_coherent_labs(self, labs: list[dict], comorbidities: set[str]) -> list[dict]:
        """Ensure Synthea-extracted labs are coherent with comorbidities.

        Adds missing disease-critical labs and adjusts values that contradict
        known diagnoses.
        """
        lab_codes = {lab["code"] for lab in labs}

        # Diabetes: ensure glucose + HbA1c are present and elevated
        if "diabetes" in comorbidities:
            if "2345-7" not in lab_codes:
                labs.append({
                    "name": "Glucose", "code": "2345-7", "unit": "mg/dL",
                    "value": round(random.uniform(126, 250), 2),
                    "ref_low": 70, "ref_high": 100,
                })
            if "4548-4" not in lab_codes:
                labs.append({
                    "name": "HbA1c", "code": "4548-4", "unit": "%",
                    "value": round(random.uniform(6.5, 10.5), 2),
                    "ref_low": 4.0, "ref_high": 5.6,
                })

        # Cardiac: ensure troponin is present
        if "cardiac" in comorbidities:
            if "6598-7" not in lab_codes:
                labs.append({
                    "name": "Troponin T", "code": "6598-7", "unit": "ng/mL",
                    "value": round(random.uniform(0.04, 0.8), 3),
                    "ref_low": 0.0, "ref_high": 0.04,
                })

        # CKD: ensure creatinine is elevated, eGFR is low
        if "ckd" in comorbidities:
            if "2160-0" not in lab_codes:
                labs.append({
                    "name": "Creatinine", "code": "2160-0", "unit": "mg/dL",
                    "value": round(random.uniform(1.5, 4.0), 2),
                    "ref_low": 0.7, "ref_high": 1.3,
                })
            if "33914-3" not in lab_codes:
                labs.append({
                    "name": "eGFR", "code": "33914-3", "unit": "mL/min/1.73m2",
                    "value": round(random.uniform(15, 55), 1),
                    "ref_low": 60, "ref_high": 120,
                })

        # Anemia: ensure hemoglobin is low
        if "anemia" in comorbidities:
            if "718-7" not in lab_codes:
                labs.append({
                    "name": "Hemoglobin", "code": "718-7", "unit": "g/dL",
                    "value": round(random.uniform(7.0, 11.0), 1),
                    "ref_low": 12.0, "ref_high": 16.0,
                })

        # Now adjust existing lab values that contradict comorbidities
        self._apply_comorbidity_lab_adjustments(labs, comorbidities)

        return labs

    @staticmethod
    def _apply_comorbidity_lab_adjustments(labs: list[dict], comorbidities: set[str]) -> None:
        """Adjust lab values in-place to be coherent with comorbidities."""
        for lab in labs:
            code = lab["code"]

            # Diabetes: glucose must be elevated (>=126), HbA1c must be elevated (>=6.5)
            if "diabetes" in comorbidities:
                if code == "2345-7" and lab["value"] < 126:
                    lab["value"] = round(random.uniform(126, 250), 2)
                if code == "4548-4" and lab["value"] < 6.5:
                    lab["value"] = round(random.uniform(6.5, 10.5), 2)

            # Cardiac: troponin should be elevated
            if "cardiac" in comorbidities:
                if code == "6598-7" and lab["value"] < 0.04:
                    lab["value"] = round(random.uniform(0.04, 0.8), 3)

            # CKD: creatinine elevated, eGFR depressed
            if "ckd" in comorbidities:
                if code == "2160-0" and lab["value"] < 1.5:
                    lab["value"] = round(random.uniform(1.5, 4.0), 2)
                if code == "33914-3" and lab["value"] > 55:
                    lab["value"] = round(random.uniform(15, 55), 1)

            # Anemia: hemoglobin must be low
            if "anemia" in comorbidities:
                if code == "718-7" and lab["value"] > 11.5:
                    lab["value"] = round(random.uniform(7.0, 11.0), 1)
