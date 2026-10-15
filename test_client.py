"""
API test client — demonstrates single and batch prediction requests.

Usage:
    python test_client.py
    python test_client.py --api-key YOUR_KEY
    python test_client.py --url http://your-server:5000
"""

import argparse
import json
import sys

import requests

# ---------------------------------------------------------------------------
# CLI arguments
# ---------------------------------------------------------------------------
parser = argparse.ArgumentParser(description="Test the Placement Prediction API")
parser.add_argument("--url", default="http://127.0.0.1:5000", help="API base URL")
parser.add_argument("--api-key", default="", help="API key for authenticated endpoints")
args = parser.parse_args()

BASE_URL = args.url.rstrip("/")
HEADERS = {"Content-Type": "application/json"}
if args.api_key:
    HEADERS["X-API-Key"] = args.api_key


def print_response(label, response):
    """Pretty-print an API response."""
    print(f"\n{'=' * 60}")
    print(f"  {label}")
    print(f"{'=' * 60}")
    print(f"  Status: {response.status_code}")
    try:
        print(f"  Response:\n{json.dumps(response.json(), indent=2)}")
    except Exception:
        print(f"  Body: {response.text}")
    if "X-Request-ID" in response.headers:
        print(f"  Request-ID: {response.headers['X-Request-ID']}")
    if "X-Response-Time-Ms" in response.headers:
        print(f"  Latency: {response.headers['X-Response-Time-Ms']}ms")


# ---------------------------------------------------------------------------
# 1. Health check
# ---------------------------------------------------------------------------
print("\n🏥 Testing Health Endpoints...")

try:
    r = requests.get(f"{BASE_URL}/health")
    print_response("GET /health", r)

    r = requests.get(f"{BASE_URL}/ready")
    print_response("GET /ready", r)
except requests.ConnectionError:
    print(f"❌ Cannot connect to {BASE_URL}. Is the server running?")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 2. Model info
# ---------------------------------------------------------------------------
print("\n📊 Testing Model Info...")
r = requests.get(f"{BASE_URL}/model/info")
print_response("GET /model/info", r)

# ---------------------------------------------------------------------------
# 3. Single prediction
# ---------------------------------------------------------------------------
print("\n🔮 Testing Single Prediction...")

single_payload = {
    "IQ": 120,
    "Prev_Sem_Result": 7.97,
    "CGPA": 7.76,
    "Academic_Performance": 6,
    "Extra_Curricular_Score": 9,
    "Communication_Skills": 9,
    "Projects_Completed": 2,
    "Internship_Experience": 1.0,
}

r = requests.post(f"{BASE_URL}/predict", json=single_payload, headers=HEADERS)
print_response("POST /predict (single)", r)

# ---------------------------------------------------------------------------
# 4. Batch prediction
# ---------------------------------------------------------------------------
print("\n📦 Testing Batch Prediction...")

batch_payload = [
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

r = requests.post(f"{BASE_URL}/predict", json=batch_payload, headers=HEADERS)
print_response("POST /predict (batch)", r)

# ---------------------------------------------------------------------------
# 5. Validation error test
# ---------------------------------------------------------------------------
print("\n🛡️ Testing Validation (should return 400)...")

invalid_payload = {
    "IQ": 999,  # Out of range
    "Prev_Sem_Result": 7.97,
    "CGPA": 7.76,
    "Academic_Performance": 6,
    "Extra_Curricular_Score": 9,
    "Communication_Skills": 9,
    "Projects_Completed": 2,
    "Internship_Experience": 1.0,
}

r = requests.post(f"{BASE_URL}/predict", json=invalid_payload, headers=HEADERS)
print_response("POST /predict (invalid IQ=999)", r)

# ---------------------------------------------------------------------------
# 6. Metrics (requires API key)
# ---------------------------------------------------------------------------
print("\n📈 Testing Metrics...")
r = requests.get(f"{BASE_URL}/metrics", headers=HEADERS)
print_response("GET /metrics", r)

print("\n✅ All tests complete!")
