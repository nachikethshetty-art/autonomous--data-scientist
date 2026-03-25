"""
Module 11: Data & Model Drift Detection
Monitor data distribution changes and model performance degradation.
"""

import json
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any
import warnings

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ks_2samp, chi2_contingency
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore")
plt.style.use("seaborn-v0_8-darkgrid")


@dataclass
class DriftState:
    """State for drift detection workflow."""
    job_id: str
    baseline_data: pd.DataFrame
    current_data: pd.DataFrame
    baseline_predictions: np.ndarray = None
    current_predictions: np.ndarray = None
    baseline_labels: pd.Series = None
    current_labels: pd.Series = None
    problem_type: str = "classification"
    data_drift_results: Dict = None
    prediction_drift_results: Dict = None
    performance_drift_results: Dict = None
    overall_drift_status: str = "no_drift"
    drift_report: Dict = None
    
    def __post_init__(self):
        if self.data_drift_results is None:
            self.data_drift_results = {}
        if self.prediction_drift_results is None:
            self.prediction_drift_results = {}
        if self.performance_drift_results is None:
            self.performance_drift_results = {}
        if self.drift_report is None:
            self.drift_report = {}


class DriftDetector:
    """
    Comprehensive drift detection and monitoring.
    
    Features:
    - Data drift detection (Kolmogorov-Smirnov test)
    - Prediction drift detection
    - Model performance drift detection
    - Feature-wise drift analysis
    - Drift severity classification
    - Automated alerting
    """
    
    def __init__(self, threshold: float = 0.05):
        """
        Initialize drift detector.
        
        Args:
            threshold: Statistical significance threshold (p-value)
        """
        self.threshold = threshold
        self.reports_dir = Path("data/drift_reports")
        self.plots_dir = Path("data/drift_plots")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.plots_dir.mkdir(parents=True, exist_ok=True)
    
    def detect(self, baseline_data: pd.DataFrame, current_data: pd.DataFrame,
              job_id: str, problem_type: str = "classification",
              baseline_predictions: Optional[np.ndarray] = None,
              current_predictions: Optional[np.ndarray] = None,
              baseline_labels: Optional[pd.Series] = None,
              current_labels: Optional[pd.Series] = None) -> Dict:
        """
        Detect data and model drift.
        
        Args:
            baseline_data: Historical/baseline training data
            current_data: Current production data
            job_id: Unique job identifier
            problem_type: "classification" or "regression"
            baseline_predictions: Baseline model predictions
            current_predictions: Current model predictions
            baseline_labels: Baseline true labels
            current_labels: Current true labels
        
        Returns:
            Drift detection report
        """
        logger.info(f"Starting drift detection for job {job_id}")
        
        state = DriftState(
            job_id=job_id,
            baseline_data=baseline_data.copy(),
            current_data=current_data.copy(),
            baseline_predictions=baseline_predictions,
            current_predictions=current_predictions,
            baseline_labels=baseline_labels,
            current_labels=current_labels,
            problem_type=problem_type
        )
        
        try:
            # Detect data drift
            state = self._detect_data_drift(state)
            
            # Detect prediction drift
            if baseline_predictions is not None and current_predictions is not None:
                state = self._detect_prediction_drift(state)
            
            # Detect performance drift
            if baseline_labels is not None and current_labels is not None:
                state = self._detect_performance_drift(state)
            
            # Determine overall drift status
            state = self._determine_drift_status(state)
            
            # Generate visualizations
            state = self._generate_visualizations(state)
            
            # Generate report
            state = self._generate_report(state)
            
            # Save logs
            state = self._save_logs(state)
            
            return state.drift_report
            
        except Exception as e:
            logger.error(f"Error in drift detection: {str(e)}")
            raise
    
    def _detect_data_drift(self, state: DriftState) -> DriftState:
        """Detect drift in input features."""
        logger.info("Detecting data drift...")
        
        drift_detected = False
        feature_drifts = {}
        
        for col in state.baseline_data.columns:
            try:
                baseline_col = state.baseline_data[col].dropna()
                current_col = state.current_data[col].dropna()
                
                if len(baseline_col) == 0 or len(current_col) == 0:
                    continue
                
                # Numerical column: KS test
                if pd.api.types.is_numeric_dtype(state.baseline_data[col]):
                    statistic, p_value = ks_2samp(baseline_col, current_col)
                    drift_detected_col = p_value < self.threshold
                    
                    feature_drifts[col] = {
                        'type': 'numerical',
                        'test': 'KS',
                        'statistic': float(statistic),
                        'p_value': float(p_value),
                        'drift_detected': drift_detected_col,
                        'baseline_mean': float(baseline_col.mean()),
                        'current_mean': float(current_col.mean()),
                        'baseline_std': float(baseline_col.std()),
                        'current_std': float(current_col.std())
                    }
                    
                    if drift_detected_col:
                        drift_detected = True
                
                # Categorical column: Chi-square test
                else:
                    baseline_cat = pd.Categorical(baseline_col)
                    current_cat = pd.Categorical(current_col)
                    
                    crosstab = pd.crosstab(
                        pd.Series(baseline_cat),
                        pd.Series(current_cat)
                    )
                    
                    if crosstab.size > 0:
                        chi2, p_value, dof, expected = chi2_contingency(crosstab)
                        drift_detected_col = p_value < self.threshold
                        
                        feature_drifts[col] = {
                            'type': 'categorical',
                            'test': 'Chi-square',
                            'statistic': float(chi2),
                            'p_value': float(p_value),
                            'drift_detected': drift_detected_col
                        }
                        
                        if drift_detected_col:
                            drift_detected = True
            
            except Exception as e:
                logger.debug(f"Could not test drift for {col}: {e}")
        
        state.data_drift_results = {
            'overall_drift_detected': drift_detected,
            'features_with_drift': [f for f, d in feature_drifts.items() if d.get('drift_detected')],
            'feature_details': feature_drifts
        }
        
        return state
    
    def _detect_prediction_drift(self, state: DriftState) -> DriftState:
        """Detect drift in model predictions."""
        logger.info("Detecting prediction drift...")
        
        # Compare prediction distributions
        statistic, p_value = ks_2samp(
            state.baseline_predictions,
            state.current_predictions
        )
        
        drift_detected = p_value < self.threshold
        
        state.prediction_drift_results = {
            'overall_drift_detected': drift_detected,
            'statistic': float(statistic),
            'p_value': float(p_value),
            'baseline_mean': float(np.mean(state.baseline_predictions)),
            'current_mean': float(np.mean(state.current_predictions)),
            'baseline_std': float(np.std(state.baseline_predictions)),
            'current_std': float(np.std(state.current_predictions)),
            'class_imbalance_change': self._detect_class_imbalance(
                state.baseline_predictions,
                state.current_predictions
            )
        }
        
        return state
    
    def _detect_performance_drift(self, state: DriftState) -> DriftState:
        """Detect drift in model performance."""
        logger.info("Detecting performance drift...")
        
        baseline_acc = accuracy_score(state.baseline_labels, state.baseline_predictions)
        current_acc = accuracy_score(state.current_labels, state.current_predictions)
        performance_drop = baseline_acc - current_acc
        
        metrics = {
            'baseline_accuracy': float(baseline_acc),
            'current_accuracy': float(current_acc),
            'accuracy_drop': float(performance_drop),
            'drift_detected': performance_drop > 0.05  # 5% drop threshold
        }
        
        # F1 score
        try:
            baseline_f1 = f1_score(state.baseline_labels, state.baseline_predictions, average='weighted', zero_division=0)
            current_f1 = f1_score(state.current_labels, state.current_predictions, average='weighted', zero_division=0)
            metrics['baseline_f1'] = float(baseline_f1)
            metrics['current_f1'] = float(current_f1)
            metrics['f1_drop'] = float(baseline_f1 - current_f1)
        except:
            pass
        
        # ROC-AUC (binary classification)
        try:
            if len(np.unique(state.baseline_labels)) == 2:
                baseline_auc = roc_auc_score(state.baseline_labels, state.baseline_predictions)
                current_auc = roc_auc_score(state.current_labels, state.current_predictions)
                metrics['baseline_auc'] = float(baseline_auc)
                metrics['current_auc'] = float(current_auc)
                metrics['auc_drop'] = float(baseline_auc - current_auc)
        except:
            pass
        
        state.performance_drift_results = metrics
        
        return state
    
    def _detect_class_imbalance(self, baseline_preds: np.ndarray,
                               current_preds: np.ndarray) -> Dict:
        """Detect changes in class distribution."""
        baseline_unique, baseline_counts = np.unique(baseline_preds, return_counts=True)
        current_unique, current_counts = np.unique(current_preds, return_counts=True)
        
        baseline_ratios = baseline_counts / len(baseline_preds)
        current_ratios = current_counts / len(current_preds)
        
        return {
            'baseline_distribution': dict(zip(map(int, baseline_unique), map(float, baseline_ratios))),
            'current_distribution': dict(zip(map(int, current_unique), map(float, current_ratios)))
        }
    
    def _determine_drift_status(self, state: DriftState) -> DriftState:
        """Determine overall drift status."""
        
        drifts = []
        
        if state.data_drift_results.get('overall_drift_detected'):
            drifts.append('data')
        
        if state.prediction_drift_results.get('overall_drift_detected'):
            drifts.append('prediction')
        
        if state.performance_drift_results.get('drift_detected'):
            drifts.append('performance')
        
        if len(drifts) >= 2:
            state.overall_drift_status = 'CRITICAL'
        elif len(drifts) == 1:
            state.overall_drift_status = 'WARNING'
        else:
            state.overall_drift_status = 'NO_DRIFT'
        
        return state
    
    def _generate_visualizations(self, state: DriftState) -> DriftState:
        """Generate drift visualization plots."""
        logger.info("Generating drift visualizations...")
        
        plot_dir = self.plots_dir / state.job_id
        plot_dir.mkdir(parents=True, exist_ok=True)
        
        plots_generated = []
        
        # Plot 1: Feature Drift Summary
        try:
            feature_drifts = state.data_drift_results.get('feature_details', {})
            drifted_features = [f for f, d in feature_drifts.items() if d.get('drift_detected')]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            colors = ['red' if f in drifted_features else 'green' for f in feature_drifts.keys()]
            ax.barh(list(feature_drifts.keys()), 
                   [d.get('p_value', 0) for d in feature_drifts.values()],
                   color=colors)
            ax.axvline(self.threshold, color='black', linestyle='--', label=f'Threshold ({self.threshold})')
            ax.set_xlabel('P-value')
            ax.set_title('Feature-wise Data Drift (KS Test)')
            ax.legend()
            
            plot_path = plot_dir / "feature_drift.png"
            plt.savefig(plot_path, dpi=150, bbox_inches="tight")
            plt.close()
            plots_generated.append("feature_drift.png")
        except Exception as e:
            logger.debug(f"Could not generate feature drift plot: {e}")
        
        # Plot 2: Performance Drift
        try:
            metrics = state.performance_drift_results
            if 'baseline_accuracy' in metrics and 'current_accuracy' in metrics:
                fig, ax = plt.subplots(figsize=(8, 6))
                
                categories = ['Accuracy', 'F1-Score', 'ROC-AUC']
                baseline = [
                    metrics.get('baseline_accuracy', 0),
                    metrics.get('baseline_f1', 0),
                    metrics.get('baseline_auc', 0)
                ]
                current = [
                    metrics.get('current_accuracy', 0),
                    metrics.get('current_f1', 0),
                    metrics.get('current_auc', 0)
                ]
                
                x = np.arange(len(categories))
                width = 0.35
                
                ax.bar(x - width/2, baseline, width, label='Baseline', alpha=0.8)
                ax.bar(x + width/2, current, width, label='Current', alpha=0.8)
                
                ax.set_ylabel('Score')
                ax.set_title('Model Performance Drift')
                ax.set_xticks(x)
                ax.set_xticklabels(categories)
                ax.legend()
                ax.set_ylim([0, 1])
                
                plot_path = plot_dir / "performance_drift.png"
                plt.savefig(plot_path, dpi=150, bbox_inches="tight")
                plt.close()
                plots_generated.append("performance_drift.png")
        except Exception as e:
            logger.debug(f"Could not generate performance drift plot: {e}")
        
        return state
    
    def _generate_report(self, state: DriftState) -> DriftState:
        """Generate drift detection report."""
        
        state.drift_report = {
            'job_id': state.job_id,
            'timestamp': pd.Timestamp.now().isoformat(),
            'overall_status': state.overall_drift_status,
            'data_drift': state.data_drift_results,
            'prediction_drift': state.prediction_drift_results,
            'performance_drift': state.performance_drift_results,
            'alert_level': 'CRITICAL' if state.overall_drift_status == 'CRITICAL' else 'WARNING' if state.overall_drift_status == 'WARNING' else 'OK',
            'recommendation': self._get_recommendation(state)
        }
        
        return state
    
    def _get_recommendation(self, state: DriftState) -> str:
        """Get actionable recommendation based on drift."""
        
        if state.overall_drift_status == 'CRITICAL':
            drifted_features = state.data_drift_results.get('features_with_drift', [])
            return f"CRITICAL: Retraining recommended. Drifted features: {', '.join(drifted_features[:3])}"
        elif state.overall_drift_status == 'WARNING':
            return "WARNING: Monitor closely. Consider retraining if drift persists."
        else:
            return "OK: No significant drift detected. Continue monitoring."
    
    def _save_logs(self, state: DriftState) -> DriftState:
        """Save drift detection logs."""
        log_path = self.reports_dir / f"{state.job_id}_drift.json"
        
        with open(log_path, 'w') as f:
            json.dump(state.drift_report, f, indent=2, default=str)
        
        logger.info(f"Saved drift report to {log_path}")
        
        return state
    
    def get_drift_report(self, job_id: str) -> Dict:
        """Get drift detection report for a job."""
        log_path = self.reports_dir / f"{job_id}_drift.json"
        
        if not log_path.exists():
            return {"error": f"No drift report found for job {job_id}"}
        
        with open(log_path, 'r') as f:
            return json.load(f)


def build_drift_detection_workflow():
    """Build drift detection workflow for LangGraph integration."""
    return DriftDetector()
