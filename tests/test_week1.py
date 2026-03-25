"""
Unit tests for Week 1 modules
Module 22: Test Suite
"""

import pytest
import os
import sys
from pathlib import Path
import pandas as pd
from io import StringIO

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion.validator import DataValidator
from src.llm.provider import OllamaProvider, GeminiProvider, get_llm_provider
from src.agents.problem_detector import AutoProblemDetector, ProblemDetectionState


class TestDataValidator:
    """Test data validation module."""

    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        return DataValidator()

    @pytest.fixture
    def sample_csv(self):
        """Create sample CSV data."""
        return "age,income,purchased\n25,50000,yes\n30,60000,no\n35,70000,yes"

    def test_upload_csv(self, validator, sample_csv):
        """Test CSV upload and validation."""
        result = validator.upload_csv(sample_csv, "test.csv")

        assert result["success"] is True
        assert "job_id" in result
        assert result["rows"] == 3
        assert result["cols"] == 3
        assert "schema" in result

    def test_schema_detection(self, validator):
        """Test schema detection."""
        csv_data = "name,value,ratio\nAlice,100,0.5\nBob,200,0.7"
        result = validator.upload_csv(csv_data, "test.csv")

        schema = result["schema"]
        assert "name" in schema
        assert schema["value"]["detected_type"] == "numeric"

    def test_validation_checks(self, validator, sample_csv):
        """Test validation checks."""
        result = validator.upload_csv(sample_csv, "test.csv")
        validations = result["validation_results"]

        # Should have passed basic checks
        assert len(validations) > 0
        assert any(check["passed"] for check in validations)

    def test_job_status(self, validator, sample_csv):
        """Test retrieving job status."""
        upload_result = validator.upload_csv(sample_csv, "test.csv")
        job_id = upload_result["job_id"]

        status = validator.get_job_status(job_id)

        assert status["job_id"] == job_id
        assert status["rows"] == 3
        assert "schema" in status

    def test_invalid_csv(self, validator):
        """Test handling of invalid CSV."""
        invalid_csv = "this is not,valid csv\n,,"
        result = validator.upload_csv(invalid_csv, "invalid.csv")

        # Should either succeed with the data or return error
        if not result["success"]:
            assert "error" in result


class TestLLMProvider:
    """Test LLM provider module."""

    def test_get_ollama_provider(self):
        """Test getting Ollama provider."""
        os.environ["LLM_PROVIDER"] = "ollama"
        provider = get_llm_provider(provider="ollama")

        assert isinstance(provider, OllamaProvider)
        assert provider.model == "mistral"

    def test_ollama_provider_init(self):
        """Test Ollama provider initialization."""
        provider = OllamaProvider(
            model="mistral", base_url="http://localhost:11434"
        )

        assert provider.model == "mistral"
        assert provider.base_url == "http://localhost:11434"

    def test_provider_factory(self):
        """Test provider factory function."""
        # Test with explicit provider
        provider = get_llm_provider(provider="ollama")
        assert isinstance(provider, OllamaProvider)


class TestProblemDetector:
    """Test problem detection module."""

    @pytest.fixture
    def detector(self):
        """Create detector instance."""
        return AutoProblemDetector(llm_provider="ollama")

    @pytest.fixture
    def classification_df(self):
        """Create classification dataset."""
        return pd.DataFrame({
            "feature1": [1, 2, 3, 4, 5],
            "feature2": [10, 20, 30, 40, 50],
            "target": ["A", "B", "A", "B", "A"],
        })

    @pytest.fixture
    def regression_df(self):
        """Create regression dataset."""
        return pd.DataFrame({
            "feature1": [1, 2, 3, 4, 5],
            "feature2": [10, 20, 30, 40, 50],
            "price": [100.5, 150.2, 200.1, 250.9, 300.3],
        })

    def test_problem_type_classification(self, detector, classification_df):
        """Test classification detection."""
        problem_type, _ = detector._detect_problem_type(
            classification_df, "target"
        )
        assert problem_type == "classification"

    def test_problem_type_regression(self, detector, regression_df):
        """Test regression detection."""
        problem_type, _ = detector._detect_problem_type(
            regression_df, "price"
        )
        assert problem_type == "regression"

    def test_heuristic_detection(self, detector, classification_df):
        """Test heuristic target detection."""
        from src.ingestion.validator import DataValidator

        validator = DataValidator()
        schema = validator._detect_schema(classification_df)

        candidates = detector._heuristic_detection(classification_df, schema)

        assert len(candidates) > 0
        # Target column should be a candidate
        candidate_names = [name for name, _ in candidates]
        assert "target" in candidate_names


class TestIntegration:
    """Integration tests."""

    def test_full_pipeline(self):
        """Test basic pipeline flow."""
        # Create sample data
        csv_data = "age,salary,promoted\n25,50000,no\n35,60000,yes\n45,70000,yes"

        # Upload
        validator = DataValidator()
        result = validator.upload_csv(csv_data, "test.csv")

        assert result["success"]
        assert result["rows"] == 3

        # Get status
        job_id = result["job_id"]
        status = validator.get_job_status(job_id)

        assert status["job_id"] == job_id
        assert len(status["validations"]) > 0

        # Problem detection setup
        df = validator.load_dataframe(job_id)
        assert df is not None
        assert len(df) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
