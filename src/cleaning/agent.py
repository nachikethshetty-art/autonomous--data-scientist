"""
Data Cleaning Agent
Module 5: Intelligent data cleaning with LangGraph orchestration
Handles missing values, outliers, scaling, and encoding
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import pandas as pd
import numpy as np
from datetime import datetime
import json
from pathlib import Path

from langgraph.graph import StateGraph, END


@dataclass
class CleaningState:
    """State for data cleaning workflow."""

    job_id: str
    dataframe: pd.DataFrame
    original_dataframe: pd.DataFrame
    schema: Dict[str, Any]
    metadata: Dict[str, Any]
    cleaning_log: List[Dict[str, Any]] = field(default_factory=list)
    cleaned_dataframe: Optional[pd.DataFrame] = None
    cleaning_complete: bool = False
    errors: List[str] = field(default_factory=list)


class DataCleaningAgent:
    """
    Intelligent data cleaning agent using multiple strategies.

    Handles:
    - Missing values (mean, median, forward-fill, drop)
    - Duplicate rows
    - Outliers (IQR method, Z-score)
    - Type conversions
    - Feature scaling (StandardScaler, MinMaxScaler)
    - Categorical encoding (one-hot, label encoding)
    """

    LOG_DIR = "data/cleaning_logs"

    def __init__(self):
        """Initialize cleaning agent."""
        Path(self.LOG_DIR).mkdir(parents=True, exist_ok=True)

    def clean(
        self,
        df: pd.DataFrame,
        schema: Dict[str, Any],
        metadata: Dict[str, Any],
        job_id: str,
        strategy: str = "smart",
    ) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
        """
        Clean a dataframe using intelligent strategy.

        Args:
            df: Input dataframe
            schema: Column type information
            metadata: Dataset metadata
            job_id: Job identifier
            strategy: Cleaning strategy ('smart', 'conservative', 'aggressive')

        Returns:
            (cleaned_dataframe, cleaning_log)
        """
        df = df.copy()
        log = []

        # 1. Handle duplicates
        dup_count = df.duplicated().sum()
        if dup_count > 0:
            df = df.drop_duplicates()
            log.append(
                {
                    "step": 1,
                    "action": "remove_duplicates",
                    "rows_removed": int(dup_count),
                    "remaining_rows": len(df),
                }
            )

        # 2. Handle missing values
        missing_log = self._handle_missing_values(df, schema, strategy)
        log.extend(missing_log)

        # 3. Handle outliers
        outlier_log = self._handle_outliers(df, schema, strategy)
        log.extend(outlier_log)

        # 4. Type conversions
        type_log = self._handle_type_conversion(df, schema)
        log.extend(type_log)

        # 5. Encoding categorical variables
        encoding_log = self._handle_categorical_encoding(df, schema)
        log.extend(encoding_log)

        # 6. Feature scaling
        scaling_log = self._handle_scaling(df, schema)
        log.extend(scaling_log)

        # Save cleaning log
        self._save_log(job_id, log)

        return df, log

    def _handle_missing_values(
        self, df: pd.DataFrame, schema: Dict[str, Any], strategy: str
    ) -> List[Dict[str, Any]]:
        """
        Handle missing values intelligently.

        Strategy:
        - smart: Use mean/median for numeric, mode for categorical, drop if >50%
        - conservative: Drop any rows with missing values
        - aggressive: Fill all with strategy-appropriate defaults
        """
        log = []

        for col in df.columns:
            missing_count = df[col].isna().sum()
            if missing_count == 0:
                continue

            missing_pct = (missing_count / len(df)) * 100
            col_type = schema.get(col, {}).get("detected_type", "unknown")

            if strategy == "conservative":
                # Drop rows with any missing values
                df = df.dropna()
                log.append(
                    {
                        "step": 2,
                        "column": col,
                        "action": "drop_rows",
                        "missing_count": int(missing_count),
                        "missing_pct": round(missing_pct, 2),
                    }
                )

            elif missing_pct > 50:
                # Drop column if >50% missing
                df = df.drop(col, axis=1)
                log.append(
                    {
                        "step": 2,
                        "column": col,
                        "action": "drop_column",
                        "reason": "Over 50% missing",
                        "missing_pct": round(missing_pct, 2),
                    }
                )

            elif col_type in ["int64", "float64", "numeric"]:
                # Fill numeric with median (robust to outliers)
                median = df[col].median()
                df[col].fillna(median, inplace=True)
                log.append(
                    {
                        "step": 2,
                        "column": col,
                        "action": "fill_numeric",
                        "method": "median",
                        "fill_value": float(median),
                        "count": int(missing_count),
                    }
                )

            else:
                # Fill categorical with mode
                mode = df[col].mode()
                if len(mode) > 0:
                    mode_val = mode[0]
                    df[col].fillna(mode_val, inplace=True)
                    log.append(
                        {
                            "step": 2,
                            "column": col,
                            "action": "fill_categorical",
                            "method": "mode",
                            "fill_value": str(mode_val),
                            "count": int(missing_count),
                        }
                    )

        return log

    def _handle_outliers(
        self, df: pd.DataFrame, schema: Dict[str, Any], strategy: str
    ) -> List[Dict[str, Any]]:
        """
        Handle outliers using IQR method.

        IQR (Interquartile Range) method:
        - Lower bound: Q1 - 1.5 * IQR
        - Upper bound: Q3 + 1.5 * IQR
        - Points outside bounds are outliers
        """
        log = []

        numeric_cols = [
            col for col, info in schema.items() if info.get("detected_type") in ["int64", "float64", "numeric"]
        ]

        for col in numeric_cols:
            if col not in df.columns:
                continue

            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]

            if len(outliers) > 0:
                if strategy == "aggressive":
                    # Remove outliers
                    df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
                    log.append(
                        {
                            "step": 3,
                            "column": col,
                            "action": "remove_outliers",
                            "method": "IQR",
                            "count_removed": len(outliers),
                            "lower_bound": float(lower_bound),
                            "upper_bound": float(upper_bound),
                        }
                    )
                else:
                    # Clip to bounds
                    df[col] = df[col].clip(lower_bound, upper_bound)
                    log.append(
                        {
                            "step": 3,
                            "column": col,
                            "action": "clip_outliers",
                            "method": "IQR",
                            "count_clipped": len(outliers),
                            "lower_bound": float(lower_bound),
                            "upper_bound": float(upper_bound),
                        }
                    )

        return log

    def _handle_type_conversion(self, df: pd.DataFrame, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert columns to appropriate types based on schema."""
        log = []

        for col, info in schema.items():
            if col not in df.columns:
                continue

            target_type = info.get("detected_type", "object")
            current_type = str(df[col].dtype)

            if target_type in ["int64", "int"] and current_type != "int64":
                try:
                    df[col] = df[col].astype("int64")
                    log.append(
                        {"step": 4, "column": col, "action": "convert_type", "to_type": "int64"}
                    )
                except ValueError:
                    pass  # Skip if conversion fails

            elif target_type in ["float64", "float"] and current_type != "float64":
                try:
                    df[col] = df[col].astype("float64")
                    log.append(
                        {"step": 4, "column": col, "action": "convert_type", "to_type": "float64"}
                    )
                except ValueError:
                    pass

        return log

    def _handle_categorical_encoding(self, df: pd.DataFrame, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Encode categorical variables intelligently.

        Strategy:
        - Binary (2 classes): Label encoding (0, 1)
        - Low cardinality (<10): One-hot encoding
        - High cardinality: Label encoding
        """
        log = []

        categorical_cols = [
            col for col, info in schema.items() if info.get("detected_type") in ["object", "category"]
        ]

        for col in categorical_cols:
            if col not in df.columns:
                continue

            unique_count = df[col].nunique()

            if unique_count == 2:
                # Binary: use label encoding
                mapping = {val: idx for idx, val in enumerate(sorted(df[col].unique()))}
                df[col] = df[col].map(mapping)
                log.append(
                    {
                        "step": 5,
                        "column": col,
                        "action": "label_encode",
                        "unique_values": unique_count,
                        "mapping": mapping,
                    }
                )

            elif unique_count <= 10:
                # Low cardinality: use one-hot encoding
                encoded = pd.get_dummies(df[col], prefix=col)
                df = pd.concat([df.drop(col, axis=1), encoded], axis=1)
                log.append(
                    {
                        "step": 5,
                        "column": col,
                        "action": "onehot_encode",
                        "unique_values": unique_count,
                        "new_columns": list(encoded.columns),
                    }
                )

            else:
                # High cardinality: use label encoding
                mapping = {val: idx for idx, val in enumerate(df[col].unique())}
                df[col] = df[col].map(mapping)
                log.append(
                    {
                        "step": 5,
                        "column": col,
                        "action": "label_encode",
                        "unique_values": unique_count,
                        "reason": "High cardinality",
                    }
                )

        return log

    def _handle_scaling(self, df: pd.DataFrame, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scale numeric features using StandardScaler.

        Formula: (x - mean) / std
        This centers data around 0 with std=1, important for algorithms like KNN, NeuralNets.
        """
        log = []

        numeric_cols = [
            col for col, info in schema.items() if info.get("detected_type") in ["int64", "float64", "numeric"]
        ]

        for col in numeric_cols:
            if col not in df.columns:
                continue

            mean = df[col].mean()
            std = df[col].std()

            if std > 0:
                df[col] = (df[col] - mean) / std
                log.append(
                    {
                        "step": 6,
                        "column": col,
                        "action": "standardize",
                        "method": "StandardScaler",
                        "mean": float(mean),
                        "std": float(std),
                    }
                )

        return log

    def _save_log(self, job_id: str, log: List[Dict[str, Any]]) -> None:
        """Save cleaning log to file."""
        log_path = Path(self.LOG_DIR) / f"{job_id}_cleaning.json"
        with open(log_path, "w") as f:
            json.dump(
                {
                    "job_id": job_id,
                    "timestamp": datetime.now().isoformat(),
                    "steps": log,
                },
                f,
                indent=2,
            )

    def get_cleaning_report(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve cleaning report for a job."""
        log_path = Path(self.LOG_DIR) / f"{job_id}_cleaning.json"
        if not log_path.exists():
            return None

        with open(log_path, "r") as f:
            return json.load(f)


def build_cleaning_workflow() -> Any:
    """Build the cleaning workflow graph."""
    agent = DataCleaningAgent()

    def clean_node(state: CleaningState) -> CleaningState:
        """Cleaning node."""
        df, log = agent.clean(
            state.dataframe, state.schema, state.metadata, state.job_id, strategy="smart"
        )
        state.cleaned_dataframe = df
        state.cleaning_log = log
        state.cleaning_complete = True
        return state

    def validate_node(state: CleaningState) -> str:
        """Validation node - check if cleaning successful."""
        if state.errors or not state.cleaning_complete:
            return "failed"
        return "success"

    # Build graph
    graph = StateGraph(CleaningState)
    graph.add_node("clean", clean_node)
    graph.add_node("validate", validate_node)
    graph.add_node("success", lambda x: x)
    graph.add_node("failed", lambda x: x)

    graph.add_edge("clean", "validate")
    graph.add_edge("validate", "success")
    graph.add_edge("validate", "failed")
    graph.add_edge("success", END)
    graph.add_edge("failed", END)

    graph.set_entry_point("clean")

    return graph.compile()


# Export
__all__ = ["DataCleaningAgent", "CleaningState", "build_cleaning_workflow"]
