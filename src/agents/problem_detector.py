"""
Auto Problem Detection Agent
Module 3: LangGraph agent for problem type detection
Detects target column and problem type (classification/regression)
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import pandas as pd
from langgraph.graph import StateGraph, END
from src.llm.provider import get_llm_provider


@dataclass
class ProblemDetectionState:
    """State for problem detection agent."""

    job_id: str
    dataframe: pd.DataFrame
    schema: Dict[str, Any]
    metadata: Dict[str, Any]
    detected_problem_type: Optional[str] = None
    target_column: Optional[str] = None
    features: Optional[List[str]] = None
    confidence: float = 0.0
    reasoning: str = ""
    requires_human_review: bool = False


class AutoProblemDetector:
    """
    Multi-stage problem detection using heuristics + LLM.

    Process:
    1. Heuristics: Check for obvious targets (id, target, label, price, etc.)
    2. LLM Analysis: Let Gemini/Ollama suggest based on column names and stats
    3. Type Detection: Determine classification vs regression
    4. Confidence Gate: Require >0.7 confidence or flag for human review
    """

    def __init__(self, llm_provider: str = "ollama"):
        self.llm = get_llm_provider(llm_provider)
        self.target_keywords = {
            "target",
            "label",
            "class",
            "outcome",
            "prediction",
            "y",
            "price",
            "revenue",
            "salary",
            "churn",
            "default",
            "fraud",
            "disease",
            "diagnosis",
        }
        self.feature_keywords = {"id", "index", "date", "time", "timestamp"}

    def detect(self, state: ProblemDetectionState) -> ProblemDetectionState:
        """
        Detect problem type and target column.

        Returns:
            Updated state with detected_problem_type, target_column, confidence
        """
        df = state.dataframe
        schema = state.schema
        metadata = state.metadata

        # Stage 1: Heuristic detection
        heuristic_candidates = self._heuristic_detection(df, schema)

        # Stage 2: LLM-assisted detection
        llm_candidates = self._llm_detection(df, schema, metadata, heuristic_candidates)

        # Stage 3: Merge and rank
        best_target = self._rank_candidates(df, heuristic_candidates, llm_candidates)

        if not best_target:
            state.requires_human_review = True
            state.reasoning = "No clear target column detected. Manual review required."
            return state

        target_col, confidence, reasoning = best_target

        # Stage 4: Type detection (classification vs regression)
        problem_type, type_reasoning = self._detect_problem_type(df, target_col)

        # Stage 5: Get feature list
        feature_cols = [col for col in df.columns if col != target_col]

        # Update state
        state.target_column = target_col
        state.detected_problem_type = problem_type
        state.features = feature_cols
        state.confidence = confidence
        state.reasoning = f"{reasoning}\n\nProblem Type: {problem_type}\n{type_reasoning}"

        if confidence < 0.7:
            state.requires_human_review = True

        return state

    def _heuristic_detection(self, df: pd.DataFrame, schema: Dict[str, Any]) -> List[tuple]:
        """
        Heuristic-based target detection.

        Returns:
            List of (column, score) tuples ranked by likelihood
        """
        candidates = []

        for col in df.columns:
            # Skip ID-like columns
            if any(
                keyword in col.lower()
                for keyword in self.feature_keywords
            ):
                continue

            score = 0.0

            # Keyword matching
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in self.target_keywords):
                score += 0.5

            # Position heuristic: last column often target
            if col == df.columns[-1]:
                score += 0.2

            # Type heuristic: numeric/bool more likely target
            col_schema = schema.get(col, {})
            col_type = col_schema.get("detected_type", "unknown")

            if col_type in ["numeric", "categorical"]:
                score += 0.1

            # Cardinality heuristic
            unique_ratio = col_schema.get("unique_values", 0) / len(df)
            if 0.01 < unique_ratio < 0.9:
                score += 0.1

            if score > 0:
                candidates.append((col, score))

        return sorted(candidates, key=lambda x: x[1], reverse=True)

    def _llm_detection(
        self,
        df: pd.DataFrame,
        schema: Dict[str, Any],
        metadata: Dict[str, Any],
        heuristic_candidates: List[tuple],
    ) -> List[tuple]:
        """
        Use LLM to analyze and suggest target column.

        Returns:
            List of (column, score) tuples from LLM analysis
        """
        # Build prompt
        col_descriptions = "\n".join(
            [
                f"- {col}: {schema[col]['detected_type']} "
                f"({schema[col]['unique_values']} unique, "
                f"{schema[col]['null_percentage']}% null)"
                for col in df.columns[:10]  # Limit to 10 cols for prompt
            ]
        )

        prompt = f"""
