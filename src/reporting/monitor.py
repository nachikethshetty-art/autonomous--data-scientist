"""
Module 13: Production Performance Monitoring
Track model performance metrics in production environments.
"""

import json
import logging
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
plt.style.use("seaborn-v0_8-darkgrid")


@dataclass
class MonitoringState:
    """State for performance monitoring workflow."""
    job_id: str
    predictions: np.ndarray
    actuals: Optional[np.ndarray] = None
    timestamps: List[datetime] = field(default_factory=list)
    problem_type: str = "classification"
    monitoring_results: Dict = field(default_factory=dict)
    alerts: List[Dict] = field(default_factory=list)
    report: Dict = field(default_factory=dict)


class PerformanceMonitor:
    """
    Production performance monitoring.
    
    Features:
    - Real-time metric calculation
    - Sliding window metrics
    - Anomaly detection
    - Automated alerting
    - Performance trend analysis
    - SLA tracking
    """
    
    def __init__(self, window_size: int = 100, alert_threshold: float = 0.05):
        """
        Initialize performance monitor.
        
        Args:
            window_size: Sliding window size for metrics
            alert_threshold: Performance degradation threshold for alerts
        """
        self.window_size = window_size
        self.alert_threshold = alert_threshold
        
        self.monitoring_dir = Path("data/monitoring")
        self.monitoring_dir.mkdir(parents=True, exist_ok=True)
        
        self.alerts_dir = self.monitoring_dir / "alerts"
        self.alerts_dir.mkdir(parents=True, exist_ok=True)
    
    def monitor(self, predictions: np.ndarray, job_id: str,
               actuals: Optional[np.ndarray] = None,
               problem_type: str = "classification",
               timestamps: Optional[List[datetime]] = None) -> Dict:
        """
        Monitor model performance.
        
        Args:
            predictions: Model predictions
            job_id: Unique job identifier
            actuals: True labels/values (optional)
            problem_type: "classification" or "regression"
            timestamps: Prediction timestamps
        
        Returns:
            Monitoring report with metrics and alerts
        """
        logger.info(f"Starting performance monitoring for job {job_id}")
        
        if timestamps is None:
            timestamps = [datetime.now() - timedelta(seconds=i) for i in range(len(predictions))]
        
        state = MonitoringState(
            job_id=job_id,
            predictions=predictions,
            actuals=actuals,
            timestamps=timestamps,
            problem_type=problem_type
        )
        
        try:
            # Calculate metrics
            state = self._calculate_metrics(state)
            
            # Detect anomalies
            state = self._detect_anomalies(state)
            
            # Generate alerts
            state = self._generate_alerts(state)
            
            # Generate visualizations
            state = self._generate_visualizations(state)
            
            # Generate report
            state = self._generate_report(state)
            
            # Save logs
            state = self._save_logs(state)
            
            return state.report
            
        except Exception as e:
            logger.error(f"Error in performance monitoring: {str(e)}")
            raise
    
    def _calculate_metrics(self, state: MonitoringState) -> MonitoringState:
        """Calculate performance metrics."""
        logger.info("Calculating performance metrics...")
        
        metrics = {
            'total_predictions': len(state.predictions),
            'timestamp_range': {
                'start': min(state.timestamps).isoformat(),
                'end': max(state.timestamps).isoformat()
            }
        }
        
        # Classification metrics
        if state.problem_type == "classification" and state.actuals is not None:
            accuracy = np.mean(state.predictions == state.actuals)
            metrics['accuracy'] = float(accuracy)
            
            # Per-class metrics
            classes = np.unique(state.actuals)
            class_metrics = {}
            
            for cls in classes:
                mask = state.actuals == cls
                if np.sum(mask) > 0:
                    class_accuracy = np.mean(state.predictions[mask] == state.actuals[mask])
                    class_metrics[str(cls)] = {
                        'accuracy': float(class_accuracy),
                        'samples': int(np.sum(mask))
                    }
            
            metrics['per_class_metrics'] = class_metrics
            
            # Confusion matrix elements
            tp = np.sum((state.predictions == 1) & (state.actuals == 1)) if len(classes) == 2 else 0
            fp = np.sum((state.predictions == 1) & (state.actuals == 0)) if len(classes) == 2 else 0
            fn = np.sum((state.predictions == 0) & (state.actuals == 1)) if len(classes) == 2 else 0
            
            if tp + fp > 0:
                metrics['precision'] = float(tp / (tp + fp))
            if tp + fn > 0:
                metrics['recall'] = float(tp / (tp + fn))
        
        # Prediction distribution
        pred_dist = {}
        for cls in np.unique(state.predictions):
            count = np.sum(state.predictions == cls)
            pred_dist[str(cls)] = {
                'count': int(count),
                'percentage': float(count / len(state.predictions) * 100)
            }
        
        metrics['prediction_distribution'] = pred_dist
        
        # Sliding window metrics
        window_metrics = self._calculate_window_metrics(state)
        metrics['sliding_window_metrics'] = window_metrics
        
        state.monitoring_results = metrics
        
        return state
    
    def _calculate_window_metrics(self, state: MonitoringState) -> Dict:
        """Calculate metrics for sliding windows."""
        
        window_metrics = {
            'windows': []
        }
        
        for i in range(0, len(state.predictions), self.window_size // 2):
            end_idx = min(i + self.window_size, len(state.predictions))
            
            if end_idx - i < self.window_size // 2:
                continue
            
            window_preds = state.predictions[i:end_idx]
            window_actuals = state.actuals[i:end_idx] if state.actuals is not None else None
            window_time = state.timestamps[i:end_idx]
            
            window_metric = {
                'window_index': i // (self.window_size // 2),
                'start_time': window_time[0].isoformat(),
                'end_time': window_time[-1].isoformat(),
                'sample_count': len(window_preds)
            }
            
            if window_actuals is not None:
                accuracy = np.mean(window_preds == window_actuals)
                window_metric['accuracy'] = float(accuracy)
            
            window_metrics['windows'].append(window_metric)
        
        return window_metrics
    
    def _detect_anomalies(self, state: MonitoringState) -> MonitoringState:
        """Detect anomalies in predictions."""
        logger.info("Detecting anomalies...")
        
        anomalies = []
        
        # Check for sudden class distribution changes
        if len(state.predictions) >= self.window_size:
            early_window = state.predictions[:self.window_size].astype(int)
            late_window = state.predictions[-self.window_size:].astype(int)
            
            early_dist = np.bincount(early_window) / len(early_window)
            late_dist = np.bincount(late_window, minlength=len(early_dist)) / len(late_window)
            
            # JS divergence as anomaly metric
            kl_div = np.sum(early_dist * np.log(early_dist / (late_dist + 1e-10) + 1e-10))
            
            if kl_div > 0.5:  # Significant change
                anomalies.append({
                    'type': 'class_distribution_shift',
                    'severity': 'high' if kl_div > 1.0 else 'medium',
                    'divergence': float(kl_div)
                })
        
        # Check for prediction confidence anomalies (if predictions are probabilities)
        if state.predictions.dtype in [np.float32, np.float64]:
            if len(state.predictions) >= 10:
                confidence_mean = np.mean(state.predictions)
                confidence_std = np.std(state.predictions)
                
                # Flag low confidence predictions
                low_confidence = np.sum(state.predictions < 0.6)
                if low_confidence / len(state.predictions) > 0.3:
                    anomalies.append({
                        'type': 'low_confidence_predictions',
                        'percentage': float(low_confidence / len(state.predictions) * 100),
                        'severity': 'medium'
                    })
        
        # Check for prediction latency anomalies
        if len(state.timestamps) > 1:
            time_diffs = np.diff([t.timestamp() for t in state.timestamps])
            median_latency = np.median(time_diffs)
            high_latency = np.sum(time_diffs > median_latency * 3)
            
            if high_latency > len(time_diffs) * 0.1:
                anomalies.append({
                    'type': 'high_prediction_latency',
                    'percentage': float(high_latency / len(time_diffs) * 100),
                    'severity': 'medium'
                })
        
        state.monitoring_results['anomalies'] = anomalies
        
        return state
    
    def _generate_alerts(self, state: MonitoringState) -> MonitoringState:
        """Generate alerts based on metrics and anomalies."""
        logger.info("Generating alerts...")
        
        alerts = []
        
        # Alert if accuracy dropped
        if 'accuracy' in state.monitoring_results and state.monitoring_results['accuracy'] < 0.7:
            alerts.append({
                'type': 'LOW_ACCURACY',
                'severity': 'CRITICAL' if state.monitoring_results['accuracy'] < 0.5 else 'WARNING',
                'message': f"Accuracy dropped to {state.monitoring_results['accuracy']:.2%}",
                'threshold': 0.7,
                'current_value': state.monitoring_results['accuracy']
            })
        
        # Alert if anomalies detected
        for anomaly in state.monitoring_results.get('anomalies', []):
            alerts.append({
                'type': 'ANOMALY_DETECTED',
                'severity': anomaly.get('severity', 'WARNING').upper(),
                'message': f"{anomaly['type']}: {anomaly}",
                'anomaly_details': anomaly
            })
        
        # Alert if class imbalance changed significantly
        if state.actuals is not None:
            actual_dist = np.bincount(state.actuals.astype(int))
            pred_dist = np.bincount(state.predictions.astype(int))
            
            # Normalize to same length
            max_len = max(len(actual_dist), len(pred_dist))
            actual_dist_norm = np.pad(actual_dist, (0, max_len - len(actual_dist)), 'constant') / len(state.actuals)
            pred_dist_norm = np.pad(pred_dist, (0, max_len - len(pred_dist)), 'constant') / len(state.predictions)
            
            distribution_diff = np.sum(np.abs(actual_dist_norm - pred_dist_norm))
            
            if distribution_diff > 0.2:
                alerts.append({
                    'type': 'CLASS_IMBALANCE_SHIFT',
                    'severity': 'WARNING',
                    'message': f"Significant shift in class distribution (diff: {distribution_diff:.2%})",
                    'distribution_diff': float(distribution_diff)
                })
        
        state.alerts = alerts
        
        return state
    
    def _generate_visualizations(self, state: MonitoringState) -> MonitoringState:
        """Generate monitoring visualizations."""
        logger.info("Generating monitoring visualizations...")
        
        plot_dir = self.monitoring_dir / state.job_id
        plot_dir.mkdir(parents=True, exist_ok=True)
        
        # Plot 1: Prediction distribution
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            pred_dist = state.monitoring_results.get('prediction_distribution', {})
            
            classes = list(pred_dist.keys())
            counts = [pred_dist[c]['count'] for c in classes]
            
            ax.bar(classes, counts, alpha=0.7, color='steelblue')
            ax.set_xlabel('Predicted Class')
            ax.set_ylabel('Count')
            ax.set_title('Prediction Distribution')
            
            plot_path = plot_dir / "prediction_distribution.png"
            plt.savefig(plot_path, dpi=150, bbox_inches="tight")
            plt.close()
        except Exception as e:
            logger.debug(f"Could not generate prediction distribution plot: {e}")
        
        # Plot 2: Sliding window accuracy
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            windows = state.monitoring_results.get('sliding_window_metrics', {}).get('windows', [])
            
            if windows:
                window_indices = [w['window_index'] for w in windows if 'accuracy' in w]
                accuracies = [w['accuracy'] for w in windows if 'accuracy' in w]
                
                if window_indices and accuracies:
                    ax.plot(window_indices, accuracies, marker='o', linestyle='-', linewidth=2)
                    ax.axhline(y=0.8, color='g', linestyle='--', label='Target (80%)')
                    ax.set_xlabel('Window Index')
                    ax.set_ylabel('Accuracy')
                    ax.set_title('Sliding Window Accuracy Over Time')
                    ax.legend()
                    ax.grid(True, alpha=0.3)
                    
                    plot_path = plot_dir / "sliding_window_accuracy.png"
                    plt.savefig(plot_path, dpi=150, bbox_inches="tight")
                    plt.close()
        except Exception as e:
            logger.debug(f"Could not generate sliding window plot: {e}")
        
        return state
    
    def _generate_report(self, state: MonitoringState) -> MonitoringState:
        """Generate monitoring report."""
        
        # Determine alert level first
        alert_level = 'CRITICAL' if any(a['severity'] == 'CRITICAL' for a in state.alerts) else \
                      'WARNING' if any(a['severity'] == 'WARNING' for a in state.alerts) else 'OK'
        
        state.report = {
            'job_id': state.job_id,
            'timestamp': datetime.now().isoformat(),
            'total_predictions': state.monitoring_results.get('total_predictions'),
            'accuracy': state.monitoring_results.get('accuracy'),
            'precision': state.monitoring_results.get('precision'),
            'recall': state.monitoring_results.get('recall'),
            'alerts': state.alerts,
            'alert_count': len(state.alerts),
            'alert_level': alert_level,
            'recommendation': self._get_recommendation(state, alert_level),
            'monitoring_results': state.monitoring_results
        }
        
        return state
    
    def _get_recommendation(self, state: MonitoringState, alert_level: str) -> str:
        """Get actionable recommendation."""
        
        if alert_level == 'CRITICAL':
            return "CRITICAL: Immediate action required. Review model predictions and consider retraining."
        elif alert_level == 'WARNING':
            return "WARNING: Monitor closely. Check for data drift and model performance degradation."
        else:
            return "OK: Model performing as expected. Continue routine monitoring."
    
    def _save_logs(self, state: MonitoringState) -> MonitoringState:
        """Save monitoring logs."""
        
        log_path = self.monitoring_dir / f"{state.job_id}_monitoring.json"
        
        with open(log_path, 'w') as f:
            json.dump(state.report, f, indent=2, default=str)
        
        # Save alerts separately
        if state.alerts:
            alerts_path = self.alerts_dir / f"{state.job_id}_alerts.json"
            with open(alerts_path, 'w') as f:
                json.dump(state.alerts, f, indent=2, default=str)
        
        logger.info(f"Saved monitoring report to {log_path}")
        
        return state
    
    def get_monitoring_report(self, job_id: str) -> Dict:
        """Retrieve monitoring report."""
        log_path = self.monitoring_dir / f"{job_id}_monitoring.json"
        
        if not log_path.exists():
            return {"error": f"No monitoring report found for job {job_id}"}
        
        with open(log_path, 'r') as f:
            return json.load(f)
    
    def get_alerts(self, job_id: str) -> List[Dict]:
        """Get all alerts for a job."""
        alerts_path = self.alerts_dir / f"{job_id}_alerts.json"
        
        if not alerts_path.exists():
            return []
        
        with open(alerts_path, 'r') as f:
            return json.load(f)
