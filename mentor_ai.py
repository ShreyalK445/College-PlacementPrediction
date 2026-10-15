"""
AI Career Mentor Engine
Context-aware intelligent assistant with LLM integration and robust rule-based fallback.
"""

from typing import Dict, List, Any
import os
import re

def ask_mentor(message: str, student_context: Dict[str, Any] = None, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Handles student mentoring queries.
    Uses OpenAI/External LLM if API key is present in environment, otherwise falls back
    to the domain-trained deterministic Career Mentor Engine.
    """
    clean_msg = message.strip()
    if not clean_msg:
        return {"reply": "Please ask a question regarding your placement preparation, resume, or assessment results.", "source": "system"}

    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key and not openai_key.startswith("your-") and len(openai_key) > 20:
        try:
            return _call_external_llm(clean_msg, student_context, conversation_history, openai_key)
        except Exception:
            # Fall through gracefully to domain mentor
            pass

    # High-quality deterministic career intelligence fallback
    reply = _rule_based_career_mentor(clean_msg, student_context or {})
    return {"reply": reply, "source": "domain_mentor_engine"}

def _call_external_llm(message: str, student_context: Dict[str, Any], history: List[Dict[str, str]], api_key: str) -> Dict[str, Any]:
    """Calls OpenAI chat completion API with timeout and safe prompt framing."""
    import requests

    system_prompt = (
        "You are an expert AI Career Mentor for university placement candidates. "
        "Provide constructive, actionable, and encouraging career and interview guidance. "
        "Strictly adhere to these principles: "
        "1. Never promise guaranteed placement or fabricated salaries. "
        "2. Ground advice in the student's actual scores if provided. "
        "3. Emphasize actionable steps using the STAR method for behavioral questions "
        "and concrete coding/data patterns for technical questions."
    )

    if student_context:
        system_prompt += f"\nStudent Context: {student_context}"

    messages = [{"role": "system", "content": system_prompt}]
    if history:
        for turn in history[-6:]:
            messages.append({"role": turn.get("role", "user"), "content": turn.get("content", "")})
    messages.append({"role": "user", "content": message})

    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": "gpt-4o-mini", "messages": messages, "max_tokens": 600, "temperature": 0.7},
        timeout=10,
    )
    if resp.status_code == 200:
        data = resp.json()
        reply_text = data["choices"][0]["message"]["content"]
        return {"reply": reply_text, "source": "openai_llm"}
    else:
        raise RuntimeError(f"LLM API returned status {resp.status_code}")

def _rule_based_career_mentor(msg: str, ctx: Dict[str, Any]) -> str:
    """Domain-trained deterministic career advisor matching user intentions."""
    q = msg.lower()
    cgpa = ctx.get("CGPA", 7.5)
    comm = ctx.get("Communication_Skills", 7)
    projects = ctx.get("Projects_Completed", 2)
    internship = ctx.get("Internship_Experience", 1)

    # 1. Resume bullet point improvement
    if any(k in q for k in ["bullet", "resume bullet", "improve this", "action verb"]):
        return (
            "### ✍️ High-Impact Resume Bullet Optimization\n\n"
            "Use the **Google XYZ Formula**: *Accomplished [X] as measured by [Y], by doing [Z]*.\n\n"
            "**Before (Weak):**\n"
            "> *Worked on a placement prediction website using React and Flask.*\n\n"
            "**After (Impact-Driven):**\n"
            "> *Architected an end-to-end placement prediction SPA with React 19 and Flask REST API, achieving **90.5% model accuracy** and sub-50ms inference latency across 100+ simulated cohort candidates.*\n\n"
            "**Key Tips:**\n"
            "- Begin with strong action verbs: *Architected, Spearheaded, Engineered, Optimized, Containerized*.\n"
            "- Always include numerical evidence: latency reduction %, accuracy, lines of code, or test coverage."
        )

    # 2. Technical Interview Questions
    if any(k in q for k in ["technical question", "coding question", "mock technical", "interview question"]):
        return (
            "### 💻 Technical Interview Practice Questions\n\n"
            "Here are 3 core placement interview problems frequently tested by campus recruiters:\n\n"
            "1. **Data Structures:** Implement a function to find the lowest common ancestor (LCA) in a Binary Tree.\n"
            "   *Hint: Consider recursive depth-first search tracking left and right subtree matches.*\n"
            "2. **Databases / SQL:** Write a query to find the second highest salary without using `TOP` or `LIMIT`.\n"
            "   *Hint: Use `DENSE_RANK() OVER (ORDER BY salary DESC)` or `MAX(salary) WHERE salary < (MAX(salary))`.*\n"
            "3. **System Design:** How would you design a rate-limiting middleware for an API?\n"
            "   *Hint: Discuss Token Bucket vs. Leaky Bucket algorithms and Redis-backed counters.*"
        )

    # 3. HR / Behavioral Questions
    if any(k in q for k in ["hr", "behavioral", "star method", "tell me about yourself", "weakness"]):
        return (
            "### 🤝 Behavioral HR Interview Strategy (The STAR Method)\n\n"
            "When responding to behavioral questions, structure your response as follows:\n\n"
            "- **S (Situation):** Set the scene in 1-2 concise sentences.\n"
            "- **T (Task):** State the specific goal or challenge you were accountable for.\n"
            "- **A (Action):** Detail the individual technical or leadership steps you took.\n"
            "- **R (Result):** Conclude with quantifiable outcomes and what you learned.\n\n"
            "**Top 3 Questions to Rehearse:**\n"
            "1. *Tell me about a time you faced a technical conflict in a team project.*\n"
            "2. *Describe a situation where a project deadline was at risk and how you handled it.*\n"
            "3. *What is your biggest technical weakness, and what steps are you taking to address it?*"
        )

    # 4. Assessment / Placement Prediction Context
    if any(k in q for k in ["my prediction", "why not placed", "at-risk", "improve my score", "placement probability"]):
        return (
            f"### 📈 Diagnostics Based on Your Assessment Profile\n\n"
            f"- **Cumulative GPA:** {cgpa} / 10.0\n"
            f"- **Communication Skills:** {comm} / 10\n"
            f"- **Projects Completed:** {projects}\n"
            f"- **Internship Experience:** {'Yes' if internship == 1 else 'None'}\n\n"
            "**Key Drivers & Recommended Action:**\n"
            "1. **Communication (27.89% model weight):** If below 8, schedule weekly group discussions and record mock interview answers.\n"
            "2. **Projects (16.83% model weight):** Maintain at least 2 well-documented, full-stack or ML repositories on GitHub with live demos.\n"
            "3. **Simulate Scenarios:** Use the **What-If Placement Simulator** tab to test how boosting your metrics shifts your probability in real-time!"
        )

    # 5. Default General Mentor Response
    return (
        "### 🎓 AI Career Mentor\n\n"
        "I'm here to assist your placement journey! You can ask me to:\n\n"
        "- **Rehearse Interviews:** *'Give me 3 technical questions for Software Developer'* or *'How to answer: Tell me about yourself?'*\n"
        "- **Improve Resume:** *'Improve this resume bullet: built a weather app'*\n"
        "- **Skill Gap Remediation:** *'What skills do I need for a Data Analyst role?'*\n"
        "- **Assessment Diagnostics:** *'How can I raise my placement readiness score?'*\n\n"
        "What area would you like to focus on right now?"
    )
