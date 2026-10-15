"""
Pytest fixtures for the College Placement Prediction test suite.
"""

import os
import pickle
import json

import pytest
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# Ensure we're in test/development mode
os.environ["FLASK_ENV"] = "development"
os.environ["API_KEY"] = "test-api-key-12345"


@pytest.fixture(scope="session")
def dummy_model(tmp_path_factory):
    """Create a minimal trained RandomForest model for testing."""
    np.random.seed(42)
    X = np.random.rand(100, 8)
    y = (X[:, 2] > 0.5).astype(int)  # Simple rule based on CGPA-like feature

    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)

    model_dir = tmp_path_factory.mktemp("models")
    model_path = model_dir / "model.pkl"
    metadata_path = model_dir / "model_metadata.json"

    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    metadata = {
        "model_version": "v20261015-test",
        "model_type": "RandomForestClassifier",
        "trained_at": "2026-10-15T00:00:00+00:00",
        "evaluation": {
            "accuracy": 0.95,
            "precision": 0.94,
            "recall": 0.96,
            "f1_score": 0.95,
            "auc_roc": 0.98,
        },
        "feature_importance": {
            "CGPA": 0.35,
            "IQ": 0.15,
            "Prev_Sem_Result": 0.12,
            "Academic_Performance": 0.10,
            "Communication_Skills": 0.08,
            "Extra_Curricular_Score": 0.08,
            "Projects_Completed": 0.07,
            "Internship_Experience": 0.05,
        },
    }
    with open(metadata_path, "w") as f:
        json.dump(metadata, f)

    return str(model_path), str(metadata_path)


@pytest.fixture
def app(dummy_model):
    """Create a Flask test app with the dummy model."""
    model_path, metadata_path = dummy_model

    os.environ["MODEL_PATH"] = model_path
    os.environ["MODEL_METADATA_PATH"] = metadata_path

    # Patch config paths before importing
    from config import get_config

    cfg = get_config()
    cfg.MODEL_PATH = model_path
    cfg.MODEL_METADATA_PATH = metadata_path

    from app import create_app

    application = create_app(config=cfg)
    application.config["TESTING"] = True

    yield application


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def auth_headers():
    """Headers with valid API key."""
    return {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key-12345",
    }


@pytest.fixture
def valid_payload():
    """A valid single prediction payload."""
    return {
        "IQ": 120,
        "Prev_Sem_Result": 7.97,
        "CGPA": 7.76,
        "Academic_Performance": 6,
        "Extra_Curricular_Score": 9,
        "Communication_Skills": 9,
        "Projects_Completed": 2,
        "Internship_Experience": 1.0,
    }


@pytest.fixture
def valid_batch_payload():
    """A valid batch prediction payload."""
    return [
        {
            "IQ": 120,
            "Prev_Sem_Result": 7.97,
            "CGPA": 7.76,
            "Academic_Performance": 6,
            "Extra_Curricular_Score": 9,
            "Communication_Skills": 9,
            "Projects_Completed": 2,
            "Internship_Experience": 1.0,
        },
        {
            "IQ": 101,
            "Prev_Sem_Result": 8.34,
            "CGPA": 7.87,
            "Academic_Performance": 9,
            "Extra_Curricular_Score": 7,
            "Communication_Skills": 9,
            "Projects_Completed": 3,
            "Internship_Experience": 0.0,
        },
    ]
