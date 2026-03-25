"""
Week 3 Tests - Feature Engineering, AutoML Training, and Model Evaluation
Tests for Modules 7, 8, and 9
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import json

from src.features import FeatureEngineeringAgent
from src.models import AutoMLTrainer, ModelEvaluator


# Test Data Fixtures
@pytest.fixture
def classification_data():
    """Create classification test dataset."""
    np.random.seed(42)
    
    # Create dataset
    n_samples = 200
    X = pd.DataFrame({
        'feature_1': np.random.randn(n_samples),
        'feature_2': np.random.randn(n_samples),
        'feature_3': np.random.randn(n_samples),
        'feature_4': np.random.randn(n_samples),
        'feature_5': np.random.randn(n_samples),
    })
    
    # Create target
    y = (X['feature_1'] + X['feature_2'] > 0).astype(int)
    
    return X, y


@pytest.fixture
def regression_data():
    """Create regression test dataset."""
    np.random.seed(42)
    
    # Create dataset
    n_samples = 200
    X = pd.DataFrame({
        'feature_1': np.random.randn(n_samples),
        'feature_2': np.random.randn(n_samples),
        'feature_3': np.random.randn(n_samples),
        'feature_4': np.random.randn(n_samples),
        'feature_5': np.random.randn(n_samples),
    })
    
    # Create target
    y = X['feature_1'] * 2 + X['feature_2'] * 3 + np.random.randn(n_samples) * 0.1
    
    return X, y


@pytest.fixture
def schema():
    """Create test schema."""
    return {
        'feature_1': {'type': 'numeric'},
        'feature_2': {'type': 'numeric'},
        'feature_3': {'type': 'numeric'},
        'feature_4': {'type': 'numeric'},
        'feature_5': {'type': 'numeric'},
    }


@pytest.fixture
def metadata():
    """Create test metadata."""
    return {
        'source': 'test',
        'rows': 200,
        'columns': 5
    }


# ============================================================================
# Feature Engineering Tests (Module 7)
# ============================================================================

class TestFeatureEngineering:
    """Tests for Feature Engineering Agent (Module 7)."""
    
    def test_feature_engineer_initialization(self):
        """Test FeatureEngineeringAgent initialization."""
        agent = FeatureEngineeringAgent()
        
        assert agent.logs_dir.exists()
        assert agent.scaler is not None
    
    def test_generate_polynomial_features_classification(self, classification_data, schema, metadata):
        """Test polynomial feature generation for classification."""
        X, y = classification_data
        agent = FeatureEngineeringAgent()
        
        X_engineered, log = agent.engineer(
            X, schema, metadata, "test_job_001", 
            problem_type="classification", strategy="smart"
        )
        
        assert X_engineered.shape[0] == X.shape[0]
        assert X_engineered.shape[1] > X.shape[1]  # More features
        assert "polynomial_features" in log
        assert log["polynomial_features"]["count"] > 0
    
    def test_generate_interaction_features(self, classification_data, schema, metadata):
        """Test interaction feature generation."""
        X, y = classification_data
        agent = FeatureEngineeringAgent()
        
        X_engineered, log = agent.engineer(
            X, schema, metadata, "test_job_002",
            problem_type="classification", strategy="aggressive"
        )
        
        assert "interaction_features" in log
        assert log["interaction_features"]["count"] > 0
        
        # Check that interaction features were created
        interaction_cols = [col for col in X_engineered.columns if "interact" in col]
        assert len(interaction_cols) > 0
    
    def test_domain_features_generation(self, classification_data, schema, metadata):
        """Test domain-specific feature generation."""
        X, y = classification_data
        
        # Add date column
        X['date_col'] = pd.date_range('2020-01-01', periods=len(X))
        
        schema['date_col'] = {'type': 'datetime'}
        
        agent = FeatureEngineeringAgent()
        X_engineered, log = agent.engineer(
            X, schema, metadata, "test_job_003",
            problem_type="classification", strategy="smart"
        )
        
        assert "domain_features" in log
        
        # Check that temporal features were created
        temporal_cols = [col for col in X_engineered.columns if any(
            x in col for x in ['year', 'month', 'day', 'dayofweek', 'quarter']
        )]
        assert len(temporal_cols) > 0
    
    def test_feature_importance_calculation(self, classification_data, schema, metadata):
        """Test feature importance calculation."""
        X, y = classification_data
        agent = FeatureEngineeringAgent()
        
        X_engineered, log = agent.engineer(
            X, schema, metadata, "test_job_004",
            problem_type="classification",
            target_column=None,  # No target provided
            strategy="smart"
        )
        
        assert X_engineered is not None
        assert "feature_selection" in log
    
    def test_conservative_strategy(self, classification_data, schema, metadata):
        """Test conservative feature engineering strategy."""
        X, y = classification_data
        agent = FeatureEngineeringAgent()
        
        X_conservative, log_cons = agent.engineer(
            X, schema, metadata, "test_cons",
            problem_type="classification", strategy="conservative"
        )
        
        X_aggressive, log_agg = agent.engineer(
            X, schema, metadata, "test_agg",
            problem_type="classification", strategy="aggressive"
        )
        
        # Conservative should produce fewer features
        assert X_conservative.shape[1] <= X_aggressive.shape[1]
    
    def test_regression_engineering(self, regression_data, schema, metadata):
        """Test feature engineering for regression."""
        X, y = regression_data
        agent = FeatureEngineeringAgent()
        
        X_engineered, log = agent.engineer(
            X, schema, metadata, "test_job_reg",
            problem_type="regression", strategy="smart"
        )
        
        assert X_engineered.shape[0] == X.shape[0]
        assert X_engineered.shape[1] > X.shape[1]
        assert "feature_selection" in log
        assert len(X_engineered.columns) > 0


# ============================================================================
# AutoML Training Tests (Module 8)
# ============================================================================

class TestAutoMLTraining:
    """Tests for AutoML Trainer (Module 8)."""
    
    def test_automl_initialization(self):
        """Test AutoMLTrainer initialization."""
        trainer = AutoMLTrainer()
        
        assert trainer.logs_dir.exists()
        assert trainer.models_dir.exists()
        assert trainer.scaler is not None
    
    def test_train_classification_models(self, classification_data):
        """Test training classification models."""
        X, y = classification_data
        
        # Split data
        split_idx = int(0.8 * len(X))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        trainer = AutoMLTrainer()
        models, log = trainer.train(
            X_train, y_train, X_test, y_test,
            job_id="test_class_001",
            problem_type="classification",
            n_trials=5,
            strategy="conservative"
        )
        
        assert len(models) > 0
        assert "best_model" in log
        assert log["best_model"]["name"] in models
        assert "model_training" in log
    
    def test_train_regression_models(self, regression_data):
        """Test training regression models."""
        X, y = regression_data
        
        # Split data
        split_idx = int(0.8 * len(X))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        trainer = AutoMLTrainer()
        models, log = trainer.train(
            X_train, y_train, X_test, y_test,
            job_id="test_reg_001",
            problem_type="regression",
            n_trials=5,
            strategy="conservative"
        )
        
        assert len(models) > 0
        assert "best_model" in log
        assert log["best_model"]["name"] is not None
    
    def test_cross_validation(self, classification_data):
        """Test cross-validation during training."""
        X, y = classification_data
        
        trainer = AutoMLTrainer()
        models, log = trainer.train(
            X, y,
            job_id="test_cv_001",
            problem_type="classification",
            n_trials=3,
            strategy="conservative"
        )
        
        assert "cross_validation" in log
        assert len(log["cross_validation"]) > 0
        
        for model_name, cv_result in log["cross_validation"].items():
            assert "mean_test_score" in cv_result
            assert "std_test_score" in cv_result
    
    def test_hyperparameter_optimization(self, classification_data):
        """Test hyperparameter optimization."""
        X, y = classification_data
        
        trainer = AutoMLTrainer()
        models, log = trainer.train(
            X, y,
            job_id="test_opt_001",
            problem_type="classification",
            n_trials=5,
            strategy="smart"
        )
        
        assert "model_training" in log
        assert "optimization_history" in log["model_training"]
        
        opt_history = log["model_training"]["optimization_history"]
        for model_name, history in opt_history.items():
            assert "best_params" in history
            assert "best_value" in history
            assert "n_trials" in history
    
    def test_strategy_variations(self, classification_data):
        """Test different training strategies."""
        X, y = classification_data
        
        trainer = AutoMLTrainer()
        
        # Conservative
        models_cons, log_cons = trainer.train(
            X, y, job_id="test_cons_001",
            problem_type="classification", n_trials=10, strategy="conservative"
        )
        
        # Aggressive
        models_agg, log_agg = trainer.train(
            X, y, job_id="test_agg_001",
            problem_type="classification", n_trials=10, strategy="aggressive"
        )
        
        # Conservative should use fewer trials
        cons_trials = sum(
            h["n_trials"] 
            for h in log_cons["model_training"]["optimization_history"].values()
        )
        agg_trials = sum(
            h["n_trials"] 
            for h in log_agg["model_training"]["optimization_history"].values()
        )
        
        assert cons_trials <= agg_trials
    
    def test_get_training_report(self, classification_data):
        """Test retrieving training report."""
        X, y = classification_data
        
        trainer = AutoMLTrainer()
        models, log = trainer.train(
            X, y, job_id="test_report_001",
            problem_type="classification", n_trials=3,
            strategy="conservative"
        )
        
        report = trainer.get_training_report("test_report_001")
        
        assert report is not None
        assert "best_model" in report


# ============================================================================
# Model Evaluation Tests (Module 9)
# ============================================================================

class TestModelEvaluation:
    """Tests for Model Evaluator (Module 9)."""
    
    def test_evaluator_initialization(self):
        """Test ModelEvaluator initialization."""
        evaluator = ModelEvaluator()
        
        assert evaluator.plots_dir.exists()
        assert evaluator.reports_dir.exists()
    
    def test_classification_evaluation(self, classification_data):
        """Test classification model evaluation."""
        from sklearn.ensemble import RandomForestClassifier
        
        X, y = classification_data
        
        # Split data
        split_idx = int(0.8 * len(X))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Train model
        model = RandomForestClassifier(n_estimators=50, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        evaluator = ModelEvaluator()
        report = evaluator.evaluate(
            model, X_test, y_test,
            job_id="test_class_eval_001",
            problem_type="classification"
        )
        
        assert "metrics" in report
        assert "accuracy" in report["metrics"]
        assert "precision" in report["metrics"]
        assert "recall" in report["metrics"]
        assert "f1" in report["metrics"]
    
    def test_regression_evaluation(self, regression_data):
        """Test regression model evaluation."""
        from sklearn.ensemble import RandomForestRegressor
        
        X, y = regression_data
        
        # Split data
        split_idx = int(0.8 * len(X))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Train model
        model = RandomForestRegressor(n_estimators=50, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        evaluator = ModelEvaluator()
        report = evaluator.evaluate(
            model, X_test, y_test,
            job_id="test_reg_eval_001",
            problem_type="regression"
        )
        
        assert "metrics" in report
        assert "r2" in report["metrics"]
        assert "mse" in report["metrics"]
        assert "rmse" in report["metrics"]
        assert "mae" in report["metrics"]
    
    def test_confusion_matrix_generation(self, classification_data):
        """Test confusion matrix generation."""
        from sklearn.ensemble import RandomForestClassifier
        
        X, y = classification_data
        
        split_idx = int(0.8 * len(X))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        model = RandomForestClassifier(n_estimators=50, random_state=42)
        model.fit(X_train, y_train)
        
        evaluator = ModelEvaluator()
        report = evaluator.evaluate(
            model, X_test, y_test,
            job_id="test_cm_001",
            problem_type="classification"
        )
        
        assert "confusion_matrix" in report["metrics"]
        cm = report["metrics"]["confusion_matrix"]
        assert len(cm) > 0
        assert len(cm[0]) > 0
    
    def test_feature_importance_calculation(self, classification_data):
        """Test feature importance calculation."""
        from sklearn.ensemble import RandomForestClassifier
        
        X, y = classification_data
        
        split_idx = int(0.8 * len(X))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        model = RandomForestClassifier(n_estimators=50, random_state=42)
        model.fit(X_train, y_train)
        
        evaluator = ModelEvaluator()
        report = evaluator.evaluate(
            model, X_test, y_test,
            job_id="test_fi_001",
            problem_type="classification"
        )
        
        assert "feature_importance" in report
        assert len(report["feature_importance"]) > 0
        
        # Check that features are ranked
        importances = list(report["feature_importance"].values())
        assert importances == sorted(importances, reverse=True)
    
    def test_visualizations_generation(self, classification_data):
        """Test visualization generation."""
        from sklearn.ensemble import RandomForestClassifier
        
        X, y = classification_data
        
        split_idx = int(0.8 * len(X))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        model = RandomForestClassifier(n_estimators=50, random_state=42)
        model.fit(X_train, y_train)
        
        evaluator = ModelEvaluator()
        report = evaluator.evaluate(
            model, X_test, y_test,
            job_id="test_plots_001",
            problem_type="classification"
        )
        
        assert "plots_generated" in report
        plots = report["plots_generated"]
        assert len(plots) > 0
        
        # Check that plot files exist
        plot_dir = evaluator.plots_dir / "test_plots_001"
        for plot_name in plots:
            plot_path = plot_dir / plot_name
            assert plot_path.exists()
    
    def test_get_evaluation_report(self, classification_data):
        """Test retrieving evaluation report."""
        from sklearn.ensemble import RandomForestClassifier
        
        X, y = classification_data
        
        split_idx = int(0.8 * len(X))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        model = RandomForestClassifier(n_estimators=50, random_state=42)
        model.fit(X_train, y_train)
        
        evaluator = ModelEvaluator()
        report = evaluator.evaluate(
            model, X_test, y_test,
            job_id="test_report_001",
            problem_type="classification"
        )
        
        retrieved_report = evaluator.get_evaluation_report("test_report_001")
        
        assert retrieved_report is not None
        assert "metrics" in retrieved_report
    
    def test_regression_visualizations(self, regression_data):
        """Test regression-specific visualizations."""
        from sklearn.ensemble import RandomForestRegressor
        
        X, y = regression_data
        
        split_idx = int(0.8 * len(X))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        model = RandomForestRegressor(n_estimators=50, random_state=42)
        model.fit(X_train, y_train)
        
        evaluator = ModelEvaluator()
        report = evaluator.evaluate(
            model, X_test, y_test,
            job_id="test_reg_plots_001",
            problem_type="regression"
        )
        
        assert "plots_generated" in report
        plots = report["plots_generated"]
        
        # Should have residuals and prediction plots for regression
        plot_names = [p.lower() for p in plots]
        assert any("residual" in p for p in plot_names)


# ============================================================================
# Integration Tests - Week 3 Complete Pipeline
# ============================================================================

class TestWeek3Integration:
    """Integration tests for complete Week 3 pipeline."""
    
    def test_complete_ml_pipeline(self, classification_data):
        """Test complete ML pipeline: Feature Engineering → Training → Evaluation."""
        X, y = classification_data
        
        schema = {col: {'type': 'numeric'} for col in X.columns}
        metadata = {'source': 'test', 'rows': len(X), 'columns': X.shape[1]}
        
        # ============ Feature Engineering ============
        feature_engineer = FeatureEngineeringAgent()
        X_engineered, eng_log = feature_engineer.engineer(
            X, schema, metadata, "pipeline_test_001",
            problem_type="classification", strategy="smart"
        )
        
        assert X_engineered.shape[1] > X.shape[1]
        
        # ============ Data Split ============
        split_idx = int(0.8 * len(X_engineered))
        X_train = X_engineered[:split_idx]
        X_test = X_engineered[split_idx:]
        y_train = y[:split_idx]
        y_test = y[split_idx:]
        
        # ============ AutoML Training ============
        trainer = AutoMLTrainer()
        models, train_log = trainer.train(
            X_train, y_train, X_test, y_test,
            job_id="pipeline_test_001",
            problem_type="classification",
            n_trials=5,
            strategy="conservative"
        )
        
        assert len(models) > 0
        best_model = models[train_log["best_model"]["name"]]
        
        # ============ Model Evaluation ============
        evaluator = ModelEvaluator()
        eval_report = evaluator.evaluate(
            best_model, X_test, y_test,
            job_id="pipeline_test_001",
            problem_type="classification"
        )
        
        assert "metrics" in eval_report
        assert eval_report["metrics"]["accuracy"] >= 0
        assert eval_report["metrics"]["accuracy"] <= 1
        
        print(f"\n✓ Complete pipeline test passed!")
        print(f"  - Features engineered: {X_engineered.shape[1]} (from {X.shape[1]})")
        print(f"  - Models trained: {len(models)}")
        print(f"  - Best model: {train_log['best_model']['name']}")
        print(f"  - Test accuracy: {eval_report['metrics']['accuracy']:.2%}")
