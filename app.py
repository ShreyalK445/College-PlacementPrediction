"""
College Placement Prediction — Production Flask Application

Industry-ready REST API with:
- Structured JSON logging with correlation IDs
- Input validation via Pydantic
- Rate limiting & CORS
- API key authentication
- Swagger/OpenAPI docs
- Health, readiness, and metrics endpoints
- Prediction audit logging
"""

import json
import logging
import os
import pickle
import time
import uuid
from datetime import datetime, timezone
from functools import wraps
from threading import Lock

import pandas as pd
from flasgger import Swagger
from flask import Flask, g, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pydantic import BaseModel, Field, ValidationError, field_validator

from config import get_config
from models import init_db
from auth_service import seed_default_users
from api_routes import api_bp
from explainability import TreePathExplainer

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------


def create_app(config=None):
    """Application factory — creates and configures the Flask app."""

    app = Flask(__name__)

    # Initialize persistent storage & default demo users
    init_db()
    seed_default_users()

    # Load configuration
    cfg = config or get_config()
    app.config.from_object(cfg)

    # -----------------------------------------------------------------------
    # Logging
    # -----------------------------------------------------------------------
    _setup_logging(app, cfg)

    # -----------------------------------------------------------------------
    # Extensions
    # -----------------------------------------------------------------------
    CORS(app, origins=cfg.CORS_ORIGINS.split(","))
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[cfg.RATE_LIMIT],
        storage_uri="memory://",
    )

    # Swagger / OpenAPI
    app.config["SWAGGER"] = {
        "title": "College Placement Prediction API",
        "version": "2.0.0",
        "description": "Industry-ready ML prediction service",
        "termsOfService": "",
    }
    Swagger(app)

    # -----------------------------------------------------------------------
    # Model loading
    # -----------------------------------------------------------------------
    model_store = {"model": None, "metadata": None}
    model_lock = Lock()

    def _load_model():
        if os.path.exists(cfg.MODEL_PATH):
            with open(cfg.MODEL_PATH, "rb") as f:
                model_store["model"] = pickle.load(f)
            app.logger.info("Model loaded from %s", cfg.MODEL_PATH)
        else:
            app.logger.warning("model.pkl not found at %s", cfg.MODEL_PATH)

        if os.path.exists(cfg.MODEL_METADATA_PATH):
            with open(cfg.MODEL_METADATA_PATH, "r") as f:
                model_store["metadata"] = json.load(f)
            app.logger.info("Model metadata loaded")

        app.config["ML_MODEL"] = model_store["model"]

    _load_model()

    # Register extended career intelligence blueprint
    app.register_blueprint(api_bp)

    # -----------------------------------------------------------------------
    # Metrics store (in-memory; swap with Prometheus/StatsD in production)
    # -----------------------------------------------------------------------
    metrics = {
        "requests_total": 0,
        "predictions_total": 0,
        "errors_total": 0,
        "latency_sum_ms": 0.0,
        "started_at": datetime.now(timezone.utc).isoformat(),
    }
    metrics_lock = Lock()

    # -----------------------------------------------------------------------
    # Middleware
    # -----------------------------------------------------------------------
    @app.before_request
    def _before_request():
        g.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        g.start_time = time.perf_counter()
        with metrics_lock:
            metrics["requests_total"] += 1

    @app.after_request
    def _after_request(response):
        elapsed_ms = (time.perf_counter() - g.start_time) * 1000
        with metrics_lock:
            metrics["latency_sum_ms"] += elapsed_ms
        response.headers["X-Request-ID"] = g.request_id
        response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.2f}"
        app.logger.info(
            "request_id=%s method=%s path=%s status=%s latency_ms=%.2f",
            g.request_id,
            request.method,
            request.path,
            response.status_code,
            elapsed_ms,
        )
        return response

    # -----------------------------------------------------------------------
    # Auth helper
    # -----------------------------------------------------------------------
    def require_api_key(f):
        """Decorator that enforces API key auth when API_KEY is configured."""

        @wraps(f)
        def decorated(*args, **kwargs):
            if cfg.API_KEY:
                provided = request.headers.get("X-API-Key", "")
                if provided != cfg.API_KEY:
                    return jsonify(
                        {"error": "Unauthorized — invalid or missing API key"}
                    ), 401
            return f(*args, **kwargs)

        return decorated

    # -----------------------------------------------------------------------
    # Pydantic validation models
    # -----------------------------------------------------------------------
    class PredictionInput(BaseModel):
        """Validates and constrains a single prediction request."""

        IQ: float = Field(..., ge=50, le=200, description="Student IQ score (50–200)")
        Prev_Sem_Result: float = Field(
            ..., ge=0, le=10, description="Previous semester GPA (0–10)"
        )
        CGPA: float = Field(..., ge=0, le=10, description="Cumulative GPA (0–10)")
        Academic_Performance: int = Field(
            ..., ge=1, le=10, description="Academic rating (1–10)"
        )
        Extra_Curricular_Score: int = Field(
            ..., ge=1, le=10, description="Extracurricular rating (1–10)"
        )
        Communication_Skills: int = Field(
            ..., ge=1, le=10, description="Communication rating (1–10)"
        )
        Projects_Completed: int = Field(
            ..., ge=0, le=50, description="Number of projects (0–50)"
        )
        Internship_Experience: float = Field(
            ..., ge=0, le=1, description="Internship (0=No, 1=Yes)"
        )

        @field_validator("Internship_Experience")
        @classmethod
        def validate_internship(cls, v):
            if v not in (0, 0.0, 1, 1.0):
                raise ValueError("Internship_Experience must be 0 or 1")
            return float(v)

    # -----------------------------------------------------------------------
    # Routes
    # -----------------------------------------------------------------------

    @app.route("/predict", methods=["POST"])
    @require_api_key
    @limiter.limit(cfg.RATE_LIMIT)
    def predict():
        """Predict student placement status.
        ---
        tags:
          - Prediction
        consumes:
          - application/json
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                IQ:
                  type: number
                  example: 120
                Prev_Sem_Result:
                  type: number
                  example: 7.97
                CGPA:
                  type: number
                  example: 7.76
                Academic_Performance:
                  type: integer
                  example: 6
                Extra_Curricular_Score:
                  type: integer
                  example: 9
                Communication_Skills:
                  type: integer
                  example: 9
                Projects_Completed:
                  type: integer
                  example: 2
                Internship_Experience:
                  type: number
                  example: 1.0
        responses:
          200:
            description: Prediction result
          400:
            description: Validation error
          401:
            description: Unauthorized
          500:
            description: Server error
        """
        with model_lock:
            model = model_store["model"]

        if model is None:
            # Attempt lazy reload
            _load_model()
            model = model_store["model"]
            if model is None:
                with metrics_lock:
                    metrics["errors_total"] += 1
                return jsonify(
                    {"error": "Model not loaded. Run model_building.py first."}
                ), 500

        # Parse JSON
        try:
            data = request.get_json(force=True)
        except Exception:
            with metrics_lock:
                metrics["errors_total"] += 1
            return jsonify({"error": "Invalid JSON payload"}), 400

        # Normalize to list for uniform processing
        is_single = isinstance(data, dict)
        items = [data] if is_single else data

        if not isinstance(items, list):
            return jsonify(
                {"error": "Payload must be a JSON object or array of objects"}
            ), 400

        # Validate each item through Pydantic
        validated = []
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                return jsonify(
                    {"error": f"Item at index {idx} is not a JSON object"}
                ), 400
            try:
                obj = PredictionInput(**item)
                validated.append(obj.model_dump())
            except ValidationError as e:
                # Convert Pydantic errors to JSON-safe dicts
                safe_errors = []
                for err in e.errors():
                    safe_err = {
                        k: str(v)
                        if not isinstance(v, (str, int, float, bool, list, type(None)))
                        else v
                        for k, v in err.items()
                    }
                    safe_errors.append(safe_err)
                return jsonify(
                    {
                        "error": f"Validation failed for item {idx}",
                        "details": safe_errors,
                    }
                ), 400

        # Build DataFrame in training feature order
        input_df = pd.DataFrame(validated)[cfg.FEATURE_NAMES]

        try:
            predictions = model.predict(input_df)
            probabilities = (
                model.predict_proba(input_df)[:, 1]
                if hasattr(model, "predict_proba")
                else None
            )
        except Exception as exc:
            app.logger.exception("Prediction error: %s", exc)
            with metrics_lock:
                metrics["errors_total"] += 1
            return jsonify({"error": f"Prediction failed: {str(exc)}"}), 500

        results = []
        for i, pred in enumerate(predictions):
            res = {
                "placement_prediction": int(pred),
                "status": "Placed" if int(pred) == 1 else "Not Placed",
            }
            if probabilities is not None:
                res["placement_probability"] = round(float(probabilities[i]), 4)
            results.append(res)

        # Optional explainability for single predictions
        if is_single and (
            request.args.get("explain") == "true"
            or (isinstance(data, dict) and data.get("explain"))
        ):
            try:
                explainer = TreePathExplainer(model, cfg.FEATURE_NAMES)
                results[0]["explainability"] = explainer.explain_instance(input_df)
            except Exception as exc:
                app.logger.warning("Explainability generation failed: %s", exc)

        with metrics_lock:
            metrics["predictions_total"] += len(results)

        # Audit log
        app.logger.info(
            "prediction request_id=%s count=%d results=%s",
            g.request_id,
            len(results),
            json.dumps(results),
        )

        return jsonify(
            {
                "request_id": g.request_id,
                "results": results[0] if is_single else results,
            }
        )

    @app.route("/explain", methods=["POST"])
    def root_explain():
        """Root alias for /api/explain."""
        return api_bp.view_functions["explain_prediction"]()

    # -----------------------------------------------------------------------
    # Health / Readiness / Metrics
    # -----------------------------------------------------------------------

    @app.route("/health", methods=["GET"])
    def health():
        """Liveness probe — always returns 200 if the process is alive.
        ---
        tags:
          - Operations
        responses:
          200:
            description: Service is alive
        """
        return jsonify(
            {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}
        )

    @app.route("/ready", methods=["GET"])
    def ready():
        """Readiness probe — returns 200 only when the model is loaded.
        ---
        tags:
          - Operations
        responses:
          200:
            description: Service is ready
          503:
            description: Service is not ready
        """
        model_loaded = model_store["model"] is not None
        status_code = 200 if model_loaded else 503
        return jsonify(
            {
                "ready": model_loaded,
                "model_loaded": model_loaded,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ), status_code

    @app.route("/metrics", methods=["GET"])
    @require_api_key
    def app_metrics():
        """Basic application metrics.
        ---
        tags:
          - Operations
        responses:
          200:
            description: Application metrics
        """
        with metrics_lock:
            avg_latency = (
                metrics["latency_sum_ms"] / metrics["requests_total"]
                if metrics["requests_total"] > 0
                else 0
            )
            return jsonify(
                {
                    "requests_total": metrics["requests_total"],
                    "predictions_total": metrics["predictions_total"],
                    "errors_total": metrics["errors_total"],
                    "avg_latency_ms": round(avg_latency, 2),
                    "uptime_since": metrics["started_at"],
                }
            )

    # -----------------------------------------------------------------------
    # Model information
    # -----------------------------------------------------------------------

    @app.route("/model/info", methods=["GET"])
    def model_info():
        """Return model metadata, version, and feature importance.
        ---
        tags:
          - Model
        responses:
          200:
            description: Model information
          404:
            description: No metadata available
        """
        metadata = model_store.get("metadata")
        model = model_store.get("model")

        info = {}
        if metadata:
            info.update(metadata)

        # Add live feature importance if model supports it
        if model is not None and hasattr(model, "feature_importances_"):
            importances = dict(
                zip(
                    cfg.FEATURE_NAMES,
                    [round(float(x), 4) for x in model.feature_importances_],
                )
            )
            info["feature_importance"] = dict(
                sorted(importances.items(), key=lambda x: x[1], reverse=True)
            )

        if not info:
            return jsonify({"error": "No model metadata available"}), 404

        return jsonify(info)

    # -----------------------------------------------------------------------
    # Reload model (for hot-swapping without restart)
    # -----------------------------------------------------------------------

    @app.route("/model/reload", methods=["POST"])
    @require_api_key
    def reload_model():
        """Reload the model from disk without restarting.
        ---
        tags:
          - Model
        responses:
          200:
            description: Model reloaded successfully
          500:
            description: Reload failed
        """
        try:
            with model_lock:
                _load_model()
            return jsonify({"status": "Model reloaded successfully"})
        except Exception as exc:
            app.logger.exception("Model reload failed: %s", exc)
            return jsonify({"error": f"Reload failed: {str(exc)}"}), 500

    # -----------------------------------------------------------------------
    # Direct /api route aliases for unified frontend routing
    # -----------------------------------------------------------------------
    @app.route("/api/predict", methods=["POST"])
    def api_predict():
        return predict()

    @app.route("/api/health", methods=["GET"])
    def api_health():
        return health()

    @app.route("/api/ready", methods=["GET"])
    def api_ready():
        return ready()

    @app.route("/api/metrics", methods=["GET"])
    def api_metrics():
        return app_metrics()

    @app.route("/api/model/info", methods=["GET"])
    def api_model_info():
        return model_info()

    # -----------------------------------------------------------------------
    # Error handlers
    # -----------------------------------------------------------------------

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Endpoint not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(429)
    def rate_limited(e):
        return jsonify({"error": "Rate limit exceeded. Please slow down."}), 429

    @app.errorhandler(500)
    def internal_error(e):
        with metrics_lock:
            metrics["errors_total"] += 1
        return jsonify({"error": "Internal server error"}), 500

    return app


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------


def _setup_logging(app, cfg):
    """Configure structured JSON logging for production."""

    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }
            if record.exc_info and record.exc_info[0]:
                log_record["exception"] = self.formatException(record.exc_info)
            return json.dumps(log_record)

    handler = logging.StreamHandler()
    env = os.getenv("FLASK_ENV", "development")
    if env == "production":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
        )

    app.logger.handlers.clear()
    app.logger.addHandler(handler)
    app.logger.setLevel(getattr(logging, cfg.LOG_LEVEL, logging.INFO))


# ---------------------------------------------------------------------------
# Direct execution
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    application = create_app()
    cfg = get_config()
    application.run(host=cfg.HOST, port=cfg.PORT, debug=cfg.DEBUG)
