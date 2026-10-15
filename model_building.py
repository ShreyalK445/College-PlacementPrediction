"""
Enhanced Model Training Pipeline — College Placement Prediction

Industry-grade training script with:
- Cross-validation
- Hyperparameter tuning (GridSearchCV)
- Model versioning with metadata JSON
- Training artifact export (confusion matrix, classification report, feature importance)
- Structured logging
"""

import json
import logging
import os
import pickle
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "College_placement.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
METADATA_PATH = os.path.join(BASE_DIR, "model_metadata.json")
ARTIFACTS_DIR = os.path.join(BASE_DIR, "training_artifacts")

os.makedirs(ARTIFACTS_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Load & validate data
# ---------------------------------------------------------------------------
logger.info("Loading dataset from: %s", CSV_PATH)
if not os.path.exists(CSV_PATH):
    logger.error("Dataset not found at %s", CSV_PATH)
    sys.exit(1)

df = pd.read_csv(CSV_PATH)

# Drop unnamed index column if present
if df.columns[0] == "" or df.columns[0].startswith("Unnamed"):
    df = df.iloc[:, 1:]

logger.info("Dataset shape: %d rows × %d columns", *df.shape)
logger.info("Columns: %s", list(df.columns))
logger.info("Target distribution:\n%s", df["Placement"].value_counts().to_string())

# Check for missing values
missing = df.isnull().sum()
if missing.any():
    logger.warning("Missing values detected:\n%s", missing[missing > 0].to_string())
    logger.info("Dropping rows with missing values")
    df = df.dropna()

# ---------------------------------------------------------------------------
# 2. Feature / target split
# ---------------------------------------------------------------------------
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

X = df[FEATURE_NAMES]
y = df["Placement"]

# ---------------------------------------------------------------------------
# 3. Train / test split (stratified)
# ---------------------------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
logger.info("Train set: %d samples | Test set: %d samples", len(X_train), len(X_test))

# ---------------------------------------------------------------------------
# 4. Hyperparameter tuning with cross-validation
# ---------------------------------------------------------------------------
logger.info("Starting hyperparameter search with 5-fold stratified CV...")

param_grid = {
    "n_estimators": [100, 200, 300],
    "max_depth": [None, 10, 20, 30],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf": [1, 2, 4],
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

grid_search = GridSearchCV(
    estimator=RandomForestClassifier(random_state=42, n_jobs=-1),
    param_grid=param_grid,
    cv=cv,
    scoring="f1",
    n_jobs=-1,
    verbose=1,
    return_train_score=True,
)

grid_search.fit(X_train, y_train)

best_model = grid_search.best_estimator_
logger.info("Best parameters: %s", grid_search.best_params_)
logger.info("Best CV F1 score: %.4f", grid_search.best_score_)

# ---------------------------------------------------------------------------
# 5. Evaluate on hold-out test set
# ---------------------------------------------------------------------------
y_pred = best_model.predict(X_test)
y_proba = best_model.predict_proba(X_test)[:, 1]

test_accuracy = accuracy_score(y_test, y_pred)
test_precision = precision_score(y_test, y_pred)
test_recall = recall_score(y_test, y_pred)
test_f1 = f1_score(y_test, y_pred)
test_auc = roc_auc_score(y_test, y_proba)

logger.info("=" * 50)
logger.info("Test Set Evaluation")
logger.info("=" * 50)
logger.info("Accuracy:  %.4f", test_accuracy)
logger.info("Precision: %.4f", test_precision)
logger.info("Recall:    %.4f", test_recall)
logger.info("F1 Score:  %.4f", test_f1)
logger.info("AUC-ROC:   %.4f", test_auc)

report = classification_report(y_test, y_pred, output_dict=True)
cm = confusion_matrix(y_test, y_pred)

logger.info("Classification Report:\n%s", classification_report(y_test, y_pred))
logger.info("Confusion Matrix:\n%s", cm)

# ---------------------------------------------------------------------------
# 6. Feature importance
# ---------------------------------------------------------------------------
importances = best_model.feature_importances_
feature_importance = dict(
    sorted(
        zip(FEATURE_NAMES, [round(float(x), 4) for x in importances]),
        key=lambda x: x[1],
        reverse=True,
    )
)
logger.info("Feature Importance:")
for feat, imp in feature_importance.items():
    logger.info("  %-25s %.4f", feat, imp)

# ---------------------------------------------------------------------------
# 7. Save model
# ---------------------------------------------------------------------------
logger.info("Saving model to: %s", MODEL_PATH)
with open(MODEL_PATH, "wb") as f:
    pickle.dump(best_model, f, protocol=pickle.HIGHEST_PROTOCOL)

# ---------------------------------------------------------------------------
# 8. Save model metadata (versioned)
# ---------------------------------------------------------------------------
metadata = {
    "model_version": datetime.now(timezone.utc).strftime("v%Y%m%d-%H%M%S"),
    "model_type": "RandomForestClassifier",
    "trained_at": datetime.now(timezone.utc).isoformat(),
    "python_version": sys.version,
    "sklearn_version": pd.io.formats.printing.pprint_thing(
        __import__("sklearn").__version__
    ),
    "dataset": {
        "path": CSV_PATH,
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "features": FEATURE_NAMES,
    },
    "training": {
        "test_size": 0.2,
        "cv_folds": 5,
        "best_params": grid_search.best_params_,
        "best_cv_f1": round(grid_search.best_score_, 4),
    },
    "evaluation": {
        "accuracy": round(test_accuracy, 4),
        "precision": round(test_precision, 4),
        "recall": round(test_recall, 4),
        "f1_score": round(test_f1, 4),
        "auc_roc": round(test_auc, 4),
        "confusion_matrix": cm.tolist(),
    },
    "feature_importance": feature_importance,
}

logger.info("Saving metadata to: %s", METADATA_PATH)
with open(METADATA_PATH, "w") as f:
    json.dump(metadata, f, indent=2, default=str)

# ---------------------------------------------------------------------------
# 9. Save training artifacts
# ---------------------------------------------------------------------------
# Classification report
report_path = os.path.join(ARTIFACTS_DIR, "classification_report.json")
with open(report_path, "w") as f:
    json.dump(report, f, indent=2)

# Confusion matrix
cm_path = os.path.join(ARTIFACTS_DIR, "confusion_matrix.json")
with open(cm_path, "w") as f:
    json.dump({"matrix": cm.tolist(), "labels": ["Not Placed", "Placed"]}, f, indent=2)

# Feature importance
fi_path = os.path.join(ARTIFACTS_DIR, "feature_importance.json")
with open(fi_path, "w") as f:
    json.dump(feature_importance, f, indent=2)

# CV results summary
cv_path = os.path.join(ARTIFACTS_DIR, "cv_results_summary.json")
cv_results = pd.DataFrame(grid_search.cv_results_)
cv_summary = cv_results[["params", "mean_test_score", "std_test_score", "rank_test_score"]]
cv_summary = cv_summary.sort_values("rank_test_score").head(10)
with open(cv_path, "w") as f:
    json.dump(cv_summary.to_dict(orient="records"), f, indent=2, default=str)

logger.info("Training artifacts saved to: %s", ARTIFACTS_DIR)
logger.info("=" * 50)
logger.info("✅ Model training pipeline complete!")
logger.info("=" * 50)
