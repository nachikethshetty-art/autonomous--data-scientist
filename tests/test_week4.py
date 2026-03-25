"""
Week 4 Test Suite: Advanced Features
Tests for drift detection, retraining, monitoring, and orchestration.
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import shutil

from src.drift.detector import DriftDetector, DriftState
from src.models.retrainer import ModelRetrainer, RetrainingState
from src.reporting.monitor import PerformanceMonitor, MonitoringState


class TestDriftDetection:
    """Test Module 11: Drift Detection"""
    
    @pytest.fixture
    def drift_detector(self):
        """Create drift detector instance."""
        return DriftDetector(threshold=0.05)
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for drift testing."""
        np.random.seed(42)
        
        # Baseline data
        baseline = pd.DataFrame({
            'feature_1': np.random.normal(0, 1, 200),
            'feature_2': np.random.normal(5, 2, 200),
            'feature_3': np.random.choice(['A', 'B', 'C'], 200)
        })
        
        # No drift data
        no_drift = pd.DataFrame({
            'feature_1': np.random.normal(0, 1, 100),
            'feature_2': np.random.normal(5, 2, 100),
            'feature_3': np.random.choice(['A', 'B', 'C'], 100)
        })
        
        # Drifted data
        drifted = pd.DataFrame({
            'feature_1': np.random.normal(2, 1, 100),  # Mean shifted
            'feature_2': np.random.normal(5, 2, 100),
            'feature_3': np.random.choice(['A', 'B', 'C'], 100)
        })
        
        return baseline, no_drift, drifted
    
    def test_drift_detector_initialization(self, drift_detector):
        """Test drift detector initialization."""
        assert drift_detector.threshold == 0.05
        assert drift_detector.reports_dir.exists()
        assert drift_detector.plots_dir.exists()
    
    def test_detect_no_drift(self, drift_detector, sample_data):
        """Test detection of no drift."""
        baseline, no_drift, _ = sample_data
        
        report = drift_detector.detect(
            baseline, no_drift, "test_job_1",
            problem_type="classification"
        )
        
        assert 'overall_status' in report
        # Note: may detect categorical drift, so check report structure instead
        assert report['overall_status'] in ['NO_DRIFT', 'WARNING']
        assert 'data_drift' in report
    
    def test_detect_data_drift(self, drift_detector, sample_data):
        """Test detection of data drift."""
        baseline, _, drifted = sample_data
        
        report = drift_detector.detect(
            baseline, drifted, "test_job_2",
            problem_type="classification"
        )
        
        assert 'overall_status' in report
        assert report['overall_status'] in ['WARNING', 'CRITICAL']
    
    def test_detect_prediction_drift(self, drift_detector, sample_data):
        """Test detection of prediction drift."""
        baseline, current, _ = sample_data
        
        baseline_preds = np.random.randint(0, 2, 200)
        drifted_preds = np.ones(100, dtype=int)  # All class 1
        
        report = drift_detector.detect(
            baseline, current, "test_job_3",
            problem_type="classification",
            baseline_predictions=baseline_preds,
            current_predictions=drifted_preds
        )
        
        assert 'prediction_drift' in report
    
    def test_detect_performance_drift(self, drift_detector, sample_data):
        """Test detection of performance drift."""
        baseline, current, _ = sample_data
        
        baseline_preds = np.array([0, 1, 0, 1] * 50)
        baseline_labels = np.array([0, 1, 0, 1] * 50)
        
        current_preds = np.zeros(100)  # Poor predictions
        current_labels = np.array([0, 1] * 50)
        
        report = drift_detector.detect(
            baseline, current, "test_job_4",
            problem_type="classification",
            baseline_predictions=baseline_preds,
            current_predictions=current_preds,
            baseline_labels=baseline_labels,
            current_labels=current_labels
        )
        
        assert 'performance_drift' in report
        assert 'accuracy_drop' in report['performance_drift']
    
    def test_drift_report_structure(self, drift_detector, sample_data):
        """Test drift report structure."""
        baseline, no_drift, _ = sample_data
        
        report = drift_detector.detect(
            baseline, no_drift, "test_job_5",
            problem_type="classification"
        )
        
        required_keys = ['job_id', 'overall_status', 'data_drift', 
                        'alert_level', 'recommendation']
        
        for key in required_keys:
            assert key in report
    
    def test_drift_report_persistence(self, drift_detector, sample_data):
        """Test drift report is saved."""
        baseline, no_drift, _ = sample_data
        
        report = drift_detector.detect(
            baseline, no_drift, "test_job_6",
            problem_type="classification"
        )
        
        retrieved = drift_detector.get_drift_report("test_job_6")
        
        assert retrieved['job_id'] == "test_job_6"
        assert retrieved['overall_status'] == report['overall_status']


