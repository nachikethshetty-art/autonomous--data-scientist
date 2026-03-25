"""
Week 2 Tests - Data Cleaning & EDA
Tests for Modules 2, 5, and 6
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from src.agents.business_context import BusinessContextManager
from src.cleaning.agent import DataCleaningAgent, CleaningState
from src.eda.engine import EDAEngine


class TestBusinessContext:
    """Tests for Business Context Manager (Module 2)."""

    @pytest.fixture
    def context_manager(self):
        """Create a business context manager."""
        return BusinessContextManager()

    def test_create_context(self, context_manager):
        """Test creating a business context."""
        context = context_manager.create_context(
            job_id="test_job_001",
            prediction_goal="Predict customer churn",
            domain="Telecommunications",
            target_audience="Customer retention team",
            success_metric="Precision >= 0.85",
            constraints="Real-time processing",
            special_requirements="Handle imbalanced data",
        )

        assert context["job_id"] == "test_job_001"
        assert context["prediction_goal"] == "Predict customer churn"
        assert context["domain"] == "Telecommunications"
        assert "context_id" in context
        assert "created_at" in context

    def test_get_context(self, context_manager):
        """Test retrieving a business context."""
        context_manager.create_context(
            job_id="test_job_002",
            prediction_goal="Fraud detection",
            domain="Finance",
            target_audience="Risk managers",
            success_metric="AUC >= 0.90",
        )

        retrieved = context_manager.get_context("test_job_002")
        assert retrieved is not None
        assert retrieved["job_id"] == "test_job_002"

    def test_get_insights(self, context_manager):
        """Test generating insights from context."""
        context = {
            "prediction_goal": "Fraud detection",
            "domain": "Finance",
            "constraints": "interpretable",
            "budget": "CPU only",
        }

        insights = context_manager.get_insights(context)
        assert "recommended_models" in insights
        assert "optimization_targets" in insights
        assert len(insights["recommended_models"]) > 0

    def test_get_context_prompt(self, context_manager):
        """Test generating an LLM prompt from context."""
        context = context_manager.create_context(
            job_id="test_job_003",
            prediction_goal="Predict house prices",
            domain="Real Estate",
            target_audience="Real estate agents",
            success_metric="MAE < 50000",
        )

        prompt = context_manager.get_context_prompt(context)
        assert "house prices" in prompt.lower() or "real estate" in prompt.lower()
        assert len(prompt) > 100


class TestDataCleaning:
    """Tests for Data Cleaning Agent (Module 5)."""

    @pytest.fixture
    def sample_dataframe(self):
        """Create a sample dataframe with data quality issues."""
        return pd.DataFrame(
            {
                "age": [25, 30, np.nan, 45, 1000, 28, 32],  # Has missing and outlier
                "salary": [50000, 60000, 55000, np.nan, 70000, 52000, 65000],
                "score": [0, 1, 1, 0, 1, 0, 1],  # Binary variable
                "name": ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace"],
            }
        )

    @pytest.fixture
    def sample_schema(self):
        """Create sample schema."""
        return {
            "age": {"detected_type": "int64"},
            "salary": {"detected_type": "float64"},
            "score": {"detected_type": "int64"},
            "name": {"detected_type": "object"},
        }

    @pytest.fixture
    def sample_metadata(self):
        """Create sample metadata."""
        return {"total_rows": 7, "numeric_columns": ["age", "salary", "score"]}

    def test_clean_dataframe(self, sample_dataframe, sample_schema, sample_metadata):
        """Test basic data cleaning."""
        agent = DataCleaningAgent()
        cleaned_df, log = agent.clean(
            sample_dataframe, sample_schema, sample_metadata, "test_job", strategy="smart"
        )

        # Check that dataframe was modified
        assert len(cleaned_df) <= len(sample_dataframe)
        assert len(log) > 0

        # Check that cleaning log contains steps
        step_numbers = [entry.get("step") for entry in log]
        assert any(s >= 2 for s in step_numbers if s is not None)  # At least some cleaning steps

    def test_handle_missing_values(self, sample_dataframe, sample_schema, sample_metadata):
        """Test missing value handling."""
        agent = DataCleaningAgent()
        df_copy = sample_dataframe.copy()

        # Verify there are missing values initially
        assert df_copy.isnull().sum().sum() > 0

        cleaned_df, log = agent.clean(
            df_copy, sample_schema, sample_metadata, "test_job", strategy="smart"
        )

        # Verify missing values are handled
        assert cleaned_df.isnull().sum().sum() == 0

    def test_outlier_detection(self, sample_dataframe, sample_schema, sample_metadata):
        """Test outlier handling."""
        agent = DataCleaningAgent()
        cleaned_df, log = agent.clean(
            sample_dataframe, sample_schema, sample_metadata, "test_job", strategy="aggressive"
        )

        # Check that outliers were handled
        outlier_actions = [entry for entry in log if "outlier" in entry.get("action", "").lower()]
        assert len(outlier_actions) > 0

    def test_categorical_encoding(self, sample_dataframe, sample_schema, sample_metadata):
        """Test categorical encoding."""
        agent = DataCleaningAgent()
        cleaned_df, log = agent.clean(
            sample_dataframe, sample_schema, sample_metadata, "test_job", strategy="smart"
        )

        # Check that categorical encoding was applied
        encoding_actions = [entry for entry in log if "encode" in entry.get("action", "").lower()]
        assert len(encoding_actions) > 0

    def test_get_cleaning_report(self, sample_dataframe, sample_schema, sample_metadata):
        """Test retrieving cleaning report."""
        agent = DataCleaningAgent()
        agent.clean(sample_dataframe, sample_schema, sample_metadata, "test_report_job")

        report = agent.get_cleaning_report("test_report_job")
        assert report is not None
        assert report["job_id"] == "test_report_job"
        assert "steps" in report


class TestEDAEngine:
    """Tests for EDA Engine (Module 6)."""

    @pytest.fixture
    def sample_dataframe(self):
        """Create a comprehensive sample dataframe."""
        np.random.seed(42)
        return pd.DataFrame(
            {
                "age": np.random.normal(35, 15, 100),
                "income": np.random.normal(50000, 20000, 100),
                "score": np.random.uniform(0, 100, 100),
                "category": np.random.choice(["A", "B", "C"], 100),
                "binary": np.random.choice([0, 1], 100),
            }
        )

    @pytest.fixture
    def sample_schema(self):
        """Create sample schema."""
        return {
            "age": {"detected_type": "float64"},
            "income": {"detected_type": "float64"},
            "score": {"detected_type": "float64"},
            "category": {"detected_type": "object"},
            "binary": {"detected_type": "int64"},
        }

    def test_generate_report(self, sample_dataframe, sample_schema):
        """Test EDA report generation."""
        eda = EDAEngine()
        report = eda.generate_report(sample_dataframe, sample_schema, "test_job")

        assert "job_id" in report
        assert "dataset_shape" in report
        assert "basic_statistics" in report
        assert "column_analysis" in report
        assert "insights" in report

        # Verify shape
        assert report["dataset_shape"]["rows"] == 100
        assert report["dataset_shape"]["columns"] == 5

    def test_generate_plots(self, sample_dataframe, sample_schema):
        """Test plot generation."""
        eda = EDAEngine()
        plot_paths = eda.generate_plots(sample_dataframe, sample_schema, "test_job")

        # Should generate multiple plots
        assert len(plot_paths) > 0

        # Verify plot files exist
        for path in plot_paths:
            assert Path(path).exists()

    def test_correlation_analysis(self, sample_dataframe, sample_schema):
        """Test correlation analysis."""
        eda = EDAEngine()
        report = eda.generate_report(sample_dataframe, sample_schema, "test_job")

        corr_analysis = report.get("correlation_analysis", {})
        assert "strong_correlations" in corr_analysis or "message" in corr_analysis

    def test_missing_value_analysis(self, sample_dataframe, sample_schema):
        """Test missing value analysis."""
        # Add some missing values
        sample_dataframe.loc[0, "age"] = None
        sample_dataframe.loc[1, "income"] = None

        eda = EDAEngine()
        report = eda.generate_report(sample_dataframe, sample_schema, "test_job")

        missing_analysis = report.get("missing_value_analysis", {})
        assert "columns_with_missing" in missing_analysis
        assert "total_missing_pct" in missing_analysis

    def test_categorical_analysis(self, sample_dataframe, sample_schema):
        """Test categorical analysis."""
        eda = EDAEngine()
        report = eda.generate_report(sample_dataframe, sample_schema, "test_job")

        cat_analysis = report.get("categorical_analysis", {})
        assert "category" in cat_analysis
        assert "unique_values" in cat_analysis["category"]

    def test_outlier_analysis(self, sample_dataframe, sample_schema):
        """Test outlier analysis."""
        eda = EDAEngine()
        report = eda.generate_report(sample_dataframe, sample_schema, "test_job")

        outlier_analysis = report.get("outlier_analysis", {})
        assert len(outlier_analysis) > 0

    def test_insights_generation(self, sample_dataframe, sample_schema):
        """Test automated insight generation."""
        eda = EDAEngine()
        report = eda.generate_report(sample_dataframe, sample_schema, "test_job")

        insights = report.get("insights", [])
        assert len(insights) > 0
        assert isinstance(insights[0], str)


class TestWeek2Integration:
    """Integration tests for Week 2 modules."""

    def test_full_week2_workflow(self):
        """Test complete Week 2 workflow: Context -> Cleaning -> EDA."""
        # Create business context
        context_mgr = BusinessContextManager()
        context = context_mgr.create_context(
            job_id="integration_test",
            prediction_goal="Classify customers",
            domain="Retail",
            target_audience="Marketing team",
            success_metric="F1 >= 0.8",
        )
        assert context["job_id"] == "integration_test"

        # Create sample data
        df = pd.DataFrame(
            {
                "age": [25, 30, 35, 40, 45, 50, 55, 60],
                "income": [30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000],
                "purchased": [0, 0, 1, 1, 1, 0, 1, 1],
            }
        )

        schema = {
            "age": {"detected_type": "int64"},
            "income": {"detected_type": "float64"},
            "purchased": {"detected_type": "int64"},
        }

        metadata = {"total_rows": 8, "numeric_columns": ["age", "income"]}

        # Clean data
        cleaner = DataCleaningAgent()
        cleaned_df, cleaning_log = cleaner.clean(df, schema, metadata, "integration_test")
        assert len(cleaned_df) > 0
        assert len(cleaning_log) > 0

        # Generate EDA
        eda = EDAEngine()
        report = eda.generate_report(cleaned_df, schema, "integration_test")
        assert report["job_id"] == "integration_test"
        assert len(report["insights"]) > 0

        print("✅ Week 2 integration test passed!")
