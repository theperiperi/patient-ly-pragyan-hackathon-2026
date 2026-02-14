"""Scans & Labs simulator - generates DICOM file + PDF lab report."""

from __future__ import annotations

from pathlib import Path

from patiently.simulators.base_simulator import BaseSimulator, PatientProfile, ClinicalScenario


class ScansLabsSimulator(BaseSimulator):

    def generate(self, profile: PatientProfile, scenario: ClinicalScenario, output_dir: Path) -> Path:
        scans_dir = output_dir / "scans_labs"
        scans_dir.mkdir(parents=True, exist_ok=True)
        self._generate_dicom(profile, scenario, scans_dir)
        self._generate_pdf(profile, scenario, scans_dir)
        return scans_dir

    def _generate_dicom(self, profile, scenario, out_dir):
        import pydicom
        from pydicom.dataset import FileDataset
        from pydicom.uid import generate_uid, ExplicitVRLittleEndian
        import numpy as np

        filename = out_dir / "sim_chest_xray.dcm"
        file_meta = pydicom.dataset.FileMetaDataset()
        file_meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.1"
        file_meta.MediaStorageSOPInstanceUID = generate_uid()
        file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

        ds = FileDataset(str(filename), {}, file_meta=file_meta, preamble=b"\x00" * 128)
        ds.SOPClassUID = file_meta.MediaStorageSOPClassUID
        ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
        ds.PatientName = f"{profile.family_name}^{profile.given_name}"
        ds.PatientID = profile.mrn
        ds.PatientBirthDate = profile.dob.replace("-", "")
        ds.PatientSex = "M" if profile.gender == "male" else "F"
        ds.Modality = "CR"
        ds.StudyDescription = "PA Chest X-Ray"
        ds.BodyPartExamined = "CHEST"
        ds.StudyInstanceUID = generate_uid()
        ds.SeriesInstanceUID = generate_uid()
        ds.StudyDate = "20260214"
        ds.Rows = 64
        ds.Columns = 64
        ds.BitsAllocated = 16
        ds.BitsStored = 12
        ds.HighBit = 11
        ds.PixelRepresentation = 0
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.PixelData = np.zeros((64, 64), dtype=np.uint16).tobytes()
        ds.save_as(str(filename))

    def _generate_pdf(self, profile, scenario, out_dir):
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas

        filename = out_dir / "sim_lab_report.pdf"
        c = canvas.Canvas(str(filename), pagesize=A4)
        w, h = A4

        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, h - 50, "AIIMS New Delhi")
        c.setFont("Helvetica", 10)
        c.drawString(100, h - 65, "Department of Pathology")

        c.setFont("Helvetica", 11)
        y = h - 100
        c.drawString(50, y, f"Patient: {profile.name}")
        c.drawString(300, y, f"DOB: {_format_dob(profile.dob)}")
        y -= 18
        c.drawString(50, y, f"Gender: {profile.gender.title()}")
        c.drawString(300, y, f"MRN: {profile.mrn}")
        y -= 18
        c.drawString(50, y, "Date: 14-Feb-2026")

        y -= 35
        c.setFont("Helvetica-Bold", 13)
        c.drawString(50, y, "Complete Blood Count & Metabolic Panel")

        y -= 30
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Test Name")
        c.drawString(250, y, "Result")
        c.drawString(350, y, "Unit")
        c.drawString(440, y, "Reference Range")
        y -= 5
        c.line(50, y, 550, y)
        y -= 15

        c.setFont("Helvetica", 10)
        for lab in scenario.labs:
            c.drawString(50, y, lab["name"])
            c.drawString(250, y, f"{lab['value']}")
            c.drawString(350, y, lab["unit"])
            c.drawString(440, y, f"{lab['ref_low']}-{lab['ref_high']}")
            y -= 18

        c.save()


def _format_dob(dob: str) -> str:
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    parts = dob.split("-")
    if len(parts) == 3:
        return f"{int(parts[2])}-{months[int(parts[1])-1]}-{parts[0]}"
    return dob
