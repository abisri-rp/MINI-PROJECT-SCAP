"""
Resume Quality Scoring Algorithm (ML Model 2).
Calculates a transparent, weighted 0-100 advisory quality score across 5 key components:
1. Section Completeness (20 points)
2. Relevant Skills (20 points)
3. Project Descriptions (20 points)
4. Action Verbs and Achievements (20 points)
5. Readability and Formatting (20 points)
"""
import re

STRONG_ACTION_VERBS = [
    "developed", "implemented", "designed", "automated", "optimized",
    "analyzed", "built", "tested", "improved", "architected", "deployed",
    "engineered", "refactored", "orchestrated", "spearheaded", "accelerated",
    "established", "integrated", "monitored", "configured", "collaborated"
]

WEAK_VERBS = ["worked on", "helped", "responsible for", "handled", "assisted", "did", "made"]

def score_resume(parsed_data, target_role=None):
    """
    Evaluates resume quality across 5 explicit components.
    Returns:
    - total_score (0-100)
    - component_scores (dict)
    - suggestions (list of feedback strings)
    - strengths (list of positive highlights)
    """
    # If document was detected as not being a valid resume format, do NOT calculate or provide any quality score
    if not parsed_data.get("is_valid_resume", True):
        return {
            "total": 0.0,
            "overall_score": 0.0,
            "has_score": False,
            "completeness": 0.0,
            "skills": 0.0,
            "projects": 0.0,
            "action_verbs": 0.0,
            "readability": 0.0,
            "is_valid_resume": False,
            "error": "The uploaded document is not in a valid resume format. Quality scoring is disabled.",
            "suggestions": [
                "This is not a resume. No quality score was calculated because the uploaded file is not in a recognized resume format.",
                "Ensure your document contains standard resume sections: Candidate Contact Info, Education, Technical Skills, and Projects/Experience.",
                "Advisory quality score and technical domain prediction are suspended."
            ],
            "strengths": []
        }

    text = parsed_data.get("raw_text", "")
    text_lower = text.lower()
    suggestions = []
    strengths = []

    # ---------------- 1. Section Completeness (Max 20 pts) ----------------
    completeness_score = 0
    # Contact info (4 pts)
    has_email = bool(parsed_data.get("email"))
    has_phone = bool(parsed_data.get("phone"))
    if has_email and has_phone:
        completeness_score += 4
        strengths.append("Complete contact details (Email and Phone) provided.")
    elif has_email or has_phone:
        completeness_score += 2
        suggestions.append("Add missing contact details (ensure both email and phone are present).")
    else:
        suggestions.append("Critical: Contact details (email and phone number) are missing.")

    # Education (4 pts)
    edu = parsed_data.get("education", "")
    if len(edu.strip()) > 30 or any(deg in text_lower for deg in ["bachelor", "b.tech", "b.e", "m.tech", "master", "degree", "university", "gpa", "cgpa"]):
        completeness_score += 4
        strengths.append("Education section is clearly outlined.")
    else:
        suggestions.append("Education section is incomplete. Specify your degree, major, university, and graduation year/GPA.")

    # Skills section (4 pts)
    skills = parsed_data.get("technical_skills", [])
    if len(skills) >= 6:
        completeness_score += 4
    elif len(skills) >= 2:
        completeness_score += 2
        suggestions.append("Add more technical proficiencies to build a comprehensive skills profile.")
    else:
        suggestions.append("Skills section appears sparse or missing. Group your core technical skills clearly.")

    # Projects section (4 pts)
    proj = parsed_data.get("projects", "")
    if len(proj.strip()) > 50 or "project" in text_lower:
        completeness_score += 4
    else:
        suggestions.append("Include a dedicated Academic or Personal Projects section highlighting hands-on work.")

    # Experience or Extracurricular/Certifications (4 pts)
    exp = parsed_data.get("experience", "")
    certs = parsed_data.get("certifications", "")
    if len(exp.strip()) > 40 or len(certs.strip()) > 30:
        completeness_score += 4
    else:
        completeness_score += 2
        suggestions.append("Enhance practical experience with internships, freelance work, or technical certifications.")

    # ---------------- 2. Relevant Technical Skills (Max 20 pts) ----------------
    skills_score = 0
    skill_count = len(skills)
    cat_skills = parsed_data.get("categorized_skills", {})

    # Volume & Diversity
    if skill_count >= 12:
        skills_score += 10
        strengths.append(f"Strong technical breadth with {skill_count} detected skills.")
    elif skill_count >= 7:
        skills_score += 8
    elif skill_count >= 4:
        skills_score += 5
        suggestions.append("Broaden your technical stack by listing modern frameworks, tools, or databases.")
    else:
        skills_score += 2
        suggestions.append("Very few technical skills detected. Ensure your tools and languages are clearly enumerated.")

    # Category balance (languages + frameworks + DBs/cloud)
    active_categories = sum(1 for cat, s_list in cat_skills.items() if len(s_list) > 0)
    if active_categories >= 3:
        skills_score += 10
        strengths.append("Well-balanced stack encompassing languages, frameworks, and database/DevOps tools.")
    elif active_categories == 2:
        skills_score += 6
        suggestions.append("Complement your programming languages with databases, DevOps tools, or cloud platforms.")
    else:
        skills_score += 3
        suggestions.append("Group your technical skills into categorized buckets (Languages, Frameworks, Databases, Tools).")

    # ---------------- 3. Project Descriptions (Max 20 pts) ----------------
    projects_score = 0
    # Evaluate project depth and technical detail
    tech_keywords_in_projects = sum(1 for s in skills if s.lower() in proj.lower())
    project_words = len(proj.split()) if proj else len(text.split()) // 3

    if project_words >= 150:
        projects_score += 8
    elif project_words >= 60:
        projects_score += 5
    else:
        projects_score += 2
        suggestions.append("Expand project descriptions with problem statement, system architecture, and solution overview.")

    if tech_keywords_in_projects >= 4:
        projects_score += 8
        strengths.append("Project descriptions explicitly mention modern tools and implementation technologies.")
    elif tech_keywords_in_projects >= 2:
        projects_score += 5
        suggestions.append("Add more technical detail to project descriptions (e.g., specific libraries, databases, APIs used).")
    else:
        projects_score += 2
        suggestions.append("Mention which technologies, database engines, or frameworks were utilized in each project.")

    # Architecture / Methodology mentions
    if any(k in text_lower for k in ["rest api", "mvc", "crud", "microservice", "pipeline", "schema", "responsive", "authentication"]):
        projects_score += 4
    else:
        suggestions.append("Highlight design patterns or architectural aspects (e.g., REST APIs, MVC, Docker containers).")

    # ---------------- 4. Action Verbs & Achievements (Max 20 pts) ----------------
    verbs_score = 0
    found_verbs = [v for v in STRONG_ACTION_VERBS if re.search(r'\b' + v + r'\b', text_lower)]
    found_weak = [v for v in WEAK_VERBS if v in text_lower]

    verb_count = len(found_verbs)
    if verb_count >= 7:
        verbs_score += 10
        strengths.append(f"Excellent use of high-impact engineering action verbs ({', '.join(found_verbs[:4])}).")
    elif verb_count >= 4:
        verbs_score += 7
    elif verb_count >= 2:
        verbs_score += 4
        suggestions.append("Use stronger engineering action verbs (e.g., Developed, Optimized, Implemented, Automated).")
    else:
        verbs_score += 2
        suggestions.append("Avoid passive language; begin each bullet point with a decisive action verb.")

    # Measurable Results & Metrics (numbers, percentages, times)
    metric_matches = re.findall(r'(?:\d+%\s*|\b\d+x\b|\b\d+\+?\s*(?:users|queries|records|requests|hours|seconds|ms|days))', text_lower)
    if len(metric_matches) >= 3:
        verbs_score += 10
        strengths.append("Impactful quantitative evidence and measurable outcomes included.")
    elif len(metric_matches) >= 1:
        verbs_score += 6
        suggestions.append("Include measurable results (e.g., reduced query runtime, automated 80% of data loading) when supported by evidence.")
    else:
        verbs_score += 3
        suggestions.append("Quantify the impact of your projects where possible (e.g., system scale, accuracy metrics, latency improvements).")

    # ---------------- 5. Readability & Formatting (Max 20 pts) ----------------
    readability_score = 0
    words = text.split()
    total_words = len(words)

    # Word count appropriateness (300 - 800 words is standard for a 1-page student resume)
    if 300 <= total_words <= 800:
        readability_score += 8
        strengths.append("Ideal resume length and information density for a concise technical resume.")
    elif 200 <= total_words < 300:
        readability_score += 5
        suggestions.append("Resume content is relatively brief; consider expanding project bullet points and coursework.")
    elif total_words > 1000:
        readability_score += 4
        suggestions.append("Resume exceeds 1,000 words. Condense descriptions into focused, high-impact bullet points.")
    else:
        readability_score += 3
        suggestions.append("Document length is very short. Provide more detailed technical context.")

    # Bullet point structure
    bullet_count = len(re.findall(r'^\s*[-•*]\s+', text, re.MULTILINE))
    if bullet_count >= 8:
        readability_score += 7
        strengths.append("Well-structured with clean bullet points for easy scanning.")
    elif bullet_count >= 3:
        readability_score += 5
    else:
        readability_score += 2
        suggestions.append("Use structured bullet points instead of dense paragraphs to enhance readability.")

    # Section organization
    line_lengths = [len(line.strip()) for line in text.split('\n') if line.strip()]
    avg_len = sum(line_lengths) / max(len(line_lengths), 1)
    if avg_len < 120:  # Avoid excessive run-on lines
        readability_score += 5
    else:
        readability_score += 2
        suggestions.append("Break up long, unbroken blocks of text into concise bullet points.")

    # Cap component scores at 20
    completeness_score = min(20.0, float(completeness_score))
    skills_score = min(20.0, float(skills_score))
    projects_score = min(20.0, float(projects_score))
    verbs_score = min(20.0, float(verbs_score))
    readability_score = min(20.0, float(readability_score))

    total = round(completeness_score + skills_score + projects_score + verbs_score + readability_score, 1)

    return {
        "total": total,
        "completeness": completeness_score,
        "skills": skills_score,
        "projects": projects_score,
        "action_verbs": verbs_score,
        "readability": readability_score,
        "suggestions": suggestions,
        "strengths": strengths,
        "disclaimer": "This advisory score is an algorithmic resume quality benchmark designed for structured improvement. It does not guarantee employment or replacement of human hiring evaluations."
    }
