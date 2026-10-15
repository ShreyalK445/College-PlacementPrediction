"""
Unit tests for model loading and prediction logic.
"""

import os
import pickle

import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestClassifier


class TestModelLoading:
    """Tests for model serialization and loading."""

    def test_model_file_exists(self, dummy_model):
        model_path, _ = dummy_model
        assert os.path.exists(model_path)

    def test_model_is_deserializable(self, dummy_model):
        model_path, _ = dummy_model
        with open(model_path, "rb") as f:
            model = pickle.load(f)
        assert model is not None
        assert isinstance(model, RandomForestClassifier)

    def test_model_has_predict(self, dummy_model):
        model_path, _ = dummy_model
        with open(model_path, "rb") as f:
            model = pickle.load(f)
        assert hasattr(model, "predict")
        assert hasattr(model, "predict_proba")

    def test_model_has_feature_importances(self, dummy_model):
        model_path, _ = dummy_model
        with open(model_path, "rb") as f:
            model = pickle.load(f)
        assert hasattr(model, "feature_importances_")
        assert len(model.feature_importances_) == 8


class TestModelPrediction:
    """Tests for prediction correctness."""

    def test_single_prediction_returns_binary(self, dummy_model):
        model_path, _ = dummy_model
        with open(model_path, "rb") as f:
            model = pickle.load(f)

        X = np.random.rand(1, 8)
        pred = model.predict(X)
        assert pred[0] in (0, 1)

    def test_batch_prediction_returns_correct_shape(self, dummy_model):
        model_path, _ = dummy_model
        with open(model_path, "rb") as f:
            model = pickle.load(f)

        X = np.random.rand(10, 8)
        preds = model.predict(X)
        assert len(preds) == 10

    def test_predict_proba_sums_to_one(self, dummy_model):
        model_path, _ = dummy_model
        with open(model_path, "rb") as f:
            model = pickle.load(f)

        X = np.random.rand(5, 8)
        proba = model.predict_proba(X)
        for row in proba:
            assert abs(sum(row) - 1.0) < 1e-6

    def test_prediction_with_dataframe(self, dummy_model):
        model_path, _ = dummy_model
        with open(model_path, "rb") as f:
            model = pickle.load(f)

        df = pd.DataFrame(
            np.random.rand(3, 8),
            columns=[
                "IQ", "Prev_Sem_Result", "CGPA", "Academic_Performance",
                "Extra_Curricular_Score", "Communication_Skills",
                "Projects_Completed", "Internship_Experience",
            ],
        )
        preds = model.predict(df)
        assert len(preds) == 3


class TestMetadata:
    """Tests for model metadata."""

    def test_metadata_file_exists(self, dummy_model):
        _, metadata_path = dummy_model
        assert os.path.exists(metadata_path)

    def test_metadata_is_valid_json(self, dummy_model):
        import json

        _, metadata_path = dummy_model
        with open(metadata_path, "r") as f:
            data = json.load(f)
        assert isinstance(data, dict)
        assert "model_version" in data
        assert "evaluation" in data
