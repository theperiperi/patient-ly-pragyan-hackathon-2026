"""Integration tests for the full ingestion pipeline."""

import json
import pytest
from pathlib import Path

from ingest.pipeline.ingestion import IngestionPipeline


class TestIngestionPipeline:

    def setup_method(self):
        self.pipeline = IngestionPipeline()

    def test_ingest_single_hl7(self, ehr_admission):
        result = self.pipeline.ingest_file(ehr_admission)
        assert result is not None
        assert result.source_type == "hospital_ehr"

    def test_ingest_single_apple_health(self, apple_health):
        result = self.pipeline.ingest_file(apple_health)
        assert result is not None
        assert result.source_type == "wearable"

    def test_ingest_unsupported_returns_none(self, tmp_path):
        f = tmp_path / "random.txt"
        f.write_text("this is not medical data")
        result = self.pipeline.ingest_file(str(f))
        assert result is None

    def test_ingest_directory(self, sample_data_dir):
        bundles = self.pipeline.ingest_directory(str(sample_data_dir))
        assert len(bundles) >= 1
        for bundle in bundles:
            assert bundle.type == "transaction"
            assert len(bundle.entry) >= 1
            assert bundle.entry[0].resource.get_resource_type() == "Patient"

    def test_patient_linking_across_sources(self, sample_data_dir):
        bundles = self.pipeline.ingest_directory(str(sample_data_dir))
        # Rajesh Kumar + Priya Sharma = at least 2 patient bundles
        assert len(bundles) >= 2
        # Find the bundle with the most entries (Rajesh, linked from multiple sources)
        entry_counts = [len(b.entry) for b in bundles]
        max_idx = entry_counts.index(max(entry_counts))
        rajesh_bundle = bundles[max_idx]
        assert len(rajesh_bundle.entry) >= 10

    def test_run_writes_output(self, sample_data_dir, tmp_path):
        output_dir = str(tmp_path / "output")
        files = self.pipeline.run(str(sample_data_dir), output_dir)
        assert len(files) >= 1
        for f in files:
            assert Path(f).exists()
            content = json.loads(Path(f).read_text())
            assert content["resourceType"] == "Bundle"
