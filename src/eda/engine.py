"""
EDA (Exploratory Data Analysis) Engine
Module 6: Auto-generate 8 plots and statistical insights
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json


class EDAEngine:
    """
    Automated Exploratory Data Analysis Engine.

    Generates:
    1. Distribution plots (histograms)
    2. Correlation heatmap
    3. Pairplot (relationships between variables)
    4. Box plots (outlier detection)
    5. Missing value patterns
    6. Categorical value counts
    7. Q-Q plots (normality check)
    8. Scatter plots (relationships)
    """

    PLOT_DIR = "data/eda_plots"
    REPORT_DIR = "data/eda_reports"

    def __init__(self, figsize: tuple = (15, 10), style: str = "darkgrid"):
        """Initialize EDA engine."""
        Path(self.PLOT_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.REPORT_DIR).mkdir(parents=True, exist_ok=True)
        sns.set_style(style)
        self.figsize = figsize

    def generate_report(
        self, df: pd.DataFrame, schema: Dict[str, Any], job_id: str
    ) -> Dict[str, Any]:
        """
        Generate comprehensive EDA report.

        Returns:
            Dictionary with statistics, plots, and insights
        """
        report = {
            "job_id": job_id,
            "timestamp": datetime.now().isoformat(),
            "dataset_shape": {"rows": len(df), "columns": len(df.columns)},
            "basic_statistics": self._basic_statistics(df),
            "column_analysis": self._column_analysis(df, schema),
            "correlation_analysis": self._correlation_analysis(df),
            "missing_value_analysis": self._missing_value_analysis(df),
            "categorical_analysis": self._categorical_analysis(df, schema),
            "numeric_distribution": self._numeric_distribution(df, schema),
            "outlier_analysis": self._outlier_analysis(df, schema),
            "insights": self._generate_insights(df, schema),
        }

        # Save report
        report_path = Path(self.REPORT_DIR) / f"{job_id}_eda_report.json"
        with open(report_path, "w") as f:
            # Convert numpy types to Python types for JSON serialization
            json.dump(self._make_json_serializable(report), f, indent=2)

        return report

    def generate_plots(self, df: pd.DataFrame, schema: Dict[str, Any], job_id: str) -> List[str]:
        """
        Generate and save 8 EDA plots.

        Returns:
            List of plot file paths
        """
        plot_paths = []

        # 1. Distribution plots (histograms)
        plot_paths.append(self._plot_distributions(df, schema, job_id))

        # 2. Correlation heatmap
        plot_paths.append(self._plot_correlation(df, schema, job_id))

        # 3. Pairplot
        plot_paths.append(self._plot_pairplot(df, schema, job_id))

        # 4. Box plots
        plot_paths.append(self._plot_boxplots(df, schema, job_id))

        # 5. Missing value patterns
        plot_paths.append(self._plot_missing_values(df, job_id))

        # 6. Categorical value counts
        plot_paths.append(self._plot_categorical(df, schema, job_id))

        # 7. Q-Q plots
        plot_paths.append(self._plot_qq(df, schema, job_id))

        # 8. Scatter plots
        plot_paths.append(self._plot_scatter(df, schema, job_id))

        return [p for p in plot_paths if p is not None]

    def _plot_distributions(self, df: pd.DataFrame, schema: Dict[str, Any], job_id: str) -> Optional[str]:
        """Plot histograms of numeric distributions."""
        numeric_cols = [
            col for col, info in schema.items() if info.get("detected_type") in ["int64", "float64", "numeric"]
        ]

        if not numeric_cols:
            return None

        n_cols = min(4, len(numeric_cols))
        n_rows = (len(numeric_cols) + n_cols - 1) // n_cols

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4 * n_rows))
        axes = axes.flatten()

        for idx, col in enumerate(numeric_cols):
            ax = axes[idx]
            df[col].hist(bins=30, ax=ax, edgecolor="black", alpha=0.7)
            ax.set_title(f"Distribution of {col}", fontsize=10, fontweight="bold")
            ax.set_xlabel(col)
            ax.set_ylabel("Frequency")

        # Hide extra subplots
        for idx in range(len(numeric_cols), len(axes)):
            axes[idx].set_visible(False)

        plt.tight_layout()
        path = f"{self.PLOT_DIR}/{job_id}_01_distributions.png"
        plt.savefig(path, dpi=100, bbox_inches="tight")
        plt.close()
        return path

    def _plot_correlation(self, df: pd.DataFrame, schema: Dict[str, Any], job_id: str) -> Optional[str]:
        """Plot correlation heatmap."""
        numeric_df = df.select_dtypes(include=[np.number])

        if numeric_df.shape[1] < 2:
            return None

        fig, ax = plt.subplots(figsize=(10, 8))
        corr_matrix = numeric_df.corr()
        sns.heatmap(
            corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax, 
            square=True, linewidths=0.5
        )
        ax.set_title("Correlation Matrix", fontsize=12, fontweight="bold", pad=20)
        plt.tight_layout()

        path = f"{self.PLOT_DIR}/{job_id}_02_correlation.png"
        plt.savefig(path, dpi=100, bbox_inches="tight")
        plt.close()
        return path

    def _plot_pairplot(self, df: pd.DataFrame, schema: Dict[str, Any], job_id: str) -> Optional[str]:
        """Plot pairplot (limited to first 4 numeric columns)."""
        numeric_cols = [
            col for col, info in schema.items() if info.get("detected_type") in ["int64", "float64", "numeric"]
        ]

        if len(numeric_cols) < 2:
            return None

        # Limit to first 4 columns for performance
        cols_to_plot = numeric_cols[:4]
        g = sns.pairplot(df[cols_to_plot], diag_kind="hist", plot_kws={"alpha": 0.6})
        g.fig.suptitle("Pairplot of Numeric Variables", fontsize=12, fontweight="bold", y=1.00)

        path = f"{self.PLOT_DIR}/{job_id}_03_pairplot.png"
        plt.savefig(path, dpi=100, bbox_inches="tight")
        plt.close()
        return path

    def _plot_boxplots(self, df: pd.DataFrame, schema: Dict[str, Any], job_id: str) -> Optional[str]:
        """Plot box plots for outlier detection."""
        numeric_cols = [
            col for col, info in schema.items() if info.get("detected_type") in ["int64", "float64", "numeric"]
        ]

        if not numeric_cols:
            return None

        n_cols = min(4, len(numeric_cols))
        n_rows = (len(numeric_cols) + n_cols - 1) // n_cols

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4 * n_rows))
        axes = axes.flatten()

        for idx, col in enumerate(numeric_cols):
            ax = axes[idx]
            df.boxplot(column=col, ax=ax)
            ax.set_title(f"Box Plot of {col}", fontsize=10, fontweight="bold")
            ax.set_ylabel(col)

        # Hide extra subplots
        for idx in range(len(numeric_cols), len(axes)):
            axes[idx].set_visible(False)

        plt.tight_layout()
        path = f"{self.PLOT_DIR}/{job_id}_04_boxplots.png"
        plt.savefig(path, dpi=100, bbox_inches="tight")
        plt.close()
        return path

    def _plot_missing_values(self, df: pd.DataFrame, job_id: str) -> Optional[str]:
        """Plot missing value patterns."""
        missing = df.isnull().sum()
        if missing.sum() == 0:
            return None

        missing = missing[missing > 0].sort_values(ascending=False)

        fig, ax = plt.subplots(figsize=(10, 6))
        missing.plot(kind="barh", ax=ax, color="coral")
        ax.set_title("Missing Values by Column", fontsize=12, fontweight="bold")
        ax.set_xlabel("Count of Missing Values")
        plt.tight_layout()

        path = f"{self.PLOT_DIR}/{job_id}_05_missing_values.png"
        plt.savefig(path, dpi=100, bbox_inches="tight")
        plt.close()
        return path

    def _plot_categorical(self, df: pd.DataFrame, schema: Dict[str, Any], job_id: str) -> Optional[str]:
        """Plot categorical value counts."""
        categorical_cols = [
            col for col, info in schema.items() if info.get("detected_type") in ["object", "category"]
        ]

        if not categorical_cols:
            return None

        n_cols = min(3, len(categorical_cols))
        n_rows = (len(categorical_cols) + n_cols - 1) // n_cols

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))
        if n_rows == 1 and n_cols == 1:
            axes = np.array([axes])
        elif n_rows == 1 or n_cols == 1:
            axes = axes.flatten() if hasattr(axes, 'flatten') else np.array(axes)
        else:
            axes = axes.flatten()

        for idx, col in enumerate(categorical_cols):
            ax = axes[idx] if isinstance(axes, np.ndarray) else axes
            df[col].value_counts().head(10).plot(kind="bar", ax=ax, color="steelblue")
            ax.set_title(f"Top Categories in {col}", fontsize=10, fontweight="bold")
            ax.set_xlabel(col)
            ax.set_ylabel("Count")
            ax.tick_params(axis="x", rotation=45)

        # Hide extra subplots
        if isinstance(axes, np.ndarray):
            for idx in range(len(categorical_cols), len(axes)):
                axes[idx].set_visible(False)

        plt.tight_layout()
        path = f"{self.PLOT_DIR}/{job_id}_06_categorical.png"
        plt.savefig(path, dpi=100, bbox_inches="tight")
        plt.close()
        return path

    def _plot_qq(self, df: pd.DataFrame, schema: Dict[str, Any], job_id: str) -> Optional[str]:
        """Plot Q-Q plots for normality check."""
        from scipy import stats

        numeric_cols = [
            col for col, info in schema.items() if info.get("detected_type") in ["int64", "float64", "numeric"]
        ]

        if not numeric_cols:
            return None

        n_cols = min(3, len(numeric_cols))
        n_rows = (len(numeric_cols) + n_cols - 1) // n_cols

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))
        axes = axes.flatten()

        for idx, col in enumerate(numeric_cols):
            ax = axes[idx]
            stats.probplot(df[col].dropna(), dist="norm", plot=ax)
            ax.set_title(f"Q-Q Plot: {col}", fontsize=10, fontweight="bold")

        # Hide extra subplots
        for idx in range(len(numeric_cols), len(axes)):
            axes[idx].set_visible(False)

        plt.tight_layout()
        path = f"{self.PLOT_DIR}/{job_id}_07_qq_plots.png"
        plt.savefig(path, dpi=100, bbox_inches="tight")
        plt.close()
        return path

    def _plot_scatter(self, df: pd.DataFrame, schema: Dict[str, Any], job_id: str) -> Optional[str]:
        """Plot scatter plots of numeric relationships."""
        numeric_cols = [
            col for col, info in schema.items() if info.get("detected_type") in ["int64", "float64", "numeric"]
        ]

        if len(numeric_cols) < 2:
            return None

        # Select first 4 columns
        cols_to_plot = numeric_cols[:4]
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.flatten()

        pairs = [(cols_to_plot[i], cols_to_plot[j]) for i in range(len(cols_to_plot)) for j in range(i + 1, len(cols_to_plot))]
        
        for idx, (col1, col2) in enumerate(pairs[:4]):
            ax = axes[idx]
            ax.scatter(df[col1], df[col2], alpha=0.5)
            ax.set_xlabel(col1)
            ax.set_ylabel(col2)
            ax.set_title(f"Scatter: {col1} vs {col2}", fontsize=10, fontweight="bold")

        # Hide extra subplots
        for idx in range(len(pairs), 4):
            axes[idx].set_visible(False)

        plt.tight_layout()
        path = f"{self.PLOT_DIR}/{job_id}_08_scatter.png"
        plt.savefig(path, dpi=100, bbox_inches="tight")
        plt.close()
        return path

    def _basic_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate basic statistics."""
        return {
            "shape": list(df.shape),
            "memory_usage_mb": float(df.memory_usage(deep=True).sum() / 1024 / 1024),
            "total_cells": int(len(df) * len(df.columns)),
            "total_missing": int(df.isnull().sum().sum()),
            "duplicates": int(df.duplicated().sum()),
        }

    def _column_analysis(self, df: pd.DataFrame, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze each column."""
        analysis = {}
        for col in df.columns:
            col_type = schema.get(col, {}).get("detected_type", str(df[col].dtype))
            analysis[col] = {
                "type": str(col_type),
                "non_null_count": int(df[col].notna().sum()),
                "null_count": int(df[col].isna().sum()),
                "unique_values": int(df[col].nunique()),
                "min": float(df[col].min()) if pd.api.types.is_numeric_dtype(df[col]) else None,
                "max": float(df[col].max()) if pd.api.types.is_numeric_dtype(df[col]) else None,
                "mean": float(df[col].mean()) if pd.api.types.is_numeric_dtype(df[col]) else None,
            }
        return analysis

    def _correlation_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze correlations."""
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.shape[1] < 2:
            return {"message": "Not enough numeric columns for correlation"}

        corr = numeric_df.corr()
        # Find strong correlations
        strong_corrs = []
        for i in range(len(corr.columns)):
            for j in range(i + 1, len(corr.columns)):
                val = float(corr.iloc[i, j])
                if abs(val) > 0.7:
                    strong_corrs.append(
                        {
                            "var1": str(corr.columns[i]),
                            "var2": str(corr.columns[j]),
                            "correlation": val,
                        }
                    )

        return {"strong_correlations": strong_corrs}

    def _missing_value_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze missing values."""
        missing = df.isnull().sum()
        return {
            "columns_with_missing": {str(col): int(count) for col, count in missing[missing > 0].items()},
            "total_missing_pct": float((df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100),
        }

    def _categorical_analysis(self, df: pd.DataFrame, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze categorical columns."""
        categorical_cols = [
            col for col, info in schema.items() if info.get("detected_type") in ["object", "category"]
        ]

        analysis = {}
        for col in categorical_cols:
            analysis[col] = {
                "unique_values": int(df[col].nunique()),
                "top_5": dict(df[col].value_counts().head(5)),
            }
        return analysis

    def _numeric_distribution(self, df: pd.DataFrame, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze numeric distributions."""
        numeric_cols = [
            col for col, info in schema.items() if info.get("detected_type") in ["int64", "float64", "numeric"]
        ]

        analysis = {}
        for col in numeric_cols:
            skew = float(df[col].skew())
            kurtosis = float(df[col].kurtosis())
            analysis[col] = {
                "skewness": skew,
                "kurtosis": kurtosis,
                "distribution": "normal" if abs(skew) < 1 else "skewed",
            }
        return analysis

    def _outlier_analysis(self, df: pd.DataFrame, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze outliers using IQR method."""
        numeric_cols = [
            col for col, info in schema.items() if info.get("detected_type") in ["int64", "float64", "numeric"]
        ]

        analysis = {}
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            outliers = df[(df[col] < lower) | (df[col] > upper)]
            analysis[col] = {
                "outlier_count": int(len(outliers)),
                "outlier_pct": float((len(outliers) / len(df)) * 100),
                "lower_bound": float(lower),
                "upper_bound": float(upper),
            }
        return analysis

    def _generate_insights(self, df: pd.DataFrame, schema: Dict[str, Any]) -> List[str]:
        """Generate automated insights."""
        insights = []

        # Check for imbalanced classes
        categorical_cols = [col for col, info in schema.items() if info.get("detected_type") in ["object", "category"]]
        for col in categorical_cols:
            val_counts = df[col].value_counts()
            if len(val_counts) <= 10:
                max_pct = (val_counts.iloc[0] / len(df)) * 100
                if max_pct > 80:
                    insights.append(f"⚠️ Highly imbalanced: {col} (top class = {max_pct:.1f}%)")

        # Check for missing data
        missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        if missing_pct > 5:
            insights.append(f"⚠️ Significant missing data: {missing_pct:.1f}%")

        # Check for duplicates
        dup_count = df.duplicated().sum()
        if dup_count > 0:
            insights.append(f"⚠️ {dup_count} duplicate rows found")

        # Check correlations
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.shape[1] >= 2:
            corr = numeric_df.corr()
            high_corr_pairs = []
            for i in range(len(corr.columns)):
                for j in range(i + 1, len(corr.columns)):
                    if abs(corr.iloc[i, j]) > 0.9:
                        high_corr_pairs.append(corr.columns[i])
            if high_corr_pairs:
                insights.append(f"ℹ️ High multicollinearity detected in: {', '.join(set(high_corr_pairs))}")

        if not insights:
            insights.append("✅ Dataset looks clean and well-structured")

        return insights

    def _make_json_serializable(self, obj: Any) -> Any:
        """Convert numpy/pandas types to Python types for JSON serialization."""
        if isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj) if isinstance(obj, np.floating) else int(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.Series):
            return obj.to_dict()
        elif pd.isna(obj):
            return None
        return obj


# Export
__all__ = ["EDAEngine"]
