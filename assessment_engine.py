"""
Smart Mock Interview & Assessment Module
Curated question banks across Technical, Aptitude, Domain-Specific, and HR assessments.
"""

from typing import Dict, List, Any
import random

QUESTION_BANKS: Dict[str, List[Dict[str, Any]]] = {
    "aptitude": [
        {
            "id": "apt_1",
            "category": "Quantitative Aptitude",
            "question": "A train 240 m long passes a pole in 24 seconds. How long will it take to pass a platform 650 m long?",
            "options": ["65 seconds", "89 seconds", "100 seconds", "150 seconds"],
            "correct_index": 1,
            "explanation": "Speed = 240 / 24 = 10 m/s. Total distance to cross platform = 240 + 650 = 890 m. Time = 890 / 10 = 89 seconds.",
        },
        {
            "id": "apt_2",
            "category": "Quantitative Aptitude",
            "question": "If 12 men can complete a project in 20 days, how many days will 15 men take to complete the same work?",
            "options": ["14 days", "16 days", "18 days", "25 days"],
            "correct_index": 1,
            "explanation": "Total man-days = 12 × 20 = 240. Days for 15 men = 240 / 15 = 16 days.",
        },
        {
            "id": "apt_3",
            "category": "Logical Reasoning",
            "question": "Look at this series: 7, 10, 8, 11, 9, 12, ... What number should come next?",
            "options": ["7", "10", "12", "13"],
            "correct_index": 1,
            "explanation": "Alternating series: (+3, -2, +3, -2, +3, -2). Next is 12 - 2 = 10.",
        },
        {
            "id": "apt_4",
            "category": "Logical Reasoning",
            "question": "Statements: All mangoes are golden-colored. No golden-colored things are cheap. Conclusions: 1) All mangoes are cheap. 2) Golden-colored mangoes are not cheap.",
            "options": ["Only (1) follows", "Only (2) follows", "Either (1) or (2) follows", "Neither follows"],
            "correct_index": 1,
            "explanation": "Since all mangoes are golden and golden things are not cheap, golden mangoes cannot be cheap.",
        },
        {
            "id": "apt_5",
            "category": "Verbal Ability",
            "question": "Choose the word most nearly opposite in meaning to 'METICULOUS':",
            "options": ["Careless", "Methodical", "Painstaking", "Accurate"],
            "correct_index": 0,
            "explanation": "'Meticulous' means showing great attention to detail. The direct antonym is 'Careless'.",
        },
    ],
    "technical_core": [
        {
            "id": "tech_1",
            "category": "Data Structures",
            "question": "What is the worst-case time complexity of searching for an element in an unbalanced Binary Search Tree (BST)?",
            "options": ["O(1)", "O(log N)", "O(N)", "O(N log N)"],
            "correct_index": 2,
            "explanation": "An unbalanced BST can degenerate into a linked list, leading to O(N) worst-case traversal time.",
        },
        {
            "id": "tech_2",
            "category": "Databases & SQL",
            "question": "Which SQL clause is used to filter records resulting from an aggregate function (such as COUNT or AVG)?",
            "options": ["WHERE", "HAVING", "GROUP BY", "ORDER BY"],
            "correct_index": 1,
            "explanation": "The HAVING clause was added to SQL because the WHERE keyword cannot be used with aggregate functions.",
        },
        {
            "id": "tech_3",
            "category": "Operating Systems",
            "question": "Which condition is NOT one of the four necessary Coffman conditions for a deadlock to occur?",
            "options": ["Mutual Exclusion", "Hold and Wait", "Preemption Allowed", "Circular Wait"],
            "correct_index": 2,
            "explanation": "Deadlock requires No Preemption (resources cannot be forcibly taken). If preemption is allowed, deadlock is avoided.",
        },
        {
            "id": "tech_4",
            "category": "Object Oriented Programming",
            "question": "Which OOP concept allows the same interface to perform different underlying forms or implementations?",
            "options": ["Encapsulation", "Polymorphism", "Inheritance", "Abstraction"],
            "correct_index": 1,
            "explanation": "Polymorphism means 'many forms' and enables runtime or compile-time method overloading and overriding.",
        },
        {
            "id": "tech_5",
            "category": "Computer Networks",
            "question": "At which layer of the OSI model does the TCP protocol operate?",
            "options": ["Network Layer", "Transport Layer", "Data Link Layer", "Session Layer"],
            "correct_index": 1,
            "explanation": "TCP and UDP are Transport Layer (Layer 4) protocols providing host-to-host communication services.",
        },
    ],
    "data_analyst": [
        {
            "id": "da_1",
            "category": "SQL & Analytics",
            "question": "In SQL, what is the key difference between RANK() and DENSE_RANK() window functions?",
            "options": [
                "RANK() ignores NULLs, DENSE_RANK() does not",
                "RANK() skips ranks after ties (e.g. 1, 2, 2, 4), while DENSE_RANK() does not (1, 2, 2, 3)",
                "DENSE_RANK() works only on integer columns",
                "RANK() can only be used with ORDER BY DESC",
            ],
            "correct_index": 1,
            "explanation": "RANK() produces gaps in the sequence upon ties, whereas DENSE_RANK() continues sequentially without gaps.",
        },
        {
            "id": "da_2",
            "category": "Statistics",
            "question": "If a data distribution is heavily right-skewed (positive skew), which relationship typically holds?",
            "options": [
                "Mean < Median < Mode",
                "Mean == Median == Mode",
                "Mode < Median < Mean",
                "Median < Mode < Mean",
            ],
            "correct_index": 2,
            "explanation": "In right-skewed distributions, high outliers pull the Mean to the right, so Mode < Median < Mean.",
        },
        {
            "id": "da_3",
            "category": "Python Pandas",
            "question": "Which Pandas method is best suited to reshape a DataFrame from long format to wide format?",
            "options": ["df.melt()", "df.pivot() or df.pivot_table()", "df.concat()", "df.dropna()"],
            "correct_index": 1,
            "explanation": "pivot() and pivot_table() reshape data from long to wide, while melt() does the reverse.",
        },
        {
            "id": "da_4",
            "category": "Business Intelligence",
            "question": "In dimensional data modeling, what type of table contains foreign keys referencing dimensions and numerical measures?",
            "options": ["Dimension Table", "Fact Table", "Bridge Table", "Lookup Table"],
            "correct_index": 1,
            "explanation": "Fact tables hold the quantitative metrics (measures) and foreign keys connecting to dimension tables.",
        },
    ],
    "software_developer": [
        {
            "id": "sd_1",
            "category": "Web & APIs",
            "question": "Which HTTP method is considered idempotent according to RFC 7231 standards?",
            "options": ["POST", "PATCH", "PUT", "CONNECT"],
            "correct_index": 2,
            "explanation": "PUT is idempotent because multiple identical PUT requests will result in the same server state as a single request.",
        },
        {
            "id": "sd_2",
            "category": "Version Control",
            "question": "What does 'git rebase' do compared to 'git merge'?",
            "options": [
                "Rebase deletes the commits, merge preserves them",
                "Rebase replays commits on top of another base tip for a linear history, while merge creates a merge commit",
                "Merge can only be used on the main branch",
                "Rebase pushes changes to the remote origin automatically",
            ],
            "correct_index": 1,
            "explanation": "Rebase rewrites project history by creating brand new commits for each commit in the original branch.",
        },
        {
            "id": "sd_3",
            "category": "System Design",
            "question": "In distributed caching, which cache invalidation pattern updates the cache and the primary database simultaneously?",
            "options": ["Cache-Aside", "Write-Through", "Write-Behind (Write-Back)", "Refresh-Ahead"],
            "correct_index": 1,
            "explanation": "Write-Through caches write data to both the cache and the database synchronously before returning success.",
        },
    ],
    "hr_behavioral": [
        {
            "id": "hr_1",
            "category": "STAR Competency",
            "question": "When asked: 'Tell me about a time you faced a tight deadline and unexpected setbacks', what is the most effective approach?",
            "options": [
                "Explain that your team members caused the delay and how you asked the manager for an extension",
                "Use the STAR method: describe the Situation, specific Task, the proactive Action you took, and the quantifiable Result",
                "State that you never face setbacks because your planning is always perfect",
                "Focus exclusively on complaining about how stressful the company timeline was",
            ],
            "correct_index": 1,
            "explanation": "Recruiters use behavioral questions to test resilience, accountability, and systematic problem solving via the STAR framework.",
        },
        {
            "id": "hr_2",
            "category": "Team Conflict",
            "question": "How should you answer: 'How do you handle disagreements with a peer over architectural or design choices?'",
            "options": [
                "Insist on your approach since you have the best coding style",
                "Escalate immediately to the department head without discussing it",
                "Focus on shared goals, evaluate data/benchmarks objectively, listen actively, and compromise on consensus",
                "Agree with whatever the other person says to avoid conflict",
            ],
            "correct_index": 2,
            "explanation": "Enterprise recruiters look for emotional intelligence, constructive collaboration, and evidence-driven technical compromise.",
        },
    ],
}

