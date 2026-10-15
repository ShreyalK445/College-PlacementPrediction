"""
Extended REST API Routes — Career Intelligence & Placement Preparation Platform
Modular Blueprint containing Auth, Explainability, Roadmap, Role Matching,
Mentor Chat, Mock Assessments, Simulator, Resume Analyzer, and TPO Dashboard.
"""

import io
import json
from flask import Blueprint, request, jsonify, g, send_file
import pandas as pd
from models import (
    get_db_session,
    User,
    RoadmapTask,
    MockAssessmentAttempt,
    MentorIntervention,
)
from auth_service import generate_token, require_jwt_auth, get_current_user
from explainability import TreePathExplainer, FEATURE_NAMES
from roadmap_engine import generate_personalized_roadmap
from job_matching import JOB_ROLES, match_role, match_all_roles
from mentor_ai import ask_mentor
from assessment_engine import get_test_catalog, get_test_questions, grade_test
from simulator_engine import run_simulation
from resume_analyzer import (
    extract_text_from_pdf,
    analyze_resume_text,
    match_resume_with_jd,
)
from mentor_dashboard import get_tpo_cohort_summary, export_cohort_to_csv
from model_monitoring import get_calibration_and_quality_metrics, detect_input_drift

api_bp = Blueprint("career_api", __name__, url_prefix="/api")


def get_model_from_app():
    from flask import current_app

    return current_app.config.get("ML_MODEL")


# ---------------------------------------------------------------------------
# 1. Authentication Endpoints
# ---------------------------------------------------------------------------


