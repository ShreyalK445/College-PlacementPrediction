# 🎓 AI-Powered Student Career Intelligence & Placement Preparation Platform

<p align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-19.0-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Flask](https://img.shields.io/badge/Flask-API-black?style=for-the-badge&logo=flask)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-ML-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

</p>

---

## 📌 Overview

**AI-Powered Student Career Intelligence and Placement Preparation Platform** is an enterprise-grade web application built to predict campus placement likelihood, explain model reasoning down to individual decision trees, generate personalized 8-week career roadmaps, evaluate skill gaps across target job profiles, provide AI mentorship, run timed mock interviews, and empower TPOs with cohort early-warning triage dashboards.

---

## ✨ Comprehensive Feature Matrix

| Category | Features |
|----------|----------|
| ⚛️ **Modern React 19 UI** | Premium dark-mode glassmorphism interface, responsive tabs, live telemetry beacons |
| 🔍 **Explainable AI (XAI)** | Exact Tree-Path feature attribution (`predict_proba = base_val + Σ contrib`), top drivers |
| 🧪 **What-If Simulator** | Interactive dual-profile sandbox testing hypothetical parameter gains in real time |
| 🗺️ **Career Roadmap** | Personalized 8-week developmental milestones with interactive task tracking & curated resources |
| 🎯 **Job Role Matching** | Skill gap analysis across 5 domains (Software Dev, Data Analyst, AI/ML, BI, QA) |
| 🤖 **AI Career Mentor** | Context-aware advisor with LLM support & robust deterministic career guidance engine |
| 📝 **Mock Interview Suite** | Timed tests (Aptitude, Core CS, Software Dev, Data Analyst, HR) with rubric scorecards |
| 📄 **Resume Analyzer** | PDF text extraction, ATS structural score, and target Job Description keyword matcher |
| 🏛️ **TPO Early-Warning** | Cohort triage prioritization (High/Medium/Low risk), counselor action logger & CSV export |
| 🛡️ **Security & Auth** | JWT token authentication, role-based access (Student, Mentor, TPO, Admin), rate limiting |
| 📊 **Observability & MLOps** | Liveness/Readiness probes, Brier score calibration, fairness analysis, Swagger UI |
| 🧪 **Automated Testing** | 46 comprehensive Pytest tests (100% pass) + Oxlint 0 warnings + Vite production bundle |

---

## 🛠 Tech Stack

| Technology | Purpose |
|---|---|
| React 19 & Vite | Modern reactive frontend SPA |
| Python 3.10+ | Backend runtime |
| Flask | REST API framework |
| SQLAlchemy | Persistent database ORM (SQLite / PostgreSQL) |
| PyJWT & Werkzeug | JWT authentication & secure password hashing |
| Scikit-Learn | Random Forest ML inference engine |
| Pydantic | Robust input schema validation |
| pypdf | Server-side PDF resume parsing |
| Gunicorn | Production WSGI server |
| Flasgger | Swagger/OpenAPI interactive documentation |
| Flask-Limiter | Rate limiting protection |
| Docker & Compose | Containerization & orchestration |
| GitHub Actions | Automated CI/CD pipeline |
| Pytest | Automated test suite (46 unit & integration tests) |

---

## 📁 Project Structure
 
```text
College-Placement-Prediction/
├── .github/workflows/
│   └── ci.yml                    # CI/CD pipeline
├── frontend/                     # React 19 + Vite Frontend SPA
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx        # Navigation & real-time API health dot
│   │   │   ├── Dashboard.jsx     # Metrics, stats & feature importance chart
│   │   │   ├── PredictionForm.jsx# Interactive sliders, presets & diagnosis
│   │   │   ├── BatchPredict.jsx  # Drag-&-drop CSV cohort inference
│   │   │   └── History.jsx       # Audit log, filters, CSV exporter
│   │   ├── api.js                # API client with proxy support
│   │   ├── App.jsx               # Main stateful tab container
│   │   ├── App.css               # Shared design system & glassmorphism
│   │   └── index.css             # Theme variables & animations
│   ├── vite.config.js            # Vite configuration with /api proxy
│   └── package.json              # NPM dependencies
├── tests/
│   ├── conftest.py               # Test fixtures
│   ├── test_api.py               # API integration tests
│   └── test_model.py             # Model unit tests
├── training_artifacts/           # Generated training reports
├── .env.example                  # Environment variable template
├── .gitignore
├── .dockerignore
├── Dockerfile                    # API container (multi-stage)
├── Dockerfile.streamlit          # Dashboard container
├── docker-compose.yml            # Orchestration
├── config.py                     # Centralized configuration
├── app.py                        # Flask API (production)
├── wsgi.py                       # WSGI entry point
├── gunicorn.conf.py              # Gunicorn settings
├── model_building.py             # Enhanced training pipeline
├── model.pkl                     # Trained model
├── model_metadata.json           # Model version & metrics
├── streamlit_app.py              # Dashboard UI
├── test_client.py                # Manual API test script
├── requirements.txt              # Pinned dependencies
├── College_placement.csv         # Training dataset
└── README.md
```

---

## ⚙️ Quick Start

### 1. Clone & Setup Backend

```bash
git clone https://github.com/your-username/College-Placement-Prediction.git
cd College-Placement-Prediction

python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings (API_KEY, SECRET_KEY, etc.)
```

### 3. Run the Backend API

**Development:**
```bash
python app.py
```

**Production:**
```bash
gunicorn wsgi:application -c gunicorn.conf.py
```

Server: `http://localhost:5000` | Swagger: `http://localhost:5000/apidocs`

### 4. Launch the React Frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend UI will open at: `http://localhost:3000` (auto-proxies `/api` to Flask at `http://localhost:5000`).

---

## 📡 API Reference

### Prediction

**`POST /predict`** — Predict placement status

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "IQ": 120,
    "Prev_Sem_Result": 7.97,
    "CGPA": 7.76,
    "Academic_Performance": 6,
    "Extra_Curricular_Score": 9,
    "Communication_Skills": 9,
    "Projects_Completed": 2,
    "Internship_Experience": 1.0
  }'
