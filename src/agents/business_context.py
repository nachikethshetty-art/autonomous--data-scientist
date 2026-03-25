"""
Business Context Agent
Module 2: Capture user's business context for the ML problem
"""

import json
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path


class BusinessContextManager:
    """Manages business context information for ML problems."""

    CONTEXT_DIR = "data/business_contexts"

    def __init__(self):
        """Initialize business context manager."""
        Path(self.CONTEXT_DIR).mkdir(parents=True, exist_ok=True)

    def create_context(
        self,
        job_id: str,
        prediction_goal: str,
        domain: str,
        target_audience: str,
        success_metric: str,
        constraints: Optional[str] = None,
        special_requirements: Optional[str] = None,
        budget: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create and save business context for a job.

        Args:
            job_id: Unique job identifier
            prediction_goal: What are we trying to predict? (e.g., "Identify customers likely to churn")
            domain: Business domain (e.g., "Telecommunications", "Finance", "Healthcare")
            target_audience: Who will use this model? (e.g., "Customer retention team", "Risk managers")
            success_metric: How will we measure success? (e.g., "Precision >= 0.85")
            constraints: Any constraints? (e.g., "Must run in <100ms", "Interpretable only")
            special_requirements: Any special requirements? (e.g., "Handle imbalanced data", "Fairness critical")
            budget: Resource budget (e.g., "CPU only", "GPU available")

        Returns:
            Context dictionary with metadata
        """
        context = {
            "job_id": job_id,
            "context_id": str(uuid.uuid4()),
            "created_at": datetime.now().isoformat(),
            "prediction_goal": prediction_goal,
            "domain": domain,
            "target_audience": target_audience,
            "success_metric": success_metric,
            "constraints": constraints or "None specified",
            "special_requirements": special_requirements or "None specified",
            "budget": budget or "Standard (CPU)",
        }

        # Save to file
        context_path = Path(self.CONTEXT_DIR) / f"{job_id}_context.json"
        with open(context_path, "w") as f:
            json.dump(context, f, indent=2)

        return context

    def get_context(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve business context for a job.

        Args:
            job_id: Unique job identifier

        Returns:
            Context dictionary or None if not found
        """
        context_path = Path(self.CONTEXT_DIR) / f"{job_id}_context.json"

        if not context_path.exists():
            return None

        with open(context_path, "r") as f:
            return json.load(f)

    def update_context(self, job_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update existing business context.

        Args:
            job_id: Unique job identifier
            updates: Fields to update

        Returns:
            Updated context dictionary or None if not found
        """
        context = self.get_context(job_id)
        if not context:
            return None

        context.update(updates)
        context["updated_at"] = datetime.now().isoformat()

        context_path = Path(self.CONTEXT_DIR) / f"{job_id}_context.json"
        with open(context_path, "w") as f:
            json.dump(context, f, indent=2)

        return context

    def get_insights(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI insights based on business context.

        Returns recommendations for:
        - Model types suitable for the domain
        - Success metrics to optimize
        - Potential challenges and mitigation
        """
        domain = context.get("domain", "").lower()
        goal = context.get("prediction_goal", "").lower()
        constraints = context.get("constraints", "").lower()

        insights = {
            "recommended_models": [],
            "optimization_targets": [],
            "challenges": [],
            "mitigation": [],
        }

        # Domain-specific recommendations
        if "finance" in domain or "bank" in domain:
            insights["recommended_models"] = ["Logistic Regression", "XGBoost", "Neural Network"]
            insights["optimization_targets"] = ["Precision", "Recall", "ROC-AUC"]
            insights["challenges"] = ["Class imbalance (fraud is rare)", "Regulatory compliance"]
            insights["mitigation"] = [
                "Use SMOTE for imbalance",
                "Ensure model explainability for regulatory audits",
            ]

        elif "healthcare" in domain or "medical" in domain:
            insights["recommended_models"] = ["Logistic Regression", "Neural Network"]
            insights["optimization_targets"] = ["Sensitivity", "Specificity", "AUC"]
            insights["challenges"] = ["Patient privacy (HIPAA)", "Rare diseases"]
            insights["mitigation"] = [
                "Implement differential privacy",
                "Use stratified sampling for rare conditions",
            ]

        elif "retail" in domain or "ecommerce" in domain or "churn" in goal:
            insights["recommended_models"] = ["XGBoost", "Random Forest", "Neural Network"]
            insights["optimization_targets"] = ["ROC-AUC", "F1-Score", "Business KPI"]
            insights["challenges"] = ["Temporal patterns", "Seasonality"]
            insights["mitigation"] = ["Use time-series CV", "Include seasonal features"]

        elif "telecom" in domain:
            insights["recommended_models"] = ["XGBoost", "Random Forest", "Logistic Regression"]
            insights["optimization_targets"] = ["Precision", "Recall", "Customer Lifetime Value"]
            insights["challenges"] = ["High customer volume", "Real-time requirements"]
            insights["mitigation"] = ["Optimize for latency", "Use feature selection"]

        else:
            # Generic recommendations
            insights["recommended_models"] = ["Logistic Regression", "XGBoost", "Random Forest"]
            insights["optimization_targets"] = ["Accuracy", "F1-Score", "ROC-AUC"]
            insights["challenges"] = ["Unknown domain patterns"]
            insights["mitigation"] = ["Start with baseline models", "Perform thorough EDA"]

        # Constraint-based adjustments
        if "interpretable" in constraints or "explainable" in constraints:
            if "Neural Network" in insights["recommended_models"]:
                insights["recommended_models"].remove("Neural Network")
            insights["recommended_models"].insert(0, "Logistic Regression")
            insights["challenges"].append("Need model interpretability")
            insights["mitigation"].append("Use SHAP/LIME for explanations")

        if "fast" in constraints or "real-time" in constraints or "<" in constraints:
            insights["challenges"].append("Low-latency requirement")
            insights["mitigation"].append("Use lightweight models, consider edge deployment")

        if "gpu" not in context.get("budget", "").lower():
            insights["challenges"].append("Limited compute (CPU only)")
            insights["mitigation"].append("Optimize model size, use efficient algorithms")

        return insights

    def get_context_prompt(self, context: Dict[str, Any]) -> str:
        """
        Generate a detailed prompt for LLM based on business context.

        This prompt will guide data cleaning, feature engineering, and model selection.
        """
        insights = self.get_insights(context)

        prompt = f"""
You are an expert ML engineer tasked with building a model for the following business problem:

BUSINESS CONTEXT:
- Goal: {context['prediction_goal']}
- Domain: {context['domain']}
- Target Audience: {context['target_audience']}
- Success Metric: {context['success_metric']}
- Constraints: {context['constraints']}
- Special Requirements: {context['special_requirements']}
- Available Resources: {context['budget']}

RECOMMENDED APPROACH:
- Models: {', '.join(insights['recommended_models'])}
- Optimize For: {', '.join(insights['optimization_targets'])}
- Key Challenges: {', '.join(insights['challenges'])}
- Mitigation Strategies: {', '.join(insights['mitigation'])}

INSTRUCTIONS:
1. Focus on data quality first - handle missing values appropriately for the domain
2. Create features that are meaningful for {context['domain']}
3. Prioritize {insights['optimization_targets'][0]} as the primary metric
4. Consider {', '.join(insights['challenges'][:2])} during model building
5. Apply {insights['mitigation'][0]}

Proceed with thorough analysis and report your findings.
"""
        return prompt.strip()


# Export
__all__ = ["BusinessContextManager"]
