"""
Job Role & Skill Gap Matching Engine
Evaluates candidate skillsets against 5 target tech domains and produces gap analyses.
"""

from typing import Dict, List, Any

# Predefined, industry-aligned role definitions with skill taxonomies
JOB_ROLES: Dict[str, Dict[str, Any]] = {
    "software_developer": {
        "title": "Software Developer",
        "description": "Designs, develops, and maintains scalable backend services, web applications, and system APIs.",
        "icon": "💻",
        "min_cgpa": 6.5,
        "recommended_projects": 3,
        "core_skills": [
            "Data Structures & Algorithms",
            "Python or Java or C++",
            "SQL & Relational Databases",
            "Git & Version Control",
            "REST APIs",
        ],
        "secondary_skills": [
            "Docker / Containerization",
            "System Design Principles",
            "Unit Testing / PyTest / JUnit",
            "CI/CD Pipelines",
        ],
        "recommended_certifications": [
            "AWS Certified Developer Associate",
            "Meta Back-End Developer Certificate",
        ],
        "study_plan": [
            "Master Array, String, Linked List, and Binary Tree interview patterns.",
            "Build an authenticated RESTful web service with PostgreSQL.",
            "Write comprehensive unit tests with code coverage above 80%.",
        ],
    },
    "data_analyst": {
        "title": "Data Analyst",
        "description": "Transforms raw institutional and business data into actionable dashboards, KPIs, and reports.",
        "icon": "📊",
        "min_cgpa": 6.5,
        "recommended_projects": 2,
        "core_skills": [
            "Advanced SQL (Window functions, CTEs)",
            "Python (Pandas, NumPy)",
            "Data Visualization (Power BI or Tableau)",
            "Descriptive & Inferential Statistics",
            "Excel (Pivot Tables, VLOOKUP, Power Query)",
        ],
        "secondary_skills": [
            "A/B Testing Methodologies",
            "ETL Pipeline Basics",
            "Business Communication & Storytelling",
            "Data Cleaning Techniques",
        ],
        "recommended_certifications": [
            "Google Data Analytics Professional Certificate",
            "Microsoft Certified: Power BI Data Analyst (PL-300)",
        ],
        "study_plan": [
            "Deep dive into complex multi-table SQL queries, window aggregates, and joins.",
            "Construct a public Power BI / Tableau dashboard with drill-down interactivity.",
            "Complete an exploratory data analysis project on Kaggle with executive summaries.",
        ],
    },
    "aiml_engineer": {
        "title": "AI/ML Engineer",
        "description": "Develops, trains, validates, and deploys predictive and machine learning algorithms into production.",
        "icon": "🤖",
        "min_cgpa": 7.0,
        "recommended_projects": 3,
        "core_skills": [
            "Python (Scikit-Learn, Pandas, NumPy)",
            "Supervised & Unsupervised Machine Learning",
            "Linear Algebra, Calculus & Probability",
            "Model Evaluation (ROC-AUC, F1, Cross-Validation)",
            "Data Preprocessing & Feature Engineering",
        ],
        "secondary_skills": [
            "Deep Learning Basics (PyTorch or TensorFlow)",
            "MLOps & Model Serialization (Pickle, ONNX)",
            "Flask / FastAPI Model Serving",
            "Explainable AI (SHAP / Tree Attribution)",
        ],
        "recommended_certifications": [
            "DeepLearning.AI Machine Learning Specialization",
            "AWS Certified Machine Learning - Specialty",
        ],
        "study_plan": [
            "Implement and cross-validate regression, random forest, and gradient boosting pipelines.",
            "Build a model serving REST API with input validation and rate limiting.",
            "Analyze feature importance and probability calibration curves on realistic datasets.",
        ],
    },
    "bi_analyst": {
        "title": "Business Intelligence Analyst",
        "description": "Bridges technical analytics with executive decision-making through enterprise data models and metrics.",
        "icon": "📈",
        "min_cgpa": 6.5,
        "recommended_projects": 2,
        "core_skills": [
            "Enterprise SQL & Data Warehousing Concepts",
            "Power BI / Tableau / Looker",
            "KPI Definition & Metric Trees",
            "Stakeholder Presentation & Verbal Articulation",
            "Dimensional Modeling (Star & Snowflake Schema)",
        ],
        "secondary_skills": [
            "DAX / Power Query M Language",
            "Python Data Scripting",
            "Requirements Gathering & Agile User Stories",
            "Financial or Operations Literacy",
        ],
        "recommended_certifications": [
            "Microsoft Certified: Power BI Data Analyst",
            "Tableau Desktop Specialist",
        ],
        "study_plan": [
            "Study star-schema dimensional modeling for retail and SaaS data marts.",
            "Design an end-to-end executive KPI scorecard tracking conversion and retention.",
            "Rehearse mock business stakeholder presentations communicating analytical insights.",
        ],
    },
    "qa_engineer": {
        "title": "QA Engineer (Quality Assurance & Test Automation)",
        "description": "Designs automated test suites, validates software robustness, and ensures enterprise defect prevention.",
        "icon": "🛡️",
        "min_cgpa": 6.0,
        "recommended_projects": 2,
        "core_skills": [
            "Software Testing Fundamentals (Functional, Regression, Boundary)",
            "Selenium / Playwright / Cypress Test Automation",
            "Python or Java Test Scripting",
            "API Testing with Postman & REST Assured",
            "Bug Tracking & Defect Life Cycle (Jira / GitHub Issues)",
        ],
        "secondary_skills": [
            "CI/CD Integration (GitHub Actions / Jenkins)",
            "Performance Testing (JMeter)",
            "SQL Querying for Test Data Verification",
            "Test-Driven Development (TDD) Mindset",
        ],
        "recommended_certifications": [
            "ISTQB Certified Tester Foundation Level (CTFL)",
            "Selenium WebDriver with Python / Java Certification",
        ],
        "study_plan": [
            "Draft formal test plan and boundary condition test cases for an open-source web application.",
            "Implement end-to-end browser automation suites with Playwright or Cypress.",
            "Automate API regression tests integrated into a GitHub Actions CI pipeline.",
        ],
    },
}


