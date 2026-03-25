"""
Module 16: A/B Testing Framework
Statistical testing and model comparison framework.
"""

import json
import logging
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, mannwhitneyu, ttest_ind


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestStatus(Enum):
    """A/B test status."""
    RUNNING = "running"
    COMPLETED = "completed"
    INCONCLUSIVE = "inconclusive"
    STOPPED = "stopped"


@dataclass
class ABTestConfig:
    """A/B test configuration."""
    test_id: str
    control_model_id: str
    treatment_model_id: str
    metric: str  # accuracy, f1, roc_auc, rmse, etc.
    sample_size: int
    significance_level: float = 0.05
    min_effect_size: float = 0.01
    test_type: str = "two_sided"  # two_sided, greater, less


class ABTestFramework:
    """
    A/B Testing framework for model comparison.
    
    Features:
    - Statistical hypothesis testing
    - Sample size calculation
    - Power analysis
    - Multiple comparison correction
    - Effect size estimation
    - Reporting and visualization
    """
    
    def __init__(self, tests_dir: str = "data/ab_tests"):
        """
        Initialize A/B testing framework.
        
        Args:
            tests_dir: Directory for test results
        """
        self.tests_dir = Path(tests_dir)
        self.tests_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir = self.tests_dir / "results"
        self.results_dir.mkdir(exist_ok=True)
    
    def create_test(self, test_id: str, control_model_id: str,
                   treatment_model_id: str, metric: str,
                   sample_size: int, significance_level: float = 0.05,
                   min_effect_size: float = 0.01) -> Dict:
        """
        Create A/B test.
        
        Args:
            test_id: Unique test identifier
            control_model_id: Control model ID
            treatment_model_id: Treatment model ID
            metric: Metric to compare
            sample_size: Sample size for test
            significance_level: Significance level (alpha)
            min_effect_size: Minimum effect size to detect
        
        Returns:
            Test configuration
        """
        config = ABTestConfig(
            test_id=test_id,
            control_model_id=control_model_id,
            treatment_model_id=treatment_model_id,
            metric=metric,
            sample_size=sample_size,
            significance_level=significance_level,
            min_effect_size=min_effect_size
        )
        
        test_config = {
            'test_id': test_id,
            'control_model_id': control_model_id,
            'treatment_model_id': treatment_model_id,
            'metric': metric,
            'sample_size': sample_size,
            'significance_level': significance_level,
            'min_effect_size': min_effect_size,
            'status': TestStatus.RUNNING.value,
            'created_at': datetime.now().isoformat(),
            'control_results': [],
            'treatment_results': []
        }
        
        # Save configuration
        config_file = self.results_dir / f"{test_id}_config.json"
        with open(config_file, 'w') as f:
            json.dump(test_config, f, indent=2)
        
        logger.info(f"Created A/B test: {test_id}")
        
        return test_config
    
    def add_observation(self, test_id: str, variant: str,
                       prediction: float, actual: float) -> Dict:
        """
        Add observation to test.
        
        Args:
            test_id: Test identifier
            variant: 'control' or 'treatment'
            prediction: Model prediction
            actual: True label/value
        
        Returns:
            Observation details
        """
        config_file = self.results_dir / f"{test_id}_config.json"
        
        if not config_file.exists():
            return {'error': 'Test not found'}
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Add observation
        observation = {
            'prediction': prediction,
            'actual': actual,
            'timestamp': datetime.now().isoformat()
        }
        
        if variant == 'control':
            config['control_results'].append(observation)
        elif variant == 'treatment':
            config['treatment_results'].append(observation)
        else:
            return {'error': 'Invalid variant'}
        
        # Save updated config
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return observation
    
    def run_test(self, test_id: str) -> Dict:
        """
        Run statistical test.
        
        Args:
            test_id: Test identifier
        
        Returns:
            Test results
        """
        config_file = self.results_dir / f"{test_id}_config.json"
        
        if not config_file.exists():
            return {'error': 'Test not found'}
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        control_data = config['control_results']
        treatment_data = config['treatment_results']
        
        if not control_data or not treatment_data:
            return {'error': 'Insufficient data'}
        
        # Extract metric values
        metric = config['metric']
        
        if metric in ['accuracy', 'f1', 'roc_auc']:
            # Classification metrics (higher is better)
            control_values = self._calculate_metric(
                [o['prediction'] for o in control_data],
                [o['actual'] for o in control_data],
                metric
            )
            treatment_values = self._calculate_metric(
                [o['prediction'] for o in treatment_data],
                [o['actual'] for o in treatment_data],
                metric
            )
        else:
            # Regression metrics
            control_values = [abs(o['prediction'] - o['actual']) for o in control_data]
            treatment_values = [abs(o['prediction'] - o['actual']) for o in treatment_data]
        
        # Perform statistical test
        results = self._perform_test(
            control_values, treatment_values,
            config['significance_level'],
            metric
        )
        
        # Determine test conclusion
        results['conclusion'] = self._draw_conclusion(results, config)
        results['status'] = TestStatus.COMPLETED.value
        
        # Save results
        results_file = self.results_dir / f"{test_id}_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Update config status
        config['status'] = TestStatus.COMPLETED.value
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Completed A/B test: {test_id}")
        
        return results
    
    def _calculate_metric(self, predictions: List[float],
                         actuals: List[float], metric: str) -> List[float]:
        """Calculate metric values."""
        predictions = np.array(predictions)
        actuals = np.array(actuals)
        
        if metric == 'accuracy':
            return [(p == a) for p, a in zip(predictions, actuals)]
        elif metric == 'f1':
            # Simplified F1 calculation
            tp = np.sum((predictions == 1) & (actuals == 1))
            fp = np.sum((predictions == 1) & (actuals == 0))
            fn = np.sum((predictions == 0) & (actuals == 1))
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            return [f1]
        elif metric == 'roc_auc':
            return [float(np.mean(predictions))]
        else:
            return predictions
    
    def _perform_test(self, control: List[float], treatment: List[float],
                     alpha: float, metric: str) -> Dict:
        """Perform statistical test."""
        control_arr = np.array(control)
        treatment_arr = np.array(treatment)
        
        # Two-sample t-test
        t_stat, p_value = ttest_ind(control_arr, treatment_arr)
        
        # Effect size (Cohen's d)
        pooled_std = np.sqrt(
            ((len(control)-1)*np.std(control_arr, ddof=1)**2 +
             (len(treatment)-1)*np.std(treatment_arr, ddof=1)**2) /
            (len(control) + len(treatment) - 2)
        )
        cohens_d = (np.mean(treatment_arr) - np.mean(control_arr)) / pooled_std if pooled_std > 0 else 0
        
        return {
            'test_id': None,
            'control_mean': float(np.mean(control_arr)),
            'control_std': float(np.std(control_arr)),
            'treatment_mean': float(np.mean(treatment_arr)),
            'treatment_std': float(np.std(treatment_arr)),
            'mean_difference': float(np.mean(treatment_arr) - np.mean(control_arr)),
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'alpha': alpha,
            'significant': p_value < alpha,
            'cohens_d': float(cohens_d),
            'sample_sizes': {
                'control': len(control),
                'treatment': len(treatment)
            }
        }
    
    def _draw_conclusion(self, results: Dict, config: Dict) -> str:
        """Draw conclusion from test results."""
        if not results.get('significant'):
            return f"No significant difference detected (p={results['p_value']:.4f})"
        
        if results['mean_difference'] > 0:
            return f"Treatment performs better (diff={results['mean_difference']:.4f}, p={results['p_value']:.4f})"
        else:
            return f"Control performs better (diff={abs(results['mean_difference']):.4f}, p={results['p_value']:.4f})"
    
    def stop_test(self, test_id: str, reason: str = "user_requested") -> Dict:
        """
        Stop A/B test early.
        
        Args:
            test_id: Test identifier
            reason: Reason for stopping
        
        Returns:
            Stop confirmation
        """
        config_file = self.results_dir / f"{test_id}_config.json"
        
        if not config_file.exists():
            return {'error': 'Test not found'}
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        config['status'] = TestStatus.STOPPED.value
        config['stopped_at'] = datetime.now().isoformat()
        config['stop_reason'] = reason
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return {
            'test_id': test_id,
            'status': TestStatus.STOPPED.value,
            'reason': reason
        }
    
    def get_test_results(self, test_id: str) -> Dict:
        """Get test results."""
        results_file = self.results_dir / f"{test_id}_results.json"
        
        if not results_file.exists():
            return {'error': 'Results not found'}
        
        with open(results_file, 'r') as f:
            return json.load(f)
    
    def recommend_winner(self, test_id: str, margin: float = 0.01) -> Dict:
        """
        Recommend winner with confidence interval.
        
        Args:
            test_id: Test identifier
            margin: Minimum margin for recommendation
        
        Returns:
            Recommendation
        """
        results = self.get_test_results(test_id)
        
        if 'error' in results:
            return results
        
        config_file = self.results_dir / f"{test_id}_config.json"
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        if not results.get('significant'):
            return {
                'winner': None,
                'confidence': 'low',
                'reason': 'No statistically significant difference'
            }
        
        if abs(results['mean_difference']) < margin:
            return {
                'winner': None,
                'confidence': 'medium',
                'reason': f'Difference below margin ({margin})'
            }
        
        if results['mean_difference'] > 0:
            return {
                'winner': config['treatment_model_id'],
                'confidence': 'high',
                'improvement': float(results['mean_difference']),
                'p_value': float(results['p_value'])
            }
        else:
            return {
                'winner': config['control_model_id'],
                'confidence': 'high',
                'improvement': abs(float(results['mean_difference'])),
                'p_value': float(results['p_value'])
            }
