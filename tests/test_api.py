"""
Integration tests for the Flask API endpoints.
"""

import json


class TestHealthEndpoints:
    """Tests for operational endpoints."""

    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_ready_returns_200_when_model_loaded(self, client):
        response = client.get("/ready")
        assert response.status_code == 200
        data = response.get_json()
        assert data["ready"] is True
        assert data["model_loaded"] is True

    def test_metrics_requires_api_key(self, client):
        response = client.get("/metrics")
        assert response.status_code == 401

    def test_metrics_returns_data_with_api_key(self, client, auth_headers):
        response = client.get("/metrics", headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert "requests_total" in data
        assert "predictions_total" in data
        assert "errors_total" in data
        assert "avg_latency_ms" in data


class TestPredictionEndpoint:
    """Tests for the /predict endpoint."""

    def test_single_prediction_success(self, client, auth_headers, valid_payload):
        response = client.post(
            "/predict",
            data=json.dumps(valid_payload),
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.get_json()
        assert "results" in data
        assert "request_id" in data
        result = data["results"]
        assert "placement_prediction" in result
        assert result["status"] in ("Placed", "Not Placed")
        assert "placement_probability" in result

    def test_batch_prediction_success(self, client, auth_headers, valid_batch_payload):
        response = client.post(
            "/predict",
            data=json.dumps(valid_batch_payload),
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.get_json()
        results = data["results"]
        assert isinstance(results, list)
        assert len(results) == 2

    def test_missing_features_returns_400(self, client, auth_headers):
        payload = {"IQ": 120}  # Missing most features
        response = client.post(
            "/predict",
            data=json.dumps(payload),
            headers=auth_headers,
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_invalid_iq_range_returns_400(self, client, auth_headers, valid_payload):
        payload = valid_payload.copy()
        payload["IQ"] = 999  # Out of range
        response = client.post(
            "/predict",
            data=json.dumps(payload),
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_invalid_cgpa_range_returns_400(self, client, auth_headers, valid_payload):
        payload = valid_payload.copy()
        payload["CGPA"] = -1  # Negative
        response = client.post(
            "/predict",
            data=json.dumps(payload),
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_invalid_internship_value_returns_400(
        self, client, auth_headers, valid_payload
    ):
        payload = valid_payload.copy()
        payload["Internship_Experience"] = 0.5  # Must be 0 or 1
        response = client.post(
            "/predict",
            data=json.dumps(payload),
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_invalid_json_returns_400(self, client, auth_headers):
        response = client.post(
            "/predict",
            data="not valid json{{{",
            headers=auth_headers,
        )
        # Flask's force=True may still parse; this tests error handling
        assert response.status_code in (400, 500)

    def test_predict_without_api_key_returns_401(self, client, valid_payload):
        response = client.post(
            "/predict",
            data=json.dumps(valid_payload),
            content_type="application/json",
        )
        assert response.status_code == 401

    def test_response_includes_request_id(self, client, auth_headers, valid_payload):
        response = client.post(
            "/predict",
            data=json.dumps(valid_payload),
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        data = response.get_json()
        assert "request_id" in data


class TestModelEndpoints:
    """Tests for model info and management endpoints."""

    def test_model_info_returns_metadata(self, client):
        response = client.get("/model/info")
        assert response.status_code == 200
        data = response.get_json()
        assert "model_version" in data

    def test_model_reload_requires_api_key(self, client):
        response = client.post("/model/reload")
        assert response.status_code == 401

    def test_model_reload_with_api_key(self, client, auth_headers):
        response = client.post("/model/reload", headers=auth_headers)
        assert response.status_code == 200


class TestErrorHandlers:
    """Tests for error handlers."""

    def test_404_returns_json(self, client):
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data

    def test_method_not_allowed_returns_json(self, client):
        response = client.get("/predict")  # GET not allowed
        assert response.status_code == 405
        data = response.get_json()
        assert "error" in data