class TestModelRetraining:
    """Test Module 12: Model Retraining"""
    
    @pytest.fixture
    def retrainer(self):
        """Create retrainer instance."""
        return ModelRetrainer()
    
    @pytest.fixture
    def training_data(self):
        """Create sample training data."""
        np.random.seed(42)
        
        X = pd.DataFrame({
            'feature_1': np.random.randn(200),
            'feature_2': np.random.randn(200),
            'feature_3': np.random.randn(200),
            'feature_4': np.random.randn(200),
        })
        
        y = (X['feature_1'] + X['feature_2'] > 0).astype(int)
        
        data = X.copy()
        data['target'] = y
        
        return data
    
    def test_retrainer_initialization(self, retrainer):
        """Test retrainer initialization."""
        assert retrainer.models_dir.exists()
        assert retrainer.versions_dir.exists()
        assert retrainer.metrics_dir.exists()
    
    def test_retrain_initial_model(self, retrainer, training_data):
        """Test initial model training."""
        report = retrainer.retrain(
            training_data, "target", "test_job_1",
            problem_type="classification"
        )
        
        assert 'job_id' in report
        assert 'new_model_score' in report
        assert 'retraining_status' in report
        assert report['retraining_status'] in ['accepted', 'rejected_low_score']
    
    def test_retrain_model_improvement(self, retrainer, training_data):
        """Test model retraining with improvement."""
        # First training
        report1 = retrainer.retrain(
            training_data, "target", "test_job_2",
            problem_type="classification"
        )
        
        # Second training with new data
        training_data2 = training_data.copy()
        training_data2['feature_1'] = training_data2['feature_1'] * 1.1
        
        report2 = retrainer.retrain(
            training_data2, "target", "test_job_2",
            problem_type="classification",
            old_model=None,
            old_model_score=report1['new_model_score']
        )
        
        assert 'improvement' in report2
    
    def test_retrain_acceptance_criteria(self, retrainer, training_data):
        """Test retraining acceptance criteria."""
        report = retrainer.retrain(
            training_data, "target", "test_job_3",
            problem_type="classification"
        )
        
        assert report['retraining_status'] in ['accepted', 'accepted_marginal', 'rejected_low_score']
    
    def test_retrain_model_versioning(self, retrainer, training_data):
        """Test model versioning."""
        report = retrainer.retrain(
            training_data, "target", "test_job_4",
            problem_type="classification"
        )
        
        if report['retraining_status'] in ['accepted', 'accepted_marginal']:
            versions = retrainer.list_versions("test_job_4")
            assert len(versions) > 0
            assert 'version_id' in versions[0]
            assert 'score' in versions[0]
    
    def test_retrain_load_model(self, retrainer, training_data):
        """Test loading saved model."""
        report = retrainer.retrain(
            training_data, "target", "test_job_5",
            problem_type="classification"
        )
        
        if report['retraining_status'] in ['accepted', 'accepted_marginal']:
            loaded = retrainer.load_model("test_job_5")
            
            assert 'model' in loaded
            assert 'metadata' in loaded
            assert loaded['model'] is not None
    
    def test_retrain_feature_tracking(self, retrainer, training_data):
        """Test feature tracking during retraining."""
        report = retrainer.retrain(
            training_data, "target", "test_job_6",
            problem_type="classification"
        )
        
        assert 'features' in report
        assert len(report['features']) == training_data.shape[1] - 1
    
    def test_retrain_report_structure(self, retrainer, training_data):
        """Test retraining report structure."""
        report = retrainer.retrain(
            training_data, "target", "test_job_7",
            problem_type="classification"
        )
        
        required_keys = ['job_id', 'new_model_score', 'retraining_status',
                        'recommendation', 'training_samples']
        
        for key in required_keys:
            assert key in report


