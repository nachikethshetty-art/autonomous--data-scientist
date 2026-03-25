"""
Module 7: Feature Engineering Agent
Automated feature generation, transformation, and selection.
"""

import json
import logging
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Set, Tuple, Optional
import warnings

import pandas as pd
import numpy as np
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif, f_regression, RFE
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from scipy.stats import pearsonr, spearmanr


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FeatureEngineeringState:
    """State for feature engineering workflow."""
    job_id: str
    df: pd.DataFrame
    schema: Dict
    metadata: Dict
    problem_type: str  # "classification" or "regression"
    target_column: Optional[str] = None
    engineered_features: List[str] = None
    feature_importance: Dict[str, float] = None
    selected_features: List[str] = None
    transformation_log: Dict = None
    
    def __post_init__(self):
        if self.engineered_features is None:
            self.engineered_features = []
        if self.feature_importance is None:
            self.feature_importance = {}
        if self.selected_features is None:
            self.selected_features = []
        if self.transformation_log is None:
            self.transformation_log = {}


class FeatureEngineeringAgent:
    """
    Automated feature engineering pipeline.
    
    Features:
    - Polynomial features (degree 2, 3)
    - Interaction terms
    - Domain-specific features (dates, text length, etc.)
    - Feature selection (univariate, tree-based, recursive)
    - Correlation analysis
    - Feature importance ranking
    """
    
    def __init__(self):
        self.logs_dir = Path("data/feature_logs")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.selector = None
        self.scaler = StandardScaler()
        self.feature_names = []
        
    def engineer(self, df: pd.DataFrame, schema: Dict, metadata: Dict, 
                job_id: str, problem_type: str, target_column: Optional[str] = None,
                strategy: str = "smart") -> Tuple[pd.DataFrame, Dict]:
        """
        Execute full feature engineering pipeline.
        
        Args:
            df: Input dataframe
            schema: Column schema
            metadata: Job metadata
            job_id: Unique job identifier
            problem_type: "classification" or "regression"
            target_column: Target column name (required for feature importance)
            strategy: "smart" (balanced), "aggressive" (many features), "conservative" (few features)
        
        Returns:
            Tuple of (engineered_dataframe, transformation_log)
        """
        logger.info(f"Starting feature engineering for job {job_id} (strategy={strategy})")
        
        state = FeatureEngineeringState(
            job_id=job_id,
            df=df.copy(),
            schema=schema,
            metadata=metadata,
            problem_type=problem_type,
            target_column=target_column
        )
        
        try:
            # 1. Generate polynomial features
            state = self._generate_polynomial_features(state, strategy)
            logger.info(f"Generated {len(state.engineered_features)} features from polynomials")
            
            # 2. Generate interaction terms
            state = self._generate_interactions(state, strategy)
            logger.info(f"Generated interactions, total features now: {len(state.engineered_features)}")
            
            # 3. Generate domain-specific features
            state = self._generate_domain_features(state, strategy)
            logger.info(f"Generated domain features, total: {len(state.engineered_features)}")
            
            # 4. Calculate feature importance
            if target_column and target_column in state.df.columns:
                state = self._calculate_feature_importance(state, target_column)
                logger.info(f"Calculated importance for {len(state.feature_importance)} features")
            
            # 5. Select features
            state = self._select_features(state, target_column, strategy)
            logger.info(f"Selected {len(state.selected_features)} features")
            
            # 6. Save transformation log
            state = self._save_logs(state)
            
            return state.df, state.transformation_log
            
        except Exception as e:
            logger.error(f"Error in feature engineering: {str(e)}")
            raise
    
    def _generate_polynomial_features(self, state: FeatureEngineeringState, 
                                     strategy: str) -> FeatureEngineeringState:
        """Generate polynomial features for numeric columns."""
        numeric_cols = [col for col in state.df.columns 
                       if state.schema.get(col, {}).get("type") in ["numeric", "int64", "float64"]]
        
        # Determine degree based on strategy
        max_degree = 3 if strategy == "aggressive" else (2 if strategy == "smart" else 1)
        
        new_features = []
        
        for degree in range(2, max_degree + 1):
            if numeric_cols:
                poly = PolynomialFeatures(degree=degree, include_bias=False)
                
                # Use subset if aggressive
                cols_to_use = numeric_cols if strategy != "aggressive" else numeric_cols[:5]
                
                try:
                    poly_features = poly.fit_transform(state.df[cols_to_use])
                    feature_names = poly.get_feature_names_out(cols_to_use)
                    
                    for i, fname in enumerate(feature_names):
                        if fname not in cols_to_use:  # Skip original columns
                            col_name = f"poly_{degree}_{fname}"
                            state.df[col_name] = poly_features[:, i]
                            new_features.append(col_name)
                            state.engineered_features.append(col_name)
                except Exception as e:
                    logger.warning(f"Could not generate degree {degree} polynomials: {e}")
        
        state.transformation_log["polynomial_features"] = {
            "count": len(new_features),
            "max_degree": max_degree,
            "features": new_features[:10]  # Log first 10
        }
        
        return state
    
    def _generate_interactions(self, state: FeatureEngineeringState, 
                             strategy: str) -> FeatureEngineeringState:
        """Generate interaction terms between numeric features."""
        numeric_cols = [col for col in state.df.columns 
                       if state.schema.get(col, {}).get("type") in ["numeric", "int64", "float64"]
                       and col not in state.engineered_features]
        
        new_features = []
        max_interactions = 15 if strategy == "aggressive" else (8 if strategy == "smart" else 3)
        interaction_count = 0
        
        # Create interactions between numeric features
        for i in range(len(numeric_cols)):
            if interaction_count >= max_interactions:
                break
            for j in range(i + 1, len(numeric_cols)):
                if interaction_count >= max_interactions:
                    break
                
                col1, col2 = numeric_cols[i], numeric_cols[j]
                col_name = f"interact_{col1}_{col2}"
                
                try:
                    state.df[col_name] = state.df[col1] * state.df[col2]
                    new_features.append(col_name)
                    state.engineered_features.append(col_name)
                    interaction_count += 1
                except Exception as e:
                    logger.warning(f"Could not create interaction {col1}*{col2}: {e}")
        
        state.transformation_log["interaction_features"] = {
            "count": len(new_features),
            "max_interactions": max_interactions,
            "features": new_features[:10]
        }
        
        return state
    
    def _generate_domain_features(self, state: FeatureEngineeringState, 
                                 strategy: str) -> FeatureEngineeringState:
        """Generate domain-specific features."""
        new_features = []
        
        # Check for datetime columns
        for col in state.df.columns:
            try:
                if pd.api.types.is_datetime64_any_dtype(state.df[col]):
                    # Extract temporal features
                    state.df[f"{col}_year"] = state.df[col].dt.year
                    state.df[f"{col}_month"] = state.df[col].dt.month
                    state.df[f"{col}_day"] = state.df[col].dt.day
                    state.df[f"{col}_dayofweek"] = state.df[col].dt.dayofweek
                    state.df[f"{col}_quarter"] = state.df[col].dt.quarter
                    
                    new_features.extend([
                        f"{col}_year", f"{col}_month", f"{col}_day",
                        f"{col}_dayofweek", f"{col}_quarter"
                    ])
                    state.engineered_features.extend(new_features[-5:])
            except Exception as e:
                logger.debug(f"Could not extract datetime features from {col}: {e}")
        
        # Check for text columns
        for col in state.df.columns:
            if state.schema.get(col, {}).get("type") == "string":
                try:
                    state.df[f"{col}_length"] = state.df[col].astype(str).str.len()
                    state.df[f"{col}_word_count"] = state.df[col].astype(str).str.split().str.len()
                    
                    new_features.extend([f"{col}_length", f"{col}_word_count"])
                    state.engineered_features.extend([f"{col}_length", f"{col}_word_count"])
                except Exception as e:
                    logger.debug(f"Could not extract text features from {col}: {e}")
        
        # Create ratio features for numeric pairs
        numeric_cols = [col for col in state.df.columns 
                       if state.schema.get(col, {}).get("type") in ["numeric", "int64", "float64"]
                       and col not in state.engineered_features]
        
        if strategy == "aggressive" and len(numeric_cols) >= 2:
            for i in range(min(3, len(numeric_cols))):
                for j in range(i + 1, min(i + 3, len(numeric_cols))):
                    col1, col2 = numeric_cols[i], numeric_cols[j]
                    try:
                        if (state.df[col2] != 0).all():
                            col_name = f"ratio_{col1}_{col2}"
                            state.df[col_name] = state.df[col1] / (state.df[col2] + 1e-8)
                            new_features.append(col_name)
                            state.engineered_features.append(col_name)
                    except Exception as e:
                        logger.debug(f"Could not create ratio feature: {e}")
        
        state.transformation_log["domain_features"] = {
            "count": len(new_features),
            "features": new_features[:10]
        }
        
        return state
    
    def _calculate_feature_importance(self, state: FeatureEngineeringState,
                                     target_column: str) -> FeatureEngineeringState:
        """Calculate feature importance using tree-based and correlation methods."""
        
        # Prepare data
        X = state.df.drop(columns=[target_column])
        y = state.df[target_column]
        
        # Handle missing values
        X = X.fillna(X.mean(numeric_only=True))
        
        # Select numeric features only
        numeric_features = X.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numeric_features:
            return state
        
        X_numeric = X[numeric_features]
        
        # Use correlation for quick ranking
        importance = {}
        for col in X_numeric.columns:
            try:
                if len(y) > 2:
                    if state.problem_type == "classification":
                        # Use point-biserial correlation for binary target
                        corr, _ = pearsonr(X_numeric[col], pd.factorize(y)[0])
                    else:
                        corr, _ = pearsonr(X_numeric[col], y)
                    importance[col] = abs(corr)
            except Exception as e:
                logger.debug(f"Could not calculate correlation for {col}: {e}")
                importance[col] = 0.0
        
        # Try tree-based importance if sample size is adequate
        if len(X_numeric) > 10:
            try:
                if state.problem_type == "classification":
                    model = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
                else:
                    model = RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1)
                
                model.fit(X_numeric, y)
                tree_importance = dict(zip(X_numeric.columns, model.feature_importances_))
                
                # Blend correlation and tree importance
                for col in importance:
                    if col in tree_importance:
                        importance[col] = 0.5 * importance[col] + 0.5 * tree_importance[col]
            except Exception as e:
                logger.warning(f"Could not calculate tree-based importance: {e}")
        
        # Sort by importance
        state.feature_importance = dict(sorted(importance.items(), 
                                             key=lambda x: x[1], 
                                             reverse=True))
        
        return state
    
    def _select_features(self, state: FeatureEngineeringState, 
                        target_column: Optional[str],
                        strategy: str) -> FeatureEngineeringState:
        """Select most important features."""
        
        # Determine number of features to keep
        total_features = len(state.df.columns) - 1 if target_column else len(state.df.columns)
        
        if strategy == "aggressive":
            n_features = max(20, total_features)
        elif strategy == "conservative":
            n_features = max(5, int(total_features * 0.3))
        else:  # smart
            n_features = max(10, int(total_features * 0.5))
        
        # Use feature importance if available
        if state.feature_importance:
            selected = sorted(state.feature_importance.keys(), 
                            key=lambda x: state.feature_importance[x], 
                            reverse=True)[:n_features]
            state.selected_features = selected
        else:
            # Fall back to all numeric features
            state.selected_features = [col for col in state.df.columns 
                                      if state.schema.get(col, {}).get("type") in 
                                      ["numeric", "int64", "float64", "int", "float"]][:n_features]
        
        state.transformation_log["feature_selection"] = {
            "strategy": strategy,
            "total_features": total_features,
            "selected_count": len(state.selected_features),
            "selected_features": state.selected_features
        }
        
        return state
    
    def _save_logs(self, state: FeatureEngineeringState) -> FeatureEngineeringState:
        """Save transformation logs."""
        
        log_path = self.logs_dir / f"{state.job_id}_engineering.json"
        
        log_data = {
            "job_id": state.job_id,
            "problem_type": state.problem_type,
            "total_original_features": len(state.schema),
            "total_engineered_features": len(state.df.columns) - len(state.schema),
            "engineered_feature_count": len(state.engineered_features),
            "feature_importance": {k: float(v) for k, v in state.feature_importance.items()},
            "selected_features": state.selected_features,
            "transformations": state.transformation_log
        }
        
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        logger.info(f"Saved feature engineering log to {log_path}")
        
        return state
    
    def get_feature_report(self, job_id: str) -> Dict:
        """Get feature engineering report for a job."""
        log_path = self.logs_dir / f"{job_id}_engineering.json"
        
        if not log_path.exists():
            return {"error": f"No log found for job {job_id}"}
        
        with open(log_path, 'r') as f:
            return json.load(f)


def build_feature_engineering_workflow():
    """Build feature engineering workflow for LangGraph integration."""
    # This function returns the agent for use in orchestration
    return FeatureEngineeringAgent()
