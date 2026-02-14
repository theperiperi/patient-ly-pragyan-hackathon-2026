"""Tests for the Scans & Labs adapter."""

import pytest
from ingest.adapters.scans_labs_adapter import ScansLabsAdapter


class TestScansLabsAdapter:

    def setup_method(self):
        self.adapter = ScansLabsAdapter()

    def test_source_type(self):
        assert self.adapter.source_type == "scans_labs"

    def test_supports_dicom(self, dicom_file):
        assert self.adapter.supports(dicom_file) is True

    def test_supports_pdf(self, pdf_lab):
        assert self.adapter.supports(pdf_lab) is True

    def test_supports_rejects_json(self, bedside_json):
        assert self.adapter.supports(bedside_json) is False

    def test_parse_dicom(self, dicom_file):
        result = self.adapter.parse(dicom_file)
        assert result is not None
        assert result.source_type == "scans_labs"
        resource_types = [r.get_resource_type() for r in result.fhir_resources]
        assert "ImagingStudy" in resource_types
        assert "DocumentReference" in resource_types

    def test_parse_pdf(self, pdf_lab):
        result = self.adapter.parse(pdf_lab)
        assert result is not None
        resource_types = [r.get_resource_type() for r in result.fhir_resources]
        assert "DocumentReference" in resource_types