@api_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json(force=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    full_name = data.get("full_name", "").strip()
    role = data.get("role", "student")
    dept = data.get("department", "Computer Science")

    if not email or not password or not full_name:
        return jsonify({"error": "Email, password, and full name are required."}), 400

    session = get_db_session()
    if session.query(User).filter_by(email=email).first():
        return jsonify({"error": "An account with this email already exists."}), 409

    user = User(email=email, full_name=full_name, role=role, department=dept)
    user.set_password(password)
    session.add(user)
    session.commit()

    token = generate_token(user)
    return jsonify(
        {
            "message": "User registered successfully",
            "token": token,
            "user": user.to_dict(),
        }
    ), 201


@api_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json(force=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    session = get_db_session()
    user = session.query(User).filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password."}), 401

    token = generate_token(user)
    return jsonify(
        {
            "message": "Login successful",
            "token": token,
            "user": user.to_dict(),
        }
    ), 200


@api_bp.route("/auth/me", methods=["GET"])
@require_jwt_auth(optional=False)
def get_me():
    return jsonify({"user": g.current_user.to_dict()}), 200


# ---------------------------------------------------------------------------
# 2. Explainable AI Endpoint
# ---------------------------------------------------------------------------


@api_bp.route("/explain", methods=["POST"])
def explain_prediction():
    data = request.get_json(force=True) or {}
    model = get_model_from_app()
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500

    # Ensure required features exist
    missing = [f for f in FEATURE_NAMES if f not in data]
    if missing:
        return jsonify({"error": f"Missing features: {', '.join(missing)}"}), 400

    try:
        sample_df = pd.DataFrame([data])[FEATURE_NAMES]
        explainer = TreePathExplainer(model, FEATURE_NAMES)
        explanation = explainer.explain_instance(sample_df)

        # Check for input distribution drift
        drifts = detect_input_drift(data)
        explanation["input_distribution_anomalies"] = drifts

        return jsonify(explanation), 200
    except Exception as exc:
        return jsonify({"error": f"Explainability failed: {str(exc)}"}), 500


# ---------------------------------------------------------------------------
# 3. Personalized Career Improvement Roadmap Endpoints
# ---------------------------------------------------------------------------


@api_bp.route("/roadmap", methods=["GET"])
def get_roadmap():
    user = get_current_user()
    session = get_db_session()

    if user:
        tasks = (
            session.query(RoadmapTask)
            .filter_by(user_id=user.id)
            .order_by(RoadmapTask.week_number)
            .all()
        )
        if tasks:
            return jsonify({"tasks": [t.to_dict() for t in tasks]}), 200

    # If no tasks saved in DB, generate default recommended template
    default_profile = {
        "CGPA": 7.4,
        "Communication_Skills": 7,
        "Projects_Completed": 2,
        "Internship_Experience": 1,
    }
    default_tasks = generate_personalized_roadmap(default_profile)
    return jsonify({"tasks": default_tasks}), 200


@api_bp.route("/roadmap/generate", methods=["POST"])
def generate_roadmap():
    data = request.get_json(force=True) or {}
    user = get_current_user()
    tasks = generate_personalized_roadmap(data)

    if user:
        session = get_db_session()
        # Clear existing tasks for fresh roadmap regeneration
        session.query(RoadmapTask).filter_by(user_id=user.id).delete()
        for t in tasks:
            rt = RoadmapTask(
                user_id=user.id,
                week_number=t["week_number"],
                title=t["title"],
                description=t["description"],
                category=t["category"],
                priority=t["priority"],
                status="pending",
                deadline=t["deadline"],
                resources_json=json.dumps(t["resources"]),
            )
            session.add(rt)
        session.commit()
        persisted = (
            session.query(RoadmapTask)
            .filter_by(user_id=user.id)
            .order_by(RoadmapTask.week_number)
            .all()
        )
        return jsonify({"tasks": [p.to_dict() for p in persisted]}), 200

    return jsonify({"tasks": tasks}), 200


@api_bp.route("/roadmap/tasks/<int:task_id>", methods=["PATCH"])
def update_task_status(task_id):
    data = request.get_json(force=True) or {}
    new_status = data.get("status")
    if new_status not in ("pending", "in_progress", "completed"):
        return jsonify(
            {"error": "Status must be pending, in_progress, or completed."}
        ), 400

    session = get_db_session()
    task = session.query(RoadmapTask).filter_by(id=task_id).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404

    task.status = new_status
    session.commit()
    return jsonify({"message": "Task updated", "task": task.to_dict()}), 200


# ---------------------------------------------------------------------------
# 4. Job Role & Skill Gap Matching Endpoints
# ---------------------------------------------------------------------------


@api_bp.route("/roles", methods=["GET"])
def get_roles():
    return jsonify({"roles": JOB_ROLES}), 200


@api_bp.route("/roles/match", methods=["POST"])
def match_job_roles():
    data = request.get_json(force=True) or {}
    role_key = data.get("role_key")
    profile = data.get("profile", data)

    if role_key:
        if role_key not in JOB_ROLES:
            return jsonify({"error": f"Role '{role_key}' not supported."}), 404
        result = match_role(profile, role_key)
        return jsonify(result), 200

    # Match all roles
    results = match_all_roles(profile)
    return jsonify({"matches": results}), 200


# ---------------------------------------------------------------------------
# 5. AI Career Mentor Chatbot Endpoint
# ---------------------------------------------------------------------------


@api_bp.route("/mentor/chat", methods=["POST"])
def mentor_chat():
    data = request.get_json(force=True) or {}
    message = data.get("message", "")
    student_ctx = data.get("student_context", {})
    history = data.get("history", [])

    response = ask_mentor(
        message, student_context=student_ctx, conversation_history=history
    )
    return jsonify(response), 200


# ---------------------------------------------------------------------------
# 6. Smart Mock Assessment Endpoints
# ---------------------------------------------------------------------------


@api_bp.route("/assessments/tests", methods=["GET"])
def get_tests():
    catalog = get_test_catalog()
    return jsonify({"tests": catalog}), 200


@api_bp.route("/assessments/tests/<test_type>/start", methods=["GET"])
def start_test(test_type):
    try:
        questions = get_test_questions(test_type)
        return jsonify({"test_type": test_type, "questions": questions}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@api_bp.route("/assessments/tests/<test_type>/submit", methods=["POST"])
def submit_test(test_type):
    data = request.get_json(force=True) or {}
    answers = data.get("answers", {})
    time_spent = data.get("time_spent_secs", 0)

    try:
        result = grade_test(test_type, answers)

        user = get_current_user()
        if user:
            session = get_db_session()
            attempt = MockAssessmentAttempt(
                user_id=user.id,
                test_type=test_type,
                score=result["score"],
                total_questions=result["total_questions"],
                time_spent_secs=time_spent,
                category_scores_json=json.dumps(result["category_breakdown"]),
                feedback=result["overall_verdict"],
            )
            session.add(attempt)
            session.commit()

        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


# ---------------------------------------------------------------------------
# 7. What-If Placement Simulator Endpoint
# ---------------------------------------------------------------------------


@api_bp.route("/simulator/simulate", methods=["POST"])
def simulate():
    data = request.get_json(force=True) or {}
    baseline = data.get("baseline")
    hypothetical = data.get("hypothetical")

    if not baseline or not hypothetical:
        return jsonify(
            {"error": "Both 'baseline' and 'hypothetical' input dictionaries required."}
        ), 400

    model = get_model_from_app()
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500

    try:
        sim_result = run_simulation(model, baseline, hypothetical)
        return jsonify(sim_result), 200
    except Exception as exc:
        return jsonify({"error": f"Simulation failed: {str(exc)}"}), 500


# ---------------------------------------------------------------------------
# 8. Resume Analyzer & JD Matcher Endpoints
# ---------------------------------------------------------------------------


@api_bp.route("/resume/analyze", methods=["POST"])
def analyze_resume():
    raw_text = ""
    if "file" in request.files:
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected."}), 400
        if not file.filename.lower().endswith(".pdf"):
            return jsonify({"error": "Only PDF resumes are supported."}), 400

        file_bytes = file.read()
        if len(file_bytes) > 5 * 1024 * 1024:
            return jsonify({"error": "File size exceeds 5MB limit."}), 400

        try:
            raw_text = extract_text_from_pdf(io.BytesIO(file_bytes))
        except Exception as exc:
            return jsonify({"error": str(exc)}), 400
    else:
        data = request.get_json(silent=True) or {}
        raw_text = data.get("resume_text", "").strip()

    if not raw_text:
        return jsonify(
            {"error": "Provide a PDF file upload or 'resume_text' in JSON."}
        ), 400

    analysis = analyze_resume_text(raw_text)
    return jsonify(analysis), 200


@api_bp.route("/resume/match-jd", methods=["POST"])
def match_jd():
    data = request.get_json(force=True) or {}
    resume_text = data.get("resume_text", "")
    jd_text = data.get("job_description", "")

    if not resume_text or not jd_text:
        return jsonify(
            {"error": "Both 'resume_text' and 'job_description' are required."}
        ), 400

    result = match_resume_with_jd(resume_text, jd_text)
    return jsonify(result), 200


# ---------------------------------------------------------------------------
# 9. Mentor / TPO Early-Warning Dashboard Endpoints
# ---------------------------------------------------------------------------


@api_bp.route("/tpo/cohort", methods=["GET"])
def get_cohort():
    dept = request.args.get("department")
    summary = get_tpo_cohort_summary(department=dept)
    return jsonify(summary), 200


@api_bp.route("/tpo/interventions", methods=["GET", "POST"])
def manage_interventions():
    session = get_db_session()
    if request.method == "POST":
        data = request.get_json(force=True) or {}
        student_name = data.get("student_name", "")
        student_email = data.get("student_email", "")
        priority = data.get("priority", "High")
        reason = data.get("reason", "")
        action_plan = data.get("action_plan", "")
        follow_up = data.get("follow_up_date", "")

        if not student_name or not reason or not action_plan:
            return jsonify(
                {"error": "student_name, reason, and action_plan are required."}
            ), 400

        intervention = MentorIntervention(
            student_name=student_name,
            student_email=student_email,
            priority=priority,
            reason=reason,
            action_plan=action_plan,
            follow_up_date=follow_up,
        )
        session.add(intervention)
        session.commit()
        return jsonify(
            {"message": "Intervention recorded", "intervention": intervention.to_dict()}
        ), 201

    interventions = (
        session.query(MentorIntervention)
        .order_by(MentorIntervention.created_at.desc())
        .all()
    )
    return jsonify({"interventions": [i.to_dict() for i in interventions]}), 200


@api_bp.route("/tpo/export-csv", methods=["GET"])
def export_tpo_csv():
    dept = request.args.get("department")
    summary = get_tpo_cohort_summary(department=dept)
    csv_text = export_cohort_to_csv(summary["roster"])

    mem = io.BytesIO()
    mem.write(csv_text.encode("utf-8"))
    mem.seek(0)
    return send_file(
        mem,
        mimetype="text/csv",
        as_attachment=True,
        download_name="tpo_cohort_interventions.csv",
    )


# ---------------------------------------------------------------------------
# 10. ML Quality & Calibration Monitoring
# ---------------------------------------------------------------------------


@api_bp.route("/model/monitoring", methods=["GET"])
def model_monitoring():
    metrics = get_calibration_and_quality_metrics()
    return jsonify(metrics), 200
