"""
Personalized Career Improvement Roadmap Engine
Generates customized 8-week developmental milestones based on actual student evaluation data.
"""

from typing import Dict, List, Any


def generate_personalized_roadmap(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Builds an 8-week milestone roadmap based on candidate weaknesses and strengths.
    Deterministic, actionable, and tailored to input features.
    """
    cgpa = float(profile.get("CGPA", 7.0))
    comm = int(profile.get("Communication_Skills", 6))
    projects = int(profile.get("Projects_Completed", 1))
    internship = int(profile.get("Internship_Experience", 0))
    acad = int(profile.get("Academic_Performance", 6))

    tasks = []

    # -------------------------------------------------------------------------
    # Week 1: Diagnostic & Core Academic Foundations
    # -------------------------------------------------------------------------
    tasks.append(
        {
            "week_number": 1,
            "title": "Placement Diagnostic & Resume Baseline Audit",
            "category": "Career Preparation",
            "priority": "High",
            "description": "Consolidate academic transcripts, build an initial ATS-friendly resume draft, and document current skill gaps.",
            "relevance_reason": "Establishing a clean baseline profile ensures targeted improvements over the 8-week preparation window.",
            "resources": [
                {
                    "title": "Harvard Career Services Resume Guide",
                    "url": "https://careerservices.fas.harvard.edu/resources/create-a-strong-resume/",
                },
                {
                    "title": "ATS Resume Formats & Checklist",
                    "url": "https://www.overleaf.com/gallery/tagged/cv",
                },
            ],
            "deadline": "Week 1, Day 5",
            "status": "pending",
        }
    )

    if cgpa < 7.5 or acad < 7:
        tasks.append(
            {
                "week_number": 1,
                "title": "Academic Grade Remediation Plan",
                "category": "Academics",
                "priority": "High",
                "description": f"Current CGPA is {cgpa:.2f}. Create a weekly study schedule targeting current semester core theory subjects to elevate GPA past 7.5 recruitment cutoffs.",
                "relevance_reason": "Many tier-1 campus recruiters enforce a hard eligibility barrier at 7.0 or 7.5 CGPA.",
                "resources": [
                    {
                        "title": "Pomodoro Academic Study Techniques",
                        "url": "https://todoist.com/productivity-methods/pomodoro-technique",
                    }
                ],
                "deadline": "Week 1, Day 7",
                "status": "pending",
            }
        )

    # -------------------------------------------------------------------------
    # Week 2: Aptitude & Problem Solving Foundations
    # -------------------------------------------------------------------------
    tasks.append(
        {
            "week_number": 2,
            "title": "Quantitative & Logical Aptitude Sprint (Part 1)",
            "category": "Aptitude",
            "priority": "High",
            "description": "Complete 50 practice problems covering Speed Math, Percentages, Ratios, and Syllogisms under timed conditions.",
            "relevance_reason": "Aptitude tests are the universal stage-1 elimination round in campus placement drives.",
            "resources": [
                {
                    "title": "IndiaBIX Quantitative Aptitude",
                    "url": "https://www.indiabix.com/aptitude/questions-and-answers/",
                },
                {
                    "title": "GeeksforGeeks Placement Aptitude Practice",
                    "url": "https://www.geeksforgeeks.org/placements-gq/",
                },
            ],
            "deadline": "Week 2, Day 7",
            "status": "pending",
        }
    )

    # -------------------------------------------------------------------------
    # Week 3: Communication & Soft Skills Deep Dive
    # -------------------------------------------------------------------------
    if comm < 8:
        tasks.append(
            {
                "week_number": 3,
                "title": "Behavioral Interview Prep & STAR Storytelling",
                "category": "Communication",
                "priority": "High" if comm < 6 else "Medium",
                "description": f"Communication score is currently {comm}/10. Draft and record 5 STAR method (Situation, Task, Action, Result) stories for common behavioral questions.",
                "relevance_reason": "Communication skills constitute 27.89% of placement model importance; interviewers heavily weigh articulation.",
                "resources": [
                    {
                        "title": "STAR Method Interview Guide (MIT Career)",
                        "url": "https://capd.mit.edu/resources/the-star-method-for-interviews/",
                    },
                    {
                        "title": "Top 25 Behavioral Questions",
                        "url": "https://www.themuse.com/advice/behavioral-interview-questions-answers-examples",
                    },
                ],
                "deadline": "Week 3, Day 6",
                "status": "pending",
            }
        )
    else:
        tasks.append(
            {
                "week_number": 3,
                "title": "Advanced Executive Communication & Group Discussion",
                "category": "Communication",
                "priority": "Medium",
                "description": "Practice spontaneous topic presentation and formal group discussion moderation techniques.",
                "relevance_reason": "Refining your already solid communication skills unlocks leadership and client-facing engineering roles.",
                "resources": [
                    {
                        "title": "Group Discussion Masterclass Guidelines",
                        "url": "https://www.geeksforgeeks.org/group-discussion-tips-for-campus-placements/",
                    }
                ],
                "deadline": "Week 3, Day 6",
                "status": "pending",
            }
        )

    # -------------------------------------------------------------------------
    # Week 4: Technical Portfolio & Projects Sprint
    # -------------------------------------------------------------------------
    if projects < 3:
        tasks.append(
            {
                "week_number": 4,
                "title": "Build & Deploy a Production Capstone Project",
                "category": "Technical & Projects",
                "priority": "High",
                "description": f"You currently have {projects} project(s). Develop a full-stack web or data engineering project with documentation, unit tests, and a live deployed URL.",
                "relevance_reason": "Projects completed contributes 16.83% to prediction weight and provides concrete evidence of technical depth.",
                "resources": [
                    {
                        "title": "freeCodeCamp Project Tutorials",
                        "url": "https://www.freecodecamp.org/news/",
                    },
                    {
                        "title": "Build Your Own X GitHub Directory",
                        "url": "https://github.com/codecrafters-io/build-your-own-x",
                    },
                ],
                "deadline": "Week 4, Day 7",
                "status": "pending",
            }
        )
    else:
        tasks.append(
            {
                "week_number": 4,
                "title": "Architecture Deep-Dive of Existing Projects",
                "category": "Technical & Projects",
                "priority": "Medium",
                "description": "Document system architecture diagrams, database schemas, and performance benchmarks for your top 2 completed projects.",
                "relevance_reason": "Technical interviewers inspect project design decisions, concurrency choices, and data modeling trade-offs.",
                "resources": [
                    {
                        "title": "System Design Primer",
                        "url": "https://github.com/donnemartin/system-design-primer",
                    }
                ],
                "deadline": "Week 4, Day 7",
                "status": "pending",
            }
        )

    # -------------------------------------------------------------------------
    # Week 5: Data Structures & Algorithms / Coding Practice
    # -------------------------------------------------------------------------
    tasks.append(
        {
            "week_number": 5,
            "title": "Core DSA & Coding Challenge Intensive",
            "category": "Technical & Projects",
            "priority": "High",
            "description": "Solve 30 intermediate-level problems focusing on Arrays, Hash Maps, Binary Trees, and Two-Pointer patterns.",
            "relevance_reason": "Coding assessments are mandatory for standard software development and data engineering positions.",
            "resources": [
                {
                    "title": "NeetCode 150 Problem Roadmap",
                    "url": "https://neetcode.io/practice",
                },
                {
                    "title": "LeetCode Curated Placement 75",
                    "url": "https://leetcode.com/studyplan/leetcode-75/",
                },
            ],
            "deadline": "Week 5, Day 7",
            "status": "pending",
        }
    )

    # -------------------------------------------------------------------------
    # Week 6: Industrial Experience & Open Source Fellowship
    # -------------------------------------------------------------------------
    if internship == 0:
        tasks.append(
            {
                "week_number": 6,
                "title": "Virtual Internship / Open Source Contribution",
                "category": "Internships & Career",
                "priority": "High",
                "description": "Complete a simulated industry job simulation on Forage or submit 2 meaningful pull requests to popular open-source repositories.",
                "relevance_reason": "Real-world codebase experience bridges the gap when formal corporate internship experience is missing.",
                "resources": [
                    {
                        "title": "Forage Industry Job Simulations",
                        "url": "https://www.theforage.com/",
                    },
                    {
                        "title": "Good First Issue Open Source Finder",
                        "url": "https://goodfirstissue.dev/",
                    },
                ],
                "deadline": "Week 6, Day 7",
                "status": "pending",
            }
        )
    else:
        tasks.append(
            {
                "week_number": 6,
                "title": "Internship Impact Metrics & Case Study Formulation",
                "category": "Internships & Career",
                "priority": "Medium",
                "description": "Quantify deliverables from your internship tenure (e.g. latency reduced, features delivered, bugs resolved) for resume bullet points.",
                "relevance_reason": "Strong internship articulation distinguishes good candidates from exceptional candidates.",
                "resources": [
                    {
                        "title": "Google XYZ Resume Formula Guide",
                        "url": "https://www.inc.com/bill-murphy-jr/google-recruiters-say-these-5-words-are-best-way-to-describe-your-work-experience.html",
                    }
                ],
                "deadline": "Week 6, Day 7",
                "status": "pending",
            }
        )

    # -------------------------------------------------------------------------
    # Week 7: Mock Technical & HR Interviews
    # -------------------------------------------------------------------------
    tasks.append(
        {
            "week_number": 7,
            "title": "Full-Length Timed Mock Interview Assessment",
            "category": "Mock Interviews",
            "priority": "High",
            "description": "Complete at least 2 full-length simulated mock interviews (one technical MCQ/coding, one HR/behavioral). Review detailed scorecard analytics.",
            "relevance_reason": "Practicing under authentic exam pressure eliminates test anxiety and pinpoints final weak topics.",
            "resources": [
                {
                    "title": "Pramp Free Peer Mock Interviews",
                    "url": "https://www.pramp.com/",
                }
            ],
            "deadline": "Week 7, Day 6",
            "status": "pending",
        }
    )

    # -------------------------------------------------------------------------
    # Week 8: Final Placement Readiness Certification & Review
    # -------------------------------------------------------------------------
    tasks.append(
        {
            "week_number": 8,
            "title": "Target Role Application Review & Mentor Sign-Off",
            "category": "Career Preparation",
            "priority": "High",
            "description": "Review final What-If placement simulation score, verify updated resume, and review application pipeline with your assigned TPO mentor.",
            "relevance_reason": "Final milestone ensuring full alignment with company recruitment eligibility criteria.",
            "resources": [
                {"title": "College Placement Cell Application Portal", "url": "#"}
            ],
            "deadline": "Week 8, Day 7",
            "status": "pending",
        }
    )

    return tasks
