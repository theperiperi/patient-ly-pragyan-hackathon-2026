"""Scans & lab reports adapter - parses DICOM metadata and PDF lab reports into FHIR."""

from __future__ import annotations

import base64
import os
import re
from typing import Any

from ingest.core.base_adapter import BaseAdapter, PatientIdentity, AdapterResult
from ingest.core.fhir_helpers import (
    make_patient, make_imaging_study, make_document_reference,
    make_diagnostic_report, make_observation_lab,
)
from ingest import config as cfg


class ScansLabsAdapter(BaseAdapter):

    @property
    def source_type(self) -> str:
        return "scans_labs"

    def supports(self, input_data: Any) -> bool:
        if not isinstance(input_data, str) or not os.path.isfile(input_data):
            return False
        lower = input_data.lower()
        if lower.endswith(".dcm"):
            return True
        if lower.endswith(".pdf"):
            try:
                with open(input_data, "rb") as f:
                    header = f.read(5)
                return header == b"%PDF-"
            except Exception:
                return False
        return False

    def parse(self, input_data: Any) -> AdapterResult:
        if input_data.lower().endswith(".dcm"):
            return self._parse_dicom(input_data)
        return self._parse_pdf_lab(input_data)

    def _parse_dicom(self, filepath: str) -> AdapterResult:
        try:
            import pydicom
        except ImportError:
            raise ImportError("pydicom package required. Install: pip install pydicom")

        ds = pydicom.dcmread(filepath, force=True)

        # Extract patient identity from DICOM tags
        patient_name = str(ds.PatientName) if hasattr(ds, "PatientName") and ds.PatientName else None
        # DICOM names are "Family^Given" format
        given, family = None, None
        if patient_name and "^" in patient_name:
            parts = patient_name.split("^")
            family = parts[0] if parts[0] else None
            given = parts[1] if len(parts) > 1 and parts[1] else None
            patient_name = f"{given} {family}" if given and family else (given or family)

        dob = None
        if hasattr(ds, "PatientBirthDate") and ds.PatientBirthDate:
            raw_dob = str(ds.PatientBirthDate)
            if len(raw_dob) >= 8:
                dob = f"{raw_dob[:4]}-{raw_dob[4:6]}-{raw_dob[6:8]}"

        gender_raw = str(ds.PatientSex).upper() if hasattr(ds, "PatientSex") and ds.PatientSex else None
        gender = {"M": "male", "F": "female", "O": "other"}.get(gender_raw) if gender_raw else None

        mrn = str(ds.PatientID) if hasattr(ds, "PatientID") and ds.PatientID else None

        identity = PatientIdentity(
            source_id=mrn or "dicom-unknown",
            source_system=self.source_type,
            full_name=patient_name,
            given_name=given,
            family_name=family,
            birth_date=dob,
            gender=gender,
            mrn=mrn if mrn and mrn.startswith("MRN") else None,
        )

        patient = make_patient(identity)
        patient_ref = f"Patient/{patient.id}"
        resources = []

        # ImagingStudy
        modality = str(ds.Modality) if hasattr(ds, "Modality") else "OT"
        study_uid = str(ds.StudyInstanceUID) if hasattr(ds, "StudyInstanceUID") else "1.2.3.4"
        series_uid = str(ds.SeriesInstanceUID) if hasattr(ds, "SeriesInstanceUID") else "1.2.3.4.1"
        study_desc = str(ds.StudyDescription) if hasattr(ds, "StudyDescription") and ds.StudyDescription else None
        body_part = str(ds.BodyPartExamined) if hasattr(ds, "BodyPartExamined") and ds.BodyPartExamined else None

        study_date = None
        if hasattr(ds, "StudyDate") and ds.StudyDate:
            raw = str(ds.StudyDate)
            if len(raw) >= 8:
                study_date = f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}T00:00:00Z"

        imaging = make_imaging_study(
            patient_ref, modality, study_uid, series_uid,
            study_description=study_desc,
            body_part=body_part,
            started=study_date,
        )
        resources.append(imaging)

        # DocumentReference for the DICOM file itself
        with open(filepath, "rb") as f:
            dicom_b64 = base64.b64encode(f.read()).decode("utf-8")
        doc = make_document_reference(
            patient_ref, "application/dicom", dicom_b64,
            f"DICOM {modality} - {study_desc or 'imaging study'}",
            doc_type_code="18748-4",
            doc_type_display="Diagnostic imaging study",
        )
        resources.append(doc)

        return AdapterResult(
            patient_identity=identity, fhir_resources=resources,
            fhir_patient=patient, source_type=self.source_type,
        )

    def _parse_pdf_lab(self, filepath: str) -> AdapterResult:
        try:
            import pdfplumber
        except ImportError:
            raise ImportError("pdfplumber package required. Install: pip install pdfplumber")

        with pdfplumber.open(filepath) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)

        identity = self._extract_patient_from_text(text)
        patient = make_patient(identity)
        patient_ref = f"Patient/{patient.id}"
        resources = []

        # DocumentReference for the original PDF
        with open(filepath, "rb") as f:
            pdf_b64 = base64.b64encode(f.read()).decode("utf-8")
        doc = make_document_reference(
            patient_ref, "application/pdf", pdf_b64,
            "Laboratory report",
            doc_type_code="11502-2",
            doc_type_display="Laboratory report",
            title=os.path.basename(filepath),
        )
        resources.append(doc)

        # Parse lab results from text
        lab_results = self._extract_lab_results(text)
        obs_refs = []
        for lab in lab_results:
            obs = make_observation_lab(
                patient_ref,
                (lab["code"], lab["name"]),
                lab["value"],
                lab["unit"],
                lab["unit"],
                "2026-02-14T12:00:00Z",
                reference_range_low=lab.get("ref_low"),
                reference_range_high=lab.get("ref_high"),
            )
            resources.append(obs)
            obs_refs.append(f"Observation/{obs.id}")

        # DiagnosticReport grouping the observations
        if obs_refs:
            report = make_diagnostic_report(
                patient_ref, "LAB", "Laboratory",
                ("11502-2", "Laboratory report"),
                result_refs=obs_refs,
            )
            resources.append(report)

        return AdapterResult(
            patient_identity=identity, fhir_resources=resources,
            fhir_patient=patient, source_type=self.source_type,
        )

    def _extract_patient_from_text(self, text: str) -> PatientIdentity:
        """Try to extract patient info from lab report text."""
        name = None
        dob = None
        gender = None
        mrn = None

        # Patient: Rajesh Kumar or Name: Rajesh Kumar
        name_match = re.search(r"(?:Patient|Name)\s*:\s*(.+?)(?:\n|,|DOB|Age)", text, re.IGNORECASE)
        if name_match:
            name = name_match.group(1).strip()

        # DOB: 15-Aug-1975 or DOB: 1975-08-15
        dob_match = re.search(r"DOB\s*:\s*(\S+)", text, re.IGNORECASE)
        if dob_match:
            raw = dob_match.group(1).strip().rstrip(",")
            # Try to normalize common date formats
            dob = self._normalize_date(raw)

        # Gender/Sex
        gender_match = re.search(r"(?:Gender|Sex)\s*:\s*(\w+)", text, re.IGNORECASE)
        if gender_match:
            g = gender_match.group(1).strip().lower()
            gender = {"m": "male", "f": "female", "male": "male", "female": "female"}.get(g, g)

        # MRN
        mrn_match = re.search(r"MRN\s*:\s*([\w-]+)", text, re.IGNORECASE)
        if mrn_match:
            mrn = mrn_match.group(1).strip()

        given, family = None, None
        if name:
            parts = name.split()
            if len(parts) >= 2:
                given, family = parts[0], parts[-1]

        return PatientIdentity(
            source_id=mrn or f"lab_{name or 'unknown'}",
            source_system=self.source_type,
            full_name=name,
            given_name=given,
            family_name=family,
            birth_date=dob,
            gender=gender,
            mrn=mrn,
        )

    def _extract_lab_results(self, text: str) -> list[dict]:
        """Extract lab results from PDF text. Expects table-like rows."""
        results = []
        # Pattern: Test Name    Value    Unit    Reference Range
        # e.g. "Hemoglobin    12.5    g/dL    12.0-16.0"
        pattern = re.compile(
            r"^(.+?)\s{2,}([\d.]+)\s+([\w/%]+)\s+([\d.]+)\s*[-–]\s*([\d.]+)",
            re.MULTILINE,
        )
        for m in pattern.finditer(text):
            name = m.group(1).strip()
            try:
                value = float(m.group(2))
                unit = m.group(3).strip()
                ref_low = float(m.group(4))
                ref_high = float(m.group(5))
            except ValueError:
                continue

            # Map common lab test names to LOINC codes
            code = self._lab_name_to_loinc(name)
            results.append({
                "name": name,
                "code": code,
                "value": value,
                "unit": unit,
                "ref_low": ref_low,
                "ref_high": ref_high,
            })

        return results

    @staticmethod
    def _lab_name_to_loinc(name: str) -> str:
        """Map common lab test names to LOINC codes."""
        mapping = {
            "hemoglobin": "718-7",
            "hematocrit": "4544-3",
            "wbc": "6690-2",
            "white blood cell": "6690-2",
            "rbc": "789-8",
            "red blood cell": "789-8",
            "platelet": "777-3",
            "glucose": "2345-7",
            "creatinine": "2160-0",
            "bun": "3094-0",
            "blood urea nitrogen": "3094-0",
            "sodium": "2951-2",
            "potassium": "2823-3",
            "chloride": "2075-0",
            "calcium": "17861-6",
            "troponin": "6598-7",
            "troponin i": "10839-9",
            "troponin t": "6598-7",
            "alt": "1742-6",
            "ast": "1920-8",
            "total bilirubin": "1975-2",
            "albumin": "1751-7",
            "total protein": "2885-2",
            "cholesterol": "2093-3",
            "triglycerides": "2571-8",
            "hdl": "2085-9",
            "ldl": "2089-1",
            "hba1c": "4548-4",
            "tsh": "3016-3",
        }
        lower = name.lower().strip()
        return mapping.get(lower, lower)

    @staticmethod
    def _normalize_date(raw: str) -> str:
        """Attempt to normalize a date string to YYYY-MM-DD."""
        import re as _re
        # Already ISO
        if _re.match(r"\d{4}-\d{2}-\d{2}", raw):
            return raw[:10]
        # DD-Mon-YYYY
        months = {
            "jan": "01", "feb": "02", "mar": "03", "apr": "04",
            "may": "05", "jun": "06", "jul": "07", "aug": "08",
            "sep": "09", "oct": "10", "nov": "11", "dec": "12",
        }
        m = _re.match(r"(\d{1,2})-(\w{3})-(\d{4})", raw, _re.IGNORECASE)
        if m:
            day = m.group(1).zfill(2)
            mon = months.get(m.group(2).lower(), "01")
            year = m.group(3)
            return f"{year}-{mon}-{day}"
        return raw