def normalize_skill(skill: str) -> str:
    """Helper to normalize skill string for fuzzy matching."""
    return "".join(c.lower() for c in skill if c.isalnum() or c in ("+", "#"))


def match_role(student_profile: Dict[str, Any], role_key: str) -> Dict[str, Any]:
    """
    Computes skill gap and role readiness for a specific job role.
    Distinguishes role readiness score (0-100%) from hiring probability!
    """
    if role_key not in JOB_ROLES:
        raise ValueError(f"Unknown job role: {role_key}")

    role = JOB_ROLES[role_key]
    declared_skills = [str(s).strip() for s in student_profile.get("skills", [])]
    normalized_declared = {normalize_skill(s): s for s in declared_skills}

    cgpa = float(student_profile.get("CGPA", 7.0))
    projects = int(student_profile.get("Projects_Completed", 1))
    comm_score = int(student_profile.get("Communication_Skills", 6))

    # Check Core Skills match
    matched_core = []
    missing_core = []
    for req in role["core_skills"]:
        # Match if any token in req aligns with student's declared skills
        req_norm = normalize_skill(req)
        matched = False
        for decl_norm, original in normalized_declared.items():
            if (
                decl_norm in req_norm
                or req_norm in decl_norm
                or any(part in req_norm for part in decl_norm.split())
            ):
                matched = True
                matched_core.append(req)
                break
        if not matched:
            missing_core.append(req)

    # Check Secondary Skills match
    matched_sec = []
    missing_sec = []
    for req in role["secondary_skills"]:
        req_norm = normalize_skill(req)
        matched = False
        for decl_norm in normalized_declared:
            if decl_norm in req_norm or req_norm in decl_norm:
                matched = True
                matched_sec.append(req)
                break
        if not matched:
            missing_sec.append(req)

    # Compute Weighted Readiness Score (0 to 100%)
    # Core Skills: 45%
    # Secondary Skills: 15%
    # CGPA Eligibility: 15%
    # Project Portfolio: 15%
    # Communication Baseline: 10%
    core_pct = (len(matched_core) / max(len(role["core_skills"]), 1)) * 45.0
    sec_pct = (len(matched_sec) / max(len(role["secondary_skills"]), 1)) * 15.0
    cgpa_pct = min(1.0, cgpa / max(role["min_cgpa"], 1.0)) * 15.0
    proj_pct = min(1.0, projects / max(role["recommended_projects"], 1)) * 15.0
    comm_pct = (min(10, comm_score) / 10.0) * 10.0

    readiness_score = round(core_pct + sec_pct + cgpa_pct + proj_pct + comm_pct, 1)

    return {
        "role_key": role_key,
        "title": role["title"],
        "icon": role["icon"],
        "description": role["description"],
        "readiness_score": readiness_score,
        "min_cgpa": role["min_cgpa"],
        "student_cgpa": cgpa,
        "cgpa_eligible": cgpa >= role["min_cgpa"],
        "matched_core_skills": matched_core,
        "missing_core_skills": missing_core,
        "matched_secondary_skills": matched_sec,
        "missing_secondary_skills": missing_sec,
        "recommended_certifications": role["recommended_certifications"],
        "actionable_study_plan": role["study_plan"],
        "disclaimer": (
            "Role Readiness Score measures curriculum and skill alignment against role competencies. "
            "It is distinctly separate from company hiring probability or placement guarantees."
        ),
    }


def match_all_roles(student_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Evaluates the student against all supported job roles for comparative analysis."""
    results = [match_role(student_profile, key) for key in JOB_ROLES]
    results.sort(key=lambda x: x["readiness_score"], reverse=True)
    return results