```

**Response:**
```json
{
  "request_id": "a1b2c3d4-...",
  "results": {
    "placement_prediction": 1,
    "placement_probability": 0.97,
    "status": "Placed"
  }
}
```

### Operations

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/health` | GET | ❌ | Liveness probe |
| `/ready` | GET | ❌ | Readiness probe (model loaded?) |
| `/metrics` | GET | ✅ | Request count, latency, errors |
| `/model/info` | GET | ❌ | Model version, metrics, feature importance |
| `/model/reload` | POST | ✅ | Hot-reload model from disk |
| `/apidocs` | GET | ❌ | Swagger documentation |

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage report
pytest tests/ -v --cov=. --cov-report=term-missing

# Specific test file
pytest tests/test_api.py -v
```

---

## 🐳 Docker Deployment

```bash
# Build and run all services
docker-compose up --build -d

# API only
docker build -t placement-api .
docker run -p 5000:5000 --env-file .env placement-api

# Check health
curl http://localhost:5000/health
```

---

## 📊 Input Features

| Feature | Type | Range | Description |
|---------|------|-------|-------------|
| IQ | float | 50–200 | Student IQ score |
| Prev_Sem_Result | float | 0–10 | Previous semester GPA |
| CGPA | float | 0–10 | Cumulative GPA |
| Academic_Performance | int | 1–10 | Academic rating |
| Extra_Curricular_Score | int | 1–10 | Extracurricular rating |
| Communication_Skills | int | 1–10 | Communication rating |
| Projects_Completed | int | 0–50 | Number of projects |
| Internship_Experience | float | 0 or 1 | Has internship experience |

---

## 🏗 Architecture

```text
                ┌──────────────────────────────────────────┐
                │           GitHub Actions CI/CD            │
                │      Lint → Test → Build → Deploy         │
                └──────────────┬───────────────────────────┘
                               │
                ┌──────────────▼───────────────────────────┐
                │              Docker Compose               │
                │  ┌─────────────┐    ┌─────────────────┐  │
                │  │  Flask API  │    │   Streamlit UI   │  │
                │  │  (Gunicorn) │    │   (Dashboard)    │  │
                │  │  Port 5000  │    │   Port 8501      │  │
                │  └──────┬──────┘    └────────┬─────────┘  │
                │         │                    │            │
                │         └────────┬───────────┘            │
                │                  │                        │
                │          ┌───────▼────────┐               │
                │          │   model.pkl    │               │
                │          │   (Versioned)  │               │
                │          └────────────────┘               │
                └──────────────────────────────────────────┘
```

---

## 👨‍💻 Author

**Your Name**

Machine Learning • Data Science • Flask API Development

---

## ⭐ Support

If you found this project useful, consider giving it a **⭐ Star** on GitHub!

---

<p align="center">
Made with ❤️ using Python, Flask, Scikit-Learn & Docker
</p>
