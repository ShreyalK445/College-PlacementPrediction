"""
Resume Analyzer & Job Description Matcher
Extracts technical credentials from PDF and plain-text resumes and benchmarks against job descriptions.
"""

from typing import Dict, List, Any
import io
import re
from pypdf import PdfReader

# Master taxonomy of industry skills for entity extraction
TECH_SKILLS = [
    "Python", "Java", "C++", "C", "JavaScript", "TypeScript", "React", "Node.js",
    "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis",
    "HTML", "CSS", "REST APIs", "FastAPI", "Flask", "Django", "Spring Boot",
    "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Git", "GitHub", "CI/CD",
    "Linux", "Pandas", "NumPy", "Scikit-Learn", "TensorFlow", "PyTorch",
    "Power BI", "Tableau", "Excel", "Data Structures", "Algorithms",
    "Machine Learning", "Deep Learning", "Data Visualization", "Selenium",
    "PyTest", "System Design", "Agile", "Scrum",
]

SOFT_SKILLS = [
    "Communication", "Leadership", "Teamwork", "Problem Solving",
    "Critical Thinking", "Adaptability", "Time Management", "Collaboration",
    "Conflict Resolution", "Presentation",
]

def extract_text_from_pdf(file_stream: io.BytesIO) -> str:
    """Extracts raw text from a PDF stream using pypdf."""
    try:
        reader = PdfReader(file_stream)
        text_parts = []
        for page_idx, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        full_text = "\n".join(text_parts).strip()
        if not full_text:
            raise ValueError("PDF appears to be scanned or contains no extractable text.")
        return full_text
    except Exception as exc:
        raise ValueError(f"Failed to read PDF resume: {str(exc)}")

def analyze_resume_text(text: str) -> Dict[str, Any]:
    """
    Parses resume text to extract skills, education clues, projects, and email/phone.
    """
    text_lower = text.lower()

    # Extract matching technical skills
    matched_tech = []
    for skill in TECH_SKILLS:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text_lower):
            matched_tech.append(skill)

    # Extract soft skills
    matched_soft = []
    for skill in SOFT_SKILLS:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text_lower):
            matched_soft.append(skill)

    # Extract email and phone
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)

    # Detect presence of key sections
    has_projects = bool(re.search(r"\b(projects?|capstones?|portfolio)\b", text_lower))
    has_internship = bool(re.search(r"\b(internship|work experience|employment|experience)\b", text_lower))
    has_education = bool(re.search(r"\b(education|b\.?tech|bachelor|degree|gpa|cgpa)\b", text_lower))
    has_certifications = bool(re.search(r"\b(certifications?|certificates?|credentials?)\b", text_lower))

    # Calculate overall resume structural strength score (out of 100)
    score = 0
    score += min(35, len(matched_tech) * 5)
    score += min(15, len(matched_soft) * 3)
    score += 15 if has_projects else 0
    score += 15 if has_internship else 0
    score += 10 if has_education else 0
    score += 10 if (email_match and phone_match) else 5

    # Suggested resume enhancements
    improvements = []
    if len(matched_tech) < 5:
        improvements.append("Expand your technical skills section with specific frameworks, databases, and tooling.")
    if not has_projects:
        improvements.append("Add a dedicated 'Projects' section with quantified achievements (e.g. latency, users, tests).")
    if not has_internship:
        improvements.append("Highlight open-source contributions or academic research to demonstrate practical code experience.")
    if not has_certifications:
        improvements.append("Consider earning an industry-recognized cloud or developer certification.")
    if not improvements:
        improvements.append("Resume contains balanced technical coverage and key functional sections.")

    return {
        "extracted_contact": {
            "email": email_match.group(0) if email_match else None,
            "phone": phone_match.group(0) if phone_match else None,
        },
        "technical_skills": matched_tech,
        "soft_skills": matched_soft,
        "structural_checks": {
            "has_projects_section": has_projects,
            "has_internship_section": has_internship,
            "has_education_section": has_education,
            "has_certifications_section": has_certifications,
        },
        "resume_strength_score": min(100, score),
        "suggested_improvements": improvements,
        "word_count": len(text.split()),
    }

def match_resume_with_jd(resume_text: str, jd_text: str) -> Dict[str, Any]:
    """
    Compares extracted resume skills directly against a target job description.
    """
    resume_analysis = analyze_resume_text(resume_text)
    jd_lower = jd_text.lower()

    # Find required skills mentioned in JD
    jd_skills = []
    for skill in TECH_SKILLS + SOFT_SKILLS:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, jd_lower):
            jd_skills.append(skill)

    resume_all_skills = set(resume_analysis["technical_skills"] + resume_analysis["soft_skills"])
    matching_skills = [s for s in jd_skills if s in resume_all_skills]
    missing_skills = [s for s in jd_skills if s not in resume_all_skills]

    match_pct = round((len(matching_skills) / max(len(jd_skills), 1)) * 100, 1)

    recommendations = []
    if missing_skills:
        recommendations.append(f"Incorporate or acquire these missing keywords required by the JD: {', '.join(missing_skills[:5])}.")
    if match_pct >= 75:
        recommendations.append("High alignment with job description! Tailor bullet points to emphasize impact metrics.")
    else:
        recommendations.append("Moderate alignment. Customize your summary and project descriptions to mirror role terminology.")

    return {
        "job_description_skills_detected": jd_skills,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "match_percentage": match_pct,
        "recommendations": recommendations,
        "resume_analysis": resume_analysis,
    }