def get_test_catalog() -> List[Dict[str, Any]]:
    """Returns available mock assessment suites and metadata."""
    return [
        {
            "test_type": "aptitude",
            "title": "General Quantitative & Logical Aptitude",
            "description": "Timed evaluation covering Speed Math, Deductive Logic, and Verbal Comprehension.",
            "question_count": len(QUESTION_BANKS["aptitude"]),
            "time_limit_mins": 15,
            "icon": "🧠",
        },
        {
            "test_type": "technical_core",
            "title": "Computer Science Core Fundamentals",
            "description": "Essential placement topics: Data Structures, SQL, Operating Systems, OOP, and Networks.",
            "question_count": len(QUESTION_BANKS["technical_core"]),
            "time_limit_mins": 15,
            "icon": "⚙️",
        },
        {
            "test_type": "software_developer",
            "title": "Software Developer Technical Assessment",
            "description": "Practical software engineering: RESTful APIs, Git, System Design, and Concurrency.",
            "question_count": len(QUESTION_BANKS["software_developer"]),
            "time_limit_mins": 10,
            "icon": "💻",
        },
        {
            "test_type": "data_analyst",
            "title": "Data Analyst Domain Assessment",
            "description": "Advanced SQL, Statistical distributions, Dimensional modeling, and Data exploration.",
            "question_count": len(QUESTION_BANKS["data_analyst"]),
            "time_limit_mins": 12,
            "icon": "📊",
        },
        {
            "test_type": "hr_behavioral",
            "title": "HR & Behavioral Interview Competency",
            "description": "STAR methodology, conflict resolution, workplace ethics, and verbal communication.",
            "question_count": len(QUESTION_BANKS["hr_behavioral"]),
            "time_limit_mins": 8,
            "icon": "🤝",
        },
    ]

