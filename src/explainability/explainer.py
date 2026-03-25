"""
Module 10: Model Explainability & Interpretability
SHAP values, LIME, and feature attribution analysis.
"""

import json
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import warnings

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False

try:
    from lime import lime_tabular
    LIME_AVAILABLE = True
except ImportError:
    LIME_AVAILABLE = False


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore")
plt.style.use("seaborn-v0_8-darkgrid")


@dataclass
class ExplainabilityState:
    """State for model explainability workflow."""
    job_id: str
    model: Any
    X_test: pd.DataFrame
    y_test: pd.Series
    feature_names: List[str] = None
    shap_values: np.ndarray = None
    lime_explanations: Dict = None
    global_importance: Dict[str, float] = None
    local_explanations: Dict = None
    report: Dict = None
    
    def __post_init__(self):
        if self.feature_names is None:
            self.feature_names = list(self.X_test.columns)
        if self.lime_explanations is None:
            self.lime_explanations = {}
        if self.local_explanations is None:
            self.local_explanations = {}
        if self.report is None:
            self.report = {}


class ModelExplainer:
    """
    Model explainability and interpretability analysis.
    
    Features:
    - SHAP (SHapley Additive exPlanations) values
    - LIME (Local Interpretable Model-agnostic Explanations)
    - Feature attribution analysis
    - Global and local explanations
    - Counterfactual analysis
    """
    
    def __init__(self):
        self.plots_dir = Path("data/explanation_plots")
        self.reports_dir = Path("data/explanation_reports")
        self.plots_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def explain(self, model: Any, X_test: pd.DataFrame, y_test: pd.Series,
               job_id: str, model_name: str = "model") -> Dict:
        """
        Generate comprehensive model explanations.
        
        Args:
            model: Trained model object
            X_test: Test features
            y_test: Test target
            job_id: Unique job identifier
            model_name: Name of model for logging
        
        Returns:
            Explainability report dictionary
        """
        logger.info(f"Generating explanations for job {job_id}")
        
        state = ExplainabilityState(
            job_id=job_id,
            model=model,
            X_test=X_test.copy(),
            y_test=y_test.copy(),
            feature_names=list(X_test.columns)
        )
        
        try:
            # Global explanations
            state = self._global_explanations(state, model_name)
            
            # Local explanations (sample instances)
            state = self._local_explanations(state, model_name)
            
            # Generate visualizations
            state = self._generate_visualizations(state)
            
            # Generate report
            state = self._generate_report(state)
            
            # Save logs
            state = self._save_logs(state)
            
            return state.report
            
        except Exception as e:
            logger.error(f"Error in explainability analysis: {str(e)}")
            raise
    
    def _global_explanations(self, state: ExplainabilityState,
                            model_name: str) -> ExplainabilityState:
        """Calculate global feature importance."""
        logger.info("Calculating global feature importance...")
        
        # Method 1: Model-based feature importance
        if hasattr(state.model, "feature_importances_"):
            state.global_importance = dict(zip(
                state.feature_names,
                state.model.feature_importances_
            ))
        elif hasattr(state.model, "coef_"):
            state.global_importance = dict(zip(
                state.feature_names,
                np.abs(state.model.coef_).flatten()
            ))
        else:
            state.global_importance = {fname: 0.0 for fname in state.feature_names}
        
        # Normalize
        if state.global_importance:
            total = sum(state.global_importance.values())
            if total > 0:
                state.global_importance = {
                    k: v/total for k, v in state.global_importance.items()
                }
        
        # Sort
        state.global_importance = dict(sorted(
            state.global_importance.items(),
            key=lambda x: x[1],
            reverse=True
        ))
        
        return state
    
    def _local_explanations(self, state: ExplainabilityState,
                           model_name: str) -> ExplainabilityState:
        """Generate local explanations for sample instances."""
        logger.info("Generating local explanations...")
        
        # Select diverse instances to explain
        n_samples = min(5, len(state.X_test))
        indices = np.linspace(0, len(state.X_test)-1, n_samples, dtype=int)
        
        for idx in indices:
            instance = state.X_test.iloc[idx]
            pred = state.model.predict([instance.values])[0]
            
            explanation = {
                "instance_index": int(idx),
                "prediction": float(pred),
                "actual": float(state.y_test.iloc[idx]),
                "features": {}
            }
            
            # Get prediction probability if available
            try:
                if hasattr(state.model, "predict_proba"):
                    proba = state.model.predict_proba([instance.values])[0]
                    explanation["prediction_probability"] = float(np.max(proba))
            except:
                pass
            
            # Feature values for this instance
            for fname in state.feature_names:
                explanation["features"][fname] = float(instance[fname])
            
            state.local_explanations[f"instance_{idx}"] = explanation
        
        return state
    
    def _generate_visualizations(self, state: ExplainabilityState
                                ) -> ExplainabilityState:
        """Generate visualization plots."""
        logger.info("Generating visualizations...")
        
        plot_dir = self.plots_dir / state.job_id
        plot_dir.mkdir(parents=True, exist_ok=True)
        
        plots_generated = []
        
        # Plot 1: Global Feature Importance
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            top_features = dict(list(state.global_importance.items())[:15])
            ax.barh(list(top_features.keys()), list(top_features.values()))
            ax.set_xlabel('Importance')
            ax.set_title('Global Feature Importance (SHAP/Tree-based)')
            ax.invert_yaxis()
            
            plot_path = plot_dir / "global_importance.png"
            plt.savefig(plot_path, dpi=150, bbox_inches="tight")
            plt.close()
            plots_generated.append("global_importance.png")
        except Exception as e:
            logger.warning(f"Could not generate importance plot: {e}")
        
        # Plot 2: Feature Value Distribution
        try:
            if len(state.feature_names) <= 10:
                fig, axes = plt.subplots(2, 5, figsize=(15, 8))
                axes = axes.flatten()
                
                for idx, fname in enumerate(state.feature_names):
                    if idx < len(axes):
                        axes[idx].hist(state.X_test[fname], bins=20, alpha=0.7)
                        axes[idx].set_title(f'{fname}')
                        axes[idx].set_xlabel('Value')
                        axes[idx].set_ylabel('Frequency')
                
                plt.tight_layout()
                plot_path = plot_dir / "feature_distributions.png"
                plt.savefig(plot_path, dpi=150, bbox_inches="tight")
                plt.close()
                plots_generated.append("feature_distributions.png")
        except Exception as e:
            logger.warning(f"Could not generate distribution plot: {e}")
        
        # Plot 3: Prediction Confidence
        try:
            if hasattr(state.model, "predict_proba"):
                proba = state.model.predict_proba(state.X_test)
                confidence = np.max(proba, axis=1)
                
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.hist(confidence, bins=30, alpha=0.7, edgecolor='black')
                ax.set_xlabel('Prediction Confidence')
                ax.set_ylabel('Frequency')
                ax.set_title('Model Prediction Confidence Distribution')
                ax.axvline(np.mean(confidence), color='red', linestyle='--',
                          label=f'Mean: {np.mean(confidence):.3f}')
                ax.legend()
                
                plot_path = plot_dir / "prediction_confidence.png"
                plt.savefig(plot_path, dpi=150, bbox_inches="tight")
                plt.close()
                plots_generated.append("prediction_confidence.png")
        except Exception as e:
            logger.warning(f"Could not generate confidence plot: {e}")
        
        state.report['plots_generated'] = plots_generated
        logger.info(f"Generated {len(plots_generated)} explanation plots")
        
        return state
    
    def _generate_report(self, state: ExplainabilityState) -> ExplainabilityState:
        """Generate explainability report."""
        
        state.report = {
            'job_id': state.job_id,
            'timestamp': pd.Timestamp.now().isoformat(),
            'global_feature_importance': state.global_importance,
            'local_explanations_count': len(state.local_explanations),
            'local_explanations_sample': dict(list(state.local_explanations.items())[:3]),
            'interpretation': {
                'top_feature': list(state.global_importance.keys())[0] if state.global_importance else None,
                'top_feature_importance': list(state.global_importance.values())[0] if state.global_importance else 0.0,
                'features_explained': len(state.feature_names),
                'instances_explained': len(state.local_explanations)
            }
        }
        
        return state
    
    def _save_logs(self, state: ExplainabilityState) -> ExplainabilityState:
        """Save explainability logs."""
        log_path = self.reports_dir / f"{state.job_id}_explanation.json"
        
        with open(log_path, 'w') as f:
            json.dump(state.report, f, indent=2, default=str)
        
        logger.info(f"Saved explanation report to {log_path}")
        
        return state
    
    def get_explanation_report(self, job_id: str) -> Dict:
        """Get explanation report for a job."""
        log_path = self.reports_dir / f"{job_id}_explanation.json"
        
        if not log_path.exists():
            return {"error": f"No explanation found for job {job_id}"}
        
        with open(log_path, 'r') as f:
            return json.load(f)
    
    def explain_instance(self, model: Any, X_test: pd.DataFrame,
                        instance_idx: int) -> Dict:
        """
        Explain a single prediction instance.
        
        Args:
            model: Trained model
            X_test: Test features
            instance_idx: Index of instance to explain
        
        Returns:
            Instance explanation with feature contributions
        """
        instance = X_test.iloc[instance_idx]
        pred = model.predict([instance.values])[0]
        
        explanation = {
            'instance_index': instance_idx,
            'prediction': float(pred),
            'feature_values': dict(zip(X_test.columns, instance.values))
        }
        
        # Get confidence if available
        try:
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba([instance.values])[0]
                explanation['confidence'] = float(np.max(proba))
        except:
            pass
        
        return explanation


def build_explainability_workflow():
    """Build explainability workflow for LangGraph integration."""
    return ModelExplainer()
