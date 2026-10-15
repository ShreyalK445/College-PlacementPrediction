"""
Comprehensive Test Suite for V2 Extended Features:
Auth, Explainability, Roadmap, Role Matching, Mentor Chat,
Mock Assessments, Simulator, Resume Analyzer, TPO Early-Warning, and Model Monitoring.
"""

import json
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

SAMPLE_STUDENT = {
    "IQ": 120,
    "Prev_Sem_Result": 7.97,
    "CGPA": 7.76,
    "Academic_Performance": 6,
    "Extra_Curricular_Score": 9,
    "Communication_Skills": 9,
    "Projects_Completed": 2,
    "Internship_Experience": 1.0,
}

# ---------------------------------------------------------------------------
# 1. Explainability Tests
# ---------------------------------------------------------------------------

def test_explain_endpoint_success(client):
    res = client.post("/api/explain", json=SAMPLE_STUDENT)
    assert res.status_code == 200
    data = res.get_json()
    assert "base_value" in data
    assert "predicted_probability" in data
    assert "feature_contributions" in data
    assert "top_positive_factors" in data
    assert "top_negative_factors" in data
    assert "narrative" in data
    assert "disclaimer" in data

    # Mathematical identity verification: base_value + sum(contributions) ~ predicted_probability
    base_val = data["base_value"]
    sum_contribs = sum(data["feature_contributions"].values())
    pred_prob = data["predicted_probability"]
    assert abs((base_val + sum_contribs) - pred_prob) < 0.01

def test_predict_with_explain_flag(client, auth_headers):
    payload = {**SAMPLE_STUDENT, "explain": True}
    res = client.post("/predict", json=payload, headers=auth_headers)
    assert res.status_code == 200
    data = res.get_json()
    assert "results" in data
    assert "explainability" in data["results"]
    assert data["results"]["explainability"]["method"].startswith("Exact Tree-Path")

# ---------------------------------------------------------------------------
# 2. Career Improvement Roadmap Tests
# ---------------------------------------------------------------------------

def test_roadmap_generate_and_fetch(client):
    # Generate roadmap from profile
    res = client.post("/api/roadmap/generate", json=SAMPLE_STUDENT)
    assert res.status_code == 200
    data = res.get_json()
    assert "tasks" in data
    assert len(data["tasks"]) >= 6

    # Verify task attributes
    first_task = data["tasks"][0]
    assert "week_number" in first_task
    assert "title" in first_task
    assert "priority" in first_task
    assert "relevance_reason" in first_task
    assert "resources" in first_task

    # Fetch roadmap
    res_get = client.get("/api/roadmap")
    assert res_get.status_code == 200
    assert "tasks" in res_get.get_json()

# ---------------------------------------------------------------------------
# 3. Job Role Matching Tests
# ---------------------------------------------------------------------------

def test_job_roles_list(client):
    res = client.get("/api/roles")
    assert res.status_code == 200
    roles = res.get_json()["roles"]
    assert "software_developer" in roles
    assert "data_analyst" in roles
    assert "aiml_engineer" in roles
    assert "bi_analyst" in roles
    assert "qa_engineer" in roles

def test_job_roles_match_all(client):
    payload = {
        "profile": {
            **SAMPLE_STUDENT,
            "skills": ["Python", "SQL", "Data Structures & Algorithms", "Git"],
        }
    }
    res = client.post("/api/roles/match", json=payload)
    assert res.status_code == 200
    matches = res.get_json()["matches"]
    assert len(matches) == 5
    for m in matches:
        assert "readiness_score" in m
        assert "matched_core_skills" in m
        assert "missing_core_skills" in m
        assert "actionable_study_plan" in m

