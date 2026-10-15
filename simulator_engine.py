"""
What-If Placement Simulator Engine
Simulates hypothetical improvements in student credentials and computes probability deltas.
"""

from typing import Dict, Any, List
import pandas as pd
from explainability import TreePathExplainer, FEATURE_NAMES, FEATURE_LABELS

def run_simulation(model, baseline_inputs: Dict[str, Any], hypothetical_inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compares baseline vs hypothetical scenarios.
    Returns delta in probability, status transitions, and driver feature shifts.
    """
    explainer = TreePathExplainer(model, FEATURE_NAMES)

    # Prepare DataFrames
    base_df = pd.DataFrame([baseline_inputs])[FEATURE_NAMES]
    hypo_df = pd.DataFrame([hypothetical_inputs])[FEATURE_NAMES]

    base_explanation = explainer.explain_instance(base_df)
    hypo_explanation = explainer.explain_instance(hypo_df)

    base_proba = base_explanation["predicted_probability"]
    hypo_proba = hypo_explanation["predicted_probability"]
    delta_proba = round(hypo_proba - base_proba, 4)
    delta_percentage = round(delta_proba * 100, 2)

    base_status = base_explanation["predicted_status"]
    hypo_status = hypo_explanation["predicted_status"]

    # Identify modified features
    modified_features = []
    for feat in FEATURE_NAMES:
        b_val = float(baseline_inputs[feat])
        h_val = float(hypothetical_inputs[feat])
        if abs(h_val - b_val) > 1e-4:
            modified_features.append({
                "feature": feat,
                "label": FEATURE_LABELS.get(feat, feat),
                "original_value": b_val,
                "hypothetical_value": h_val,
                "delta_value": round(h_val - b_val, 2),
                "base_contribution": base_explanation["feature_contributions"].get(feat, 0),
                "hypo_contribution": hypo_explanation["feature_contributions"].get(feat, 0),
                "delta_contribution": round(
                    hypo_explanation["feature_contributions"].get(feat, 0)
                    - base_explanation["feature_contributions"].get(feat, 0),
                    4
                ),
            })

    # Summary insight
    status_transition = "No Change"
    if base_status == "Not Placed" and hypo_status == "Placed":
        status_transition = "Positive Transition: At-Risk → Placed 🎉"
    elif base_status == "Placed" and hypo_status == "Not Placed":
        status_transition = "Negative Transition: Placed → At-Risk ⚠️"

    insights = []
    if delta_percentage > 0:
        insights.append(f"This scenario yields a +{delta_percentage}% boost in estimated placement probability.")
        # Find which modified feature produced the biggest positive delta contribution
        if modified_features:
            best_feat = max(modified_features, key=lambda x: x["delta_contribution"])
            if best_feat["delta_contribution"] > 0:
                insights.append(f"The largest single gain came from improving {best_feat['label']} (+{round(best_feat['delta_contribution']*100, 1)}% impact).")
    elif delta_percentage < 0:
        insights.append(f"This scenario reduces estimated placement probability by {abs(delta_percentage)}%.")
    else:
        insights.append("Adjustments made in this scenario resulted in no net change in model confidence.")

    return {
        "baseline": {
            "probability": base_proba,
            "status": base_status,
            "inputs": baseline_inputs,
        },
        "hypothetical": {
            "probability": hypo_proba,
            "status": hypo_status,
            "inputs": hypothetical_inputs,
        },
        "delta": {
            "probability_delta": delta_proba,
            "percentage_delta": delta_percentage,
            "status_transition": status_transition,
        },
        "modified_features": modified_features,
        "insights": insights,
        "disclaimer": (
            "Hypothetical simulation models marginal changes in algorithmic confidence scores. "
            "It does not represent a causal certainty or guarantee of real-world hiring outcomes."
        ),
    }
