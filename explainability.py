"""
Explainable AI Engine — Tree Path Attribution & Feature Contributions
Compatible with scikit-learn tree ensembles (RandomForestClassifier).
Provides local sample-level feature attributions that sum to model output.
"""

from typing import Dict, List, Any
import numpy as np
import pandas as pd

FEATURE_NAMES = [
    "IQ",
    "Prev_Sem_Result",
    "CGPA",
    "Academic_Performance",
    "Extra_Curricular_Score",
    "Communication_Skills",
    "Projects_Completed",
    "Internship_Experience",
]

FEATURE_LABELS = {
    "IQ": "Cognitive Aptitude (IQ)",
    "Prev_Sem_Result": "Previous Semester GPA",
    "CGPA": "Cumulative GPA",
    "Academic_Performance": "Academic Rating",
    "Extra_Curricular_Score": "Extra-Curricular Score",
    "Communication_Skills": "Communication Skills",
    "Projects_Completed": "Projects Completed",
    "Internship_Experience": "Internship Experience",
}


class TreePathExplainer:
    """
    Exact decision-path tree interpreter for scikit-learn Random Forests.
    Decomposes the prediction along tree decision paths into exact feature contributions.
    Guaranteed identity: base_value + sum(contributions) == predicted_probability.
    """

    def __init__(self, model, feature_names: List[str] = None):
        self.model = model
        self.feature_names = feature_names or FEATURE_NAMES

    def explain_instance(self, sample_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Computes local feature contributions for a single student sample.
        """
        if not hasattr(self.model, "estimators_"):
            raise ValueError(
                "Model must be a fitted ensemble with estimators_ attribute"
            )

        X = sample_df[self.feature_names].values
        if len(X.shape) == 1:
            X = X.reshape(1, -1)

        n_features = len(self.feature_names)
        all_contribs = np.zeros(n_features)
        base_val = 0.0

        for tree in self.model.estimators_:
            t = tree.tree_
            # Root node class distribution (class 1 is Placed)
            root_p = t.value[0, 0, 1] / np.sum(t.value[0, 0])
            base_val += root_p

            node_indicator = tree.decision_path(X)
            node_index = node_indicator.indices

            for i in range(len(node_index) - 1):
                curr_node = node_index[i]
                next_node = node_index[i + 1]
                feat = t.feature[curr_node]
                p_curr = t.value[curr_node, 0, 1] / np.sum(t.value[curr_node, 0])
                p_next = t.value[next_node, 0, 1] / np.sum(t.value[next_node, 0])
                all_contribs[feat] += p_next - p_curr

        n_trees = len(self.model.estimators_)
        base_val /= n_trees
        all_contribs /= n_trees

        predicted_proba = float(self.model.predict_proba(X)[0, 1])
        predicted_class = int(self.model.predict(X)[0])

        # Construct contribution dictionary
        contrib_dict = {}
        for idx, feat_name in enumerate(self.feature_names):
            contrib_dict[feat_name] = round(float(all_contribs[idx]), 4)

        # Categorize positive vs negative contributions
        positives = []
        negatives = []
        for feat_name, val in contrib_dict.items():
            item = {
                "feature": feat_name,
                "label": FEATURE_LABELS.get(feat_name, feat_name),
                "contribution": val,
                "percentage_impact": round(val * 100, 2),
                "student_value": float(sample_df[feat_name].iloc[0]),
            }
            if val > 0.001:
                positives.append(item)
            elif val < -0.001:
                negatives.append(item)

        positives.sort(key=lambda x: x["contribution"], reverse=True)
        negatives.sort(key=lambda x: x["contribution"])  # most negative first

        # Generate narrative text
        narrative = self._generate_narrative(
            positives, negatives, predicted_class, predicted_proba
        )

        return {
            "method": "Exact Tree-Path Attribution (TreeInterpreter)",
            "base_value": round(float(base_val), 4),
            "predicted_probability": round(predicted_proba, 4),
            "predicted_status": "Placed" if predicted_class == 1 else "Not Placed",
            "feature_contributions": contrib_dict,
            "top_positive_factors": positives,
            "top_negative_factors": negatives,
            "narrative": narrative,
            "disclaimer": (
                "Feature contributions represent the mathematical decision path inside the Random Forest model "
                "for this specific candidate and should not be interpreted as definitive proof of real-world causation."
            ),
        }

    def _generate_narrative(self, positives, negatives, pred_class, proba) -> List[str]:
        lines = []
        prob_pct = round(proba * 100, 1)

        if pred_class == 1:
            lines.append(
                f"Candidate is classified as Placed with a model confidence of {prob_pct}%."
            )
            if positives:
                top_p = positives[0]
                lines.append(
                    f"The strongest factor boosting this outcome was {top_p['label']} (value: {top_p['student_value']}), contributing +{top_p['percentage_impact']}% toward placement."
                )
            if negatives:
                top_n = negatives[0]
                lines.append(
                    f"Conversely, {top_n['label']} was the primary drag, lowering probability by {abs(top_n['percentage_impact'])}%."
                )
        else:
            lines.append(
                f"Candidate is currently classified as At-Risk (predicted probability: {prob_pct}%)."
            )
            if negatives:
                top_n = negatives[0]
                lines.append(
                    f"The most substantial limiting factor was {top_n['label']} (value: {top_n['student_value']}), which reduced placement probability by {abs(top_n['percentage_impact'])}%."
                )
            if positives:
                top_p = positives[0]
                lines.append(
                    f"A notable positive strength was {top_p['label']} (value: {top_p['student_value']}), contributing +{top_p['percentage_impact']}%."
                )

        return lines