def test_job_roles_match_single(client):
    payload = {
        "role_key": "data_analyst",
        "profile": {
            **SAMPLE_STUDENT,
            "skills": ["SQL", "Power BI", "Pandas", "Excel"],
        }
    }
    res = client.post("/api/roles/match", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["role_key"] == "data_analyst"
    assert data["readiness_score"] > 0
    assert "SQL & Relational Databases" in data["matched_core_skills"] or len(data["matched_core_skills"]) >= 0

# ---------------------------------------------------------------------------
# 4. AI Career Mentor Chat Tests
# ---------------------------------------------------------------------------

def test_mentor_chat_fallback(client):
    payload = {
        "message": "How do I improve my resume bullet point for a web app project?",
        "student_context": SAMPLE_STUDENT,
    }
    res = client.post("/api/mentor/chat", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert "reply" in data
    assert "Google XYZ Formula" in data["reply"] or "Bullet" in data["reply"]

def test_mentor_chat_technical_question(client):
    payload = {"message": "Give me a technical question on data structures"}
    res = client.post("/api/mentor/chat", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert "Data Structures" in data["reply"] or "Binary Tree" in data["reply"]

# ---------------------------------------------------------------------------
# 5. Mock Interview Assessment Tests
# ---------------------------------------------------------------------------

def test_mock_test_catalog(client):
    res = client.get("/api/assessments/tests")
    assert res.status_code == 200
    tests = res.get_json()["tests"]
    assert len(tests) >= 5

def test_mock_test_start_and_submit(client):
    res_start = client.get("/api/assessments/tests/aptitude/start")
    assert res_start.status_code == 200
    questions = res_start.get_json()["questions"]
    assert len(questions) > 0
    assert "question" in questions[0]
    assert "options" in questions[0]
    assert "correct_index" not in questions[0]  # Answers should not be leaked to taker!

    # Submit answers
    answers = {q["id"]: 1 for q in questions}
    res_submit = client.post("/api/assessments/tests/aptitude/submit", json={"answers": answers, "time_spent_secs": 180})
    assert res_submit.status_code == 200
    scorecard = res_submit.get_json()
    assert "score" in scorecard
    assert "percentage" in scorecard
    assert "passed" in scorecard
    assert "category_breakdown" in scorecard
    assert "review" in scorecard

# ---------------------------------------------------------------------------
# 6. What-If Placement Simulator Tests
# ---------------------------------------------------------------------------

def test_what_if_simulator(client):
    baseline = dict(SAMPLE_STUDENT)
    hypothetical = dict(SAMPLE_STUDENT)
    hypothetical["Communication_Skills"] = 10
    hypothetical["Projects_Completed"] = 5

    payload = {"baseline": baseline, "hypothetical": hypothetical}
    res = client.post("/api/simulator/simulate", json=payload)
    assert res.status_code == 200
    sim = res.get_json()
    assert "baseline" in sim
    assert "hypothetical" in sim
    assert "delta" in sim
    assert "modified_features" in sim
    assert len(sim["modified_features"]) == 2
    assert "insights" in sim

# ---------------------------------------------------------------------------
# 7. Resume Analyzer Tests
# ---------------------------------------------------------------------------

def test_resume_text_analysis(client):
    sample_resume = (
        "John Doe\nEmail: john.doe@email.com Phone: 555-123-4567\n"
        "Education: B.Tech Computer Science, CGPA 8.4\n"
        "Technical Skills: Python, SQL, React, Git, Docker, Machine Learning\n"
        "Projects: Built a full-stack e-commerce web platform with REST APIs\n"
        "Work Experience: Software Engineering Intern at Tech Corp\n"
    )
    res = client.post("/api/resume/analyze", json={"resume_text": sample_resume})
    assert res.status_code == 200
    data = res.get_json()
    assert "Python" in data["technical_skills"]
    assert "SQL" in data["technical_skills"]
    assert data["structural_checks"]["has_projects_section"] is True
    assert data["structural_checks"]["has_internship_section"] is True
    assert data["resume_strength_score"] > 50

def test_resume_match_with_jd(client):
    resume = "Skills: Python, SQL, Git, Linux, Docker"
    jd = "Requirements: Python, SQL, Docker, Kubernetes, AWS, Microservices"
    payload = {"resume_text": resume, "job_description": jd}
    res = client.post("/api/resume/match-jd", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert "Python" in data["matching_skills"]
    assert "SQL" in data["matching_skills"]
    assert "Kubernetes" in data["missing_skills"]
    assert data["match_percentage"] > 0

# ---------------------------------------------------------------------------
# 8. TPO Early-Warning Dashboard Tests
# ---------------------------------------------------------------------------

def test_tpo_cohort_summary(client):
    res = client.get("/api/tpo/cohort")
    assert res.status_code == 200
    data = res.get_json()
    assert "cohort_metrics" in data
    assert "roster" in data
    assert len(data["roster"]) > 0
    assert "intervention_priority" in data["roster"][0]

def test_tpo_interventions_crud(client):
    new_intervention = {
        "student_name": "Test Student",
        "student_email": "test@college.edu",
        "priority": "High",
        "reason": "Communication score below minimum bar",
        "action_plan": "Enrolled in Week 3 mock interview workshops",
        "follow_up_date": "2026-11-01",
    }
    res_post = client.post("/api/tpo/interventions", json=new_intervention)
    assert res_post.status_code == 201

    res_get = client.get("/api/tpo/interventions")
    assert res_get.status_code == 200
    interventions = res_get.get_json()["interventions"]
    assert len(interventions) >= 1
    assert any(i["student_name"] == "Test Student" for i in interventions)

def test_tpo_csv_export(client):
    res = client.get("/api/tpo/export-csv")
    assert res.status_code == 200
    assert res.headers["Content-Type"].startswith("text/csv")
    assert b"Student_ID,Name,Email" in res.data

# ---------------------------------------------------------------------------
# 9. Authentication Tests
# ---------------------------------------------------------------------------

def test_auth_register_and_login(client):
    import uuid
    email = f"user_{uuid.uuid4().hex[:8]}@test.edu"
    register_payload = {
        "email": email,
        "password": "SecurePassword123!",
        "full_name": "Test Candidate",
        "role": "student",
        "department": "Computer Science",
    }
    res_reg = client.post("/api/auth/register", json=register_payload)
    assert res_reg.status_code == 201
    assert "token" in res_reg.get_json()

    # Login
    res_login = client.post("/api/auth/login", json={"email": email, "password": "SecurePassword123!"})
    assert res_login.status_code == 200
    token = res_login.get_json()["token"]

    # Verify protected /auth/me
    res_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_me.status_code == 200
    assert res_me.get_json()["user"]["email"] == email

# ---------------------------------------------------------------------------
# 10. Model Monitoring & Calibration Tests
# ---------------------------------------------------------------------------

def test_model_monitoring_endpoint(client):
    res = client.get("/api/model/monitoring")
    assert res.status_code == 200
    data = res.get_json()
    assert "brier_score" in data
    assert "calibration_bins" in data
    assert "subgroup_fairness" in data
    assert "model_limitations" in data