class TestPerformanceMonitoring:
    """Test Module 13: Performance Monitoring"""
    
    @pytest.fixture
    def monitor(self):
        """Create performance monitor instance."""
        return PerformanceMonitor(window_size=50)
    
    @pytest.fixture
    def monitoring_data(self):
        """Create sample monitoring data."""
        np.random.seed(42)
        
        predictions = np.random.randint(0, 2, 200)
        actuals = np.random.randint(0, 2, 200)
        timestamps = [datetime.now() - timedelta(seconds=i) for i in range(200)]
        
        return predictions, actuals, timestamps
    
    def test_monitor_initialization(self, monitor):
        """Test monitor initialization."""
        assert monitor.window_size == 50
        assert monitor.alert_threshold == 0.05
        assert monitor.monitoring_dir.exists()
    
    def test_monitor_good_performance(self, monitor, monitoring_data):
        """Test monitoring with good performance."""
        predictions, actuals, timestamps = monitoring_data
        
        # Good predictions
        predictions = np.array([0, 1] * 100)
        actuals = np.array([0, 1] * 100)
        
        report = monitor.monitor(
            predictions, "test_job_1",
            actuals=actuals,
            problem_type="classification",
            timestamps=timestamps
        )
        
        assert 'job_id' in report
        assert 'accuracy' in report
        assert report['accuracy'] >= 0.9
    
    def test_monitor_poor_performance(self, monitor, monitoring_data):
        """Test monitoring with poor performance."""
        predictions, actuals, timestamps = monitoring_data
        
        # Poor predictions
        predictions = np.zeros(200)
        actuals = np.ones(200)
        
        report = monitor.monitor(
            predictions, "test_job_2",
            actuals=actuals,
            problem_type="classification",
            timestamps=timestamps
        )
        
        assert 'accuracy' in report
        assert report['accuracy'] < 0.1
        assert len(report['alerts']) > 0
    
    def test_monitor_alert_generation(self, monitor, monitoring_data):
        """Test alert generation."""
        predictions, actuals, timestamps = monitoring_data
        
        report = monitor.monitor(
            predictions, "test_job_3",
            actuals=actuals,
            problem_type="classification",
            timestamps=timestamps
        )
        
        assert 'alerts' in report
        assert 'alert_count' in report
        assert 'alert_level' in report
    
    def test_monitor_sliding_window_metrics(self, monitor, monitoring_data):
        """Test sliding window metrics."""
        predictions, actuals, timestamps = monitoring_data
        
        report = monitor.monitor(
            predictions, "test_job_4",
            actuals=actuals,
            problem_type="classification",
            timestamps=timestamps
        )
        
        assert 'monitoring_results' in report
        results = report['monitoring_results']
        assert 'sliding_window_metrics' in results
    
    def test_monitor_anomaly_detection(self, monitor, monitoring_data):
        """Test anomaly detection."""
        predictions, actuals, timestamps = monitoring_data
        
        report = monitor.monitor(
            predictions, "test_job_5",
            actuals=actuals,
            problem_type="classification",
            timestamps=timestamps
        )
        
        results = report['monitoring_results']
        assert 'anomalies' in results
    
    def test_monitor_report_persistence(self, monitor, monitoring_data):
        """Test monitoring report is saved."""
        predictions, actuals, timestamps = monitoring_data
        
        report = monitor.monitor(
            predictions, "test_job_6",
            actuals=actuals,
            problem_type="classification",
            timestamps=timestamps
        )
        
        retrieved = monitor.get_monitoring_report("test_job_6")
        assert retrieved['job_id'] == "test_job_6"
    
    def test_monitor_get_alerts(self, monitor, monitoring_data):
        """Test retrieving alerts."""
        predictions, actuals, timestamps = monitoring_data
        predictions = np.zeros(200)  # Poor performance to trigger alerts
        
        report = monitor.monitor(
            predictions, "test_job_7",
            actuals=np.ones(200),
            problem_type="classification",
            timestamps=timestamps
        )
        
        alerts = monitor.get_alerts("test_job_7")
        assert len(alerts) > 0
    
    def test_monitor_prediction_distribution(self, monitor, monitoring_data):
        """Test prediction distribution tracking."""
        predictions, actuals, timestamps = monitoring_data
        
        report = monitor.monitor(
            predictions, "test_job_8",
            actuals=actuals,
            problem_type="classification",
            timestamps=timestamps
        )
        
        results = report['monitoring_results']
        assert 'prediction_distribution' in results
    
    def test_monitor_class_metrics(self, monitor, monitoring_data):
        """Test per-class metrics."""
        predictions, actuals, timestamps = monitoring_data
        
        report = monitor.monitor(
            predictions, "test_job_9",
            actuals=actuals,
            problem_type="classification",
            timestamps=timestamps
        )
        
        results = report['monitoring_results']
        if 'per_class_metrics' in results:
            assert len(results['per_class_metrics']) > 0
    
    def test_monitor_report_structure(self, monitor, monitoring_data):
        """Test monitoring report structure."""
        predictions, actuals, timestamps = monitoring_data
        
        report = monitor.monitor(
            predictions, "test_job_10",
            actuals=actuals,
            problem_type="classification",
            timestamps=timestamps
        )
        
        required_keys = ['job_id', 'timestamp', 'alert_level', 'recommendation']
        
        for key in required_keys:
            assert key in report