def get_test_questions(test_type: str) -> List[Dict[str, Any]]:
    """Returns questions for a test without correct answer indices (for client taking test)."""
    if test_type not in QUESTION_BANKS:
        raise ValueError(f"Unknown test type: {test_type}")

    questions = QUESTION_BANKS[test_type]
    sanitized = []
    for q in questions:
        sanitized.append({
            "id": q["id"],
            "category": q["category"],
            "question": q["question"],
            "options": q["options"],
        })
    return sanitized

def grade_test(test_type: str, user_answers: Dict[str, int]) -> Dict[str, Any]:
    """
    Grades user answers against the answer key.
    Computes overall score, category breakdowns, and personalized remedial suggestions.
    """
    if test_type not in QUESTION_BANKS:
        raise ValueError(f"Unknown test type: {test_type}")

    questions = QUESTION_BANKS[test_type]
    total = len(questions)
    correct_count = 0
    category_totals: Dict[str, int] = {}
    category_correct: Dict[str, int] = {}
    itemized_review = []

    for q in questions:
        qid = q["id"]
        cat = q["category"]
        category_totals[cat] = category_totals.get(cat, 0) + 1

        selected_idx = user_answers.get(qid)
        is_correct = (selected_idx == q["correct_index"])

        if is_correct:
            correct_count += 1
            category_correct[cat] = category_correct.get(cat, 0) + 1

        itemized_review.append({
            "id": qid,
            "question": q["question"],
            "category": cat,
            "selected_index": selected_idx,
            "correct_index": q["correct_index"],
            "is_correct": is_correct,
            "explanation": q["explanation"],
        })

    score_pct = round((correct_count / max(total, 1)) * 100, 1)

    # Category performance
    category_breakdown = {}
    weak_categories = []
    for cat, count in category_totals.items():
        corr = category_correct.get(cat, 0)
        pct = round((corr / count) * 100, 1)
        category_breakdown[cat] = {"correct": corr, "total": count, "percentage": pct}
        if pct < 60.0:
            weak_categories.append(cat)

    # Feedback rubric
    if score_pct >= 80:
        overall_verdict = "Excellent — Strong Mastery Demonstrated"
        recommendations = ["Continue maintaining timed practice to preserve speed and accuracy."]
    elif score_pct >= 60:
        overall_verdict = "Competent — Minor Remediation Required"
        recommendations = [f"Focus extra revision on weaker categories: {', '.join(weak_categories) if weak_categories else 'edge cases'}."]
    else:
        overall_verdict = "Needs Targeted Improvement"
        recommendations = [
            f"Review fundamental theory for: {', '.join(weak_categories)}.",
            "Work through the recommended Roadmap tasks for Week 2 & Week 5.",
            "Retake this assessment after 3 days of targeted revision.",
        ]

    return {
        "test_type": test_type,
        "score": correct_count,
        "total_questions": total,
        "percentage": score_pct,
        "passed": score_pct >= 60.0,
        "overall_verdict": overall_verdict,
        "category_breakdown": category_breakdown,
        "weak_categories": weak_categories,
        "recommendations": recommendations,
        "review": itemized_review,
    }
