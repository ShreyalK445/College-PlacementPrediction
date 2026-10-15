"""
Centralized configuration for the College Placement Prediction application.

Reads environment variables (with .env support) and exposes typed settings
for development, staging, and production environments.
"""

import os
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

# ---------------------------------------------------------------------------
# Base configuration
# ---------------------------------------------------------------------------


class BaseConfig:
    """Shared configuration across all environments."""

    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-to-a-random-secret")
    API_KEY = os.getenv("API_KEY", "")

    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))

    RATE_LIMIT = os.getenv("RATE_LIMIT", "60/minute")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_PATH = os.path.join(BASE_DIR, os.getenv("MODEL_PATH", "model.pkl"))
    MODEL_METADATA_PATH = os.path.join(
        BASE_DIR, os.getenv("MODEL_METADATA_PATH", "model_metadata.json")
    )

    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

    # Feature schema (single source of truth)
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


class DevelopmentConfig(BaseConfig):
    """Development-specific overrides."""

    DEBUG = True
    TESTING = False
    LOG_LEVEL = "DEBUG"


class StagingConfig(BaseConfig):
    """Staging-specific overrides."""

    DEBUG = False
    TESTING = False


class ProductionConfig(BaseConfig):
    """Production-specific overrides."""

    DEBUG = False
    TESTING = False


# ---------------------------------------------------------------------------
# Config selector
# ---------------------------------------------------------------------------

_env_map = {
    "development": DevelopmentConfig,
    "staging": StagingConfig,
    "production": ProductionConfig,
}


def get_config():
    """Return the configuration class matching FLASK_ENV."""
    env = os.getenv("FLASK_ENV", "development").lower()
    return _env_map.get(env, DevelopmentConfig)()