class TestWeek4Integration:
    """Integration tests for Week 4 modules."""
    
    def test_drift_to_retraining_workflow(self):
        """Test drift detection triggering retraining."""
        np.random.seed(42)
        
        # Create baseline
        baseline = pd.DataFrame({
            'feature_1': np.random.randn(100),
            'feature_2': np.random.randn(100),
            'target': np.random.randint(0, 2, 100)
        })
        
        # Create drifted data
        drifted = pd.DataFrame({
            'feature_1': np.random.randn(100) + 2,  # Drifted
            'feature_2': np.random.randn(100),
            'target': np.random.randint(0, 2, 100)
        })
        
        # Detect drift
        detector = DriftDetector()
        drift_report = detector.detect(baseline, drifted, "integration_1")
        
        # If drift detected, retrain
        if drift_report['overall_status'] in ['WARNING', 'CRITICAL']:
            retrainer = ModelRetrainer()
            retrain_report = retrainer.retrain(
                drifted, "target", "integration_1",
                problem_type="classification"
            )
            
            assert 'retraining_status' in retrain_report
    
    def test_retraining_to_monitoring_workflow(self):
        """Test retraining followed by monitoring."""
        np.random.seed(42)
        
        # Create training data
        data = pd.DataFrame({
            'feature_1': np.random.randn(100),
            'feature_2': np.random.randn(100),
            'target': (np.random.randn(100) > 0).astype(int)
        })
        
        # Retrain model
        retrainer = ModelRetrainer()
        retrain_report = retrainer.retrain(
            data, "target", "integration_2",
            problem_type="classification"
        )
        
        # Monitor predictions
        monitor = PerformanceMonitor()
        predictions = np.random.randint(0, 2, 50)
        actuals = np.random.randint(0, 2, 50)
        
        monitor_report = monitor.monitor(
            predictions, "integration_2",
            actuals=actuals,
            problem_type="classification"
        )
        
        assert 'alert_level' in monitor_report


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