You are a machine learning expert. Analyze these columns and suggest which is most likely the TARGET variable (what we want to predict):

Columns:
{col_descriptions}

Dataset info:
- Total rows: {metadata['total_rows']}
- Numeric columns: {metadata['numeric_columns'][:3]}
- Categorical columns: {metadata['categorical_columns'][:3]}

Based on column names, types, and cardinality, suggest:
1. Most likely target column
2. Why (be concise)
3. Confidence 0-10

Format: TARGET: column_name | REASON: ... | CONFIDENCE: X/10
"""

        try:
            response = self.llm.generate(prompt, temperature=0.1, max_tokens=200)

            # Parse response
            if "TARGET:" in response:
                parts = response.split("|")
                target = parts[0].replace("TARGET:", "").strip()
                confidence_str = parts[-1].replace("CONFIDENCE:", "").strip()

                # Validate column exists
                if target in df.columns:
                    confidence_score = float(confidence_str.split("/")[0]) / 10.0
                    return [(target, confidence_score)]

        except Exception as e:
            print(f"LLM detection failed: {e}")

        return []

    def _rank_candidates(
        self,
        df: pd.DataFrame,
        heuristic_candidates: List[tuple],
        llm_candidates: List[tuple],
    ) -> Optional[tuple]:
        """
        Merge heuristic and LLM results.

        Returns:
            Best candidate as (column, confidence, reasoning) or None
        """
        # LLM suggestions have high weight if provided
        if llm_candidates:
            target, llm_score = llm_candidates[0]
            if target in df.columns:
                reasoning = f"LLM-assisted detection: {target} (confidence: {llm_score:.2f})"
                return (target, llm_score, reasoning)

        # Fall back to heuristics
        if heuristic_candidates:
            target, heuristic_score = heuristic_candidates[0]
            reasoning = f"Heuristic detection: {target} (confidence: {heuristic_score:.2f})"
            return (target, heuristic_score, reasoning)

        return None

    def _detect_problem_type(self, df: pd.DataFrame, target_col: str) -> tuple:
        """
        Determine if this is classification or regression.

        Returns:
            (problem_type, reasoning) where problem_type in ["classification", "regression"]
        """
        target = df[target_col].dropna()

        # Check cardinality
        unique_count = target.nunique()
        unique_ratio = unique_count / len(target)

        # Check type
        try:
            pd.to_numeric(target, errors="raise")
            is_numeric = True
        except:
            is_numeric = False

        # Decision logic
        if not is_numeric:
            # Categorical target = classification
            return "classification", f"Categorical target with {unique_count} classes"

        # For numeric targets, check if values look discrete (integer-like and limited range)
        # vs continuous (floats or many unique values)
        
        # Check if all values are integers
        all_integers = all(val == int(val) for val in target if pd.notna(val))
        
        if all_integers and unique_count <= 5:
            # Very few discrete numeric values = likely classification (e.g., 0,1,2,3 for classes)
            return "classification", f"Numeric target with {unique_count} discrete values"
        
        if unique_ratio < 0.05 and unique_count <= 3:
            # <5% unique with <= 3 classes = likely classification
            return "classification", f"Low cardinality ratio {unique_ratio:.2%}"

        # Otherwise, continuous numeric target = regression
        return "regression", f"Continuous numeric target with {unique_count} unique values"

        # Otherwise regression
        return "regression", f"Continuous numeric target ({unique_count} unique values)"


# Build LangGraph workflow
def build_problem_detection_graph():
    """Create LangGraph workflow for problem detection."""

    detector = AutoProblemDetector()

    def detect_node(state: ProblemDetectionState) -> ProblemDetectionState:
        """Detection node."""
        return detector.detect(state)

    def requires_review_node(state: ProblemDetectionState) -> str:
        """Route based on confidence."""
        if state.requires_human_review:
            return "human_review"
        return "confirmed"

    # Build graph
    graph = StateGraph(ProblemDetectionState)
    graph.add_node("detect", detect_node)
    graph.add_node("route", requires_review_node)
    graph.add_node("confirmed", lambda x: x)
    graph.add_node("human_review", lambda x: x)

    graph.add_edge("detect", "route")
    graph.add_edge("route", "confirmed")
    graph.add_edge("route", "human_review")
    graph.add_edge("confirmed", END)
    graph.add_edge("human_review", END)

    graph.set_entry_point("detect")

    return graph.compile()


# Export
__all__ = ["AutoProblemDetector", "ProblemDetectionState", "build_problem_detection_graph"]
