"""
Resume Parsing and NLP Extraction Pipeline (ML Model 1).
Extracts text from PDF (PyMuPDF / pypdf) and DOCX (python-docx), normalizes whitespace,
extracts contact information, sections, and technical skills using rule-based NLP and dictionaries.
"""
import re
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Try PyMuPDF (fitz), fall back to pypdf
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# Try spaCy for NER, fall back to robust rule-based extractor
try:
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
        SPACY_AVAILABLE = True
    except Exception:
        SPACY_AVAILABLE = False
except ImportError:
    SPACY_AVAILABLE = False

# Comprehensive Skill Taxonomy
DEFAULT_SKILL_TAXONOMY = {
    "Languages": [
        "python", "javascript", "typescript", "java", "c++", "c", "c#", "go", "golang",
        "ruby", "php", "rust", "swift", "kotlin", "scala", "r", "dart", "sql", "bash", "shell"
    ],
    "Frameworks & Libraries": [
        "react", "react.js", "reactjs", "angular", "vue", "vue.js", "vuejs", "next.js", "nextjs",
        "node.js", "nodejs", "express", "express.js", "flask", "django", "fastapi", "spring",
        "spring boot", ".net", "dotnet", "laravel", "rails", "ruby on rails", "redux", "tailwind",
        "bootstrap", "jquery", "scikit-learn", "sklearn", "tensorflow", "pytorch", "keras",
        "pandas", "numpy", "matplotlib", "seaborn", "opencv", "spacy", "nltk", "huggingface"
    ],
    "Databases & Storage": [
        "oracle", "oracle database", "oracledb", "pl/sql", "mysql", "postgresql", "postgres",
        "sqlite", "mongodb", "redis", "cassandra", "dynamodb", "mariadb", "snowflake", "bigquery"
    ],
    "Cloud & DevOps": [
        "aws", "amazon web services", "azure", "gcp", "google cloud", "docker", "kubernetes",
        "k8s", "jenkins", "gitlab ci", "github actions", "ci/cd", "terraform", "ansible",
        "linux", "unix", "nginx", "apache", "helm"
    ],
    "Tools & Methodologies": [
        "git", "github", "gitlab", "jira", "agile", "scrum", "rest api", "restful", "graphql",
        "microservices", "unit testing", "ci/cd", "postman", "power bi", "tableau", "excel"
    ]
}

def extract_text_from_pdf(file_path):
    """Extracts text using PyMuPDF if available, otherwise pypdf."""
    text = ""
    file_path = str(file_path)
    if PYMUPDF_AVAILABLE:
        try:
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text() + "\n"
            doc.close()
            if text.strip():
                return text
        except Exception as e:
            logger.warning(f"PyMuPDF failed on {file_path}: {e}")

    if PYPDF_AVAILABLE:
        try:
            reader = pypdf.PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
        except Exception as e:
            logger.error(f"pypdf extraction failed on {file_path}: {e}")

    return text

def extract_text_from_docx(file_path):
    """Extracts text from DOCX file using python-docx."""
    if not DOCX_AVAILABLE:
        logger.error("python-docx is not installed.")
        return ""
    try:
        doc = docx.Document(str(file_path))
        full_text = []
        for para in doc.paragraphs:
            if para.text:
                full_text.append(para.text)
        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_text:
                    full_text.append(" | ".join(row_text))
        return "\n".join(full_text)
    except Exception as e:
        logger.error(f"python-docx extraction failed on {file_path}: {e}")
        return ""

def clean_and_normalize_text(text):
    """Normalizes whitespace, removes control chars and standardizes linebreaks."""
    if not text:
        return ""
    # Standardize CRLF to LF
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # Replace non-breaking spaces and tabs
    text = text.replace('\xa0', ' ').replace('\t', ' ')
    # Normalize multiple horizontal spaces
    text = re.sub(r'[ ]{2,}', ' ', text)
    # Normalize multiple vertical spaces (max 2 consecutive newlines)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def extract_email(text):
    """Extracts candidate email using regex."""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    matches = re.findall(email_pattern, text)
    return matches[0] if matches else ""

def extract_phone(text):
    """Extracts candidate phone number supporting US and international formats."""
    phone_pattern = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    matches = re.findall(phone_pattern, text)
    # Filter out year ranges like 2019-2023
    for m in matches:
        digits = re.sub(r'\D', '', m)
        if len(digits) >= 10:
            return m
    return ""

def extract_name(text):
    """Extracts candidate name using heuristic rules and NER."""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not lines:
        return "Candidate"

    # Often candidate name is the first prominent header line
    for line in lines[:4]:
        # Ignore headers like RESUME, CURRICULUM VITAE
        if re.search(r'^(resume|curriculum vitae|cv|profile|contact)$', line, re.IGNORECASE):
            continue
        # Avoid lines with email or phone or links
        if "@" in line or re.search(r'\d{5,}', line) or "http" in line or "github" in line:
            continue
        # Check if line looks like a human name (2 to 4 capitalized words)
        words = line.split()
        if 1 <= len(words) <= 4 and all(re.match(r'^[A-Z][a-zA-Z.\'-]*$', w) for w in words):
            return line

    return lines[0][:60]

def extract_skills(text, custom_skills=None):
    """Detects technical skills matching skill taxonomy."""
    text_lower = text.lower()
    detected = {
        "Languages": set(),
        "Frameworks & Libraries": set(),
        "Databases & Storage": set(),
        "Cloud & DevOps": set(),
        "Tools & Methodologies": set(),
        "Other": set()
    }
    all_flat = set()

    taxonomy = DEFAULT_SKILL_TAXONOMY.copy()
    if custom_skills:
        for s in custom_skills:
            cat = s.get("category_name", "Other")
            if cat not in taxonomy:
                taxonomy[cat] = []
            taxonomy[cat].append(s.get("skill_name", "").lower())

    for cat_name, skill_list in taxonomy.items():
        target_bucket = cat_name if cat_name in detected else "Other"
        for s in skill_list:
            # Word boundary regex to avoid false positives (e.g., 'c' in 'candidate')
            if s in ["c", "r"]:
                pattern = r'(?:\b|(?<=[^a-zA-Z]))' + re.escape(s) + r'(?:\b|(?=[^a-zA-Z]))'
            elif s in ["c++", "c#", ".net"]:
                pattern = r'(?:\b|(?<=\s))' + re.escape(s) + r'(?:\b|(?=\s|,|\.))'
            else:
                pattern = r'\b' + re.escape(s) + r'\b'
            
            if re.search(pattern, text_lower):
                clean_name = s.title()
                if s in ["sql", "html5", "css3", "aws", "gcp", "nlp", "ci/cd", "rest api", "rdbms"]:
                    clean_name = s.upper()
                elif s == "javascript":
                    clean_name = "JavaScript"
                elif s == "typescript":
                    clean_name = "TypeScript"
                elif s == "postgresql" or s == "postgres":
                    clean_name = "PostgreSQL"
                elif s == "mongodb":
                    clean_name = "MongoDB"
                elif s == "docker":
                    clean_name = "Docker"
                elif s == "kubernetes":
                    clean_name = "Kubernetes"
                elif s == "node.js" or s == "nodejs":
                    clean_name = "Node.js"
                elif s == "react" or s == "react.js":
                    clean_name = "React"
                elif s == "scikit-learn" or s == "sklearn":
                    clean_name = "scikit-learn"
                elif s == "oracle" or s == "oracle database":
                    clean_name = "Oracle Database"

                detected[target_bucket].add(clean_name)
                all_flat.add(clean_name)

    return {
        "categorized": {k: sorted(list(v)) for k, v in detected.items() if v},
        "all_skills": sorted(list(all_flat))
    }

def extract_sections(text):
    """Identifies and segments resume sections using regex anchors."""
    section_patterns = {
        "education": r'(?:education|academic background|qualifications|academic credentials)',
        "experience": r'(?:experience|work experience|employment history|professional experience|internship|internships)',
        "projects": r'(?:projects|academic projects|key projects|personal projects)',
        "skills": r'(?:technical skills|skills|technologies|proficiencies|core competencies)',
        "certifications": r'(?:certifications|certificates|licenses|courses)',
        "achievements": r'(?:achievements|awards|honors|extracurricular activities)'
    }

    sections = {k: "" for k in section_patterns}
    lines = text.split('\n')
    current_sec = None
    buffer = {k: [] for k in section_patterns}

    for line in lines:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue
        
        # Check if line is a section header (short, capitalized or matching patterns)
        header_found = False
        for sec_name, pattern in section_patterns.items():
            if re.search(r'^\s*(?:[\#\*\-]\s*)?' + pattern + r'\s*[:\-]?\s*$', cleaned_line, re.IGNORECASE) and len(cleaned_line) < 40:
                current_sec = sec_name
                header_found = True
                break

        if not header_found and current_sec:
            buffer[current_sec].append(cleaned_line)

    for k in buffer:
        sections[k] = "\n".join(buffer[k])

    return sections

def extract_languages_known(text):
    """Detects natural/spoken languages known from resume text."""
    pattern = r'(?:languages\s+known|spoken\s+languages|languages\s+spoken|languages)\s*[:\-]\s*([^\n\r]+)'
    m = re.search(pattern, text, re.IGNORECASE)
    if m:
        val = m.group(1).strip()
        val = re.sub(r'[\.;]+$', '', val).strip()
        # Avoid technical languages accidentally captured here
        if len(val) <= 120 and not any(k in val.lower() for k in ["python", "c++", "javascript", "java", "sql", "html"]):
            return val
    return ""

def extract_area_of_interest(text):
    """Detects area of interest or technical specialization from resume text."""
    pattern = r'(?:areas?\s+of\s+interest|areas?\s+of\s+specialization|technical\s+interests?|interests)\s*[:\-]\s*([^\n\r]+)'
    m = re.search(pattern, text, re.IGNORECASE)
    if m:
        val = m.group(1).strip()
        val = re.sub(r'[\.;]+$', '', val).strip()
        if len(val) <= 150:
            return val
    return ""

def parse_resume(file_path, custom_skills=None):
    """
    Main entry point for parsing and structuring a resume file.
    Returns a comprehensive structured profile dictionary with validation.
    """
    path = Path(file_path)
    ext = path.suffix.lower().replace('.', '')
    
    if ext == "pdf":
        raw_text = extract_text_from_pdf(path)
    elif ext == "docx":
        raw_text = extract_text_from_docx(path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}. Expected PDF or DOCX.")

    clean_text = clean_and_normalize_text(raw_text)
    if not clean_text or len(clean_text.strip()) < 30:
        return {
            "error": "Failed to extract readable text. The document may be empty, image-only, or password-protected.",
            "raw_text": "",
            "confidence": 0.0,
            "is_valid_resume": False
        }

    email = extract_email(clean_text)
    phone = extract_phone(clean_text)
    name = extract_name(clean_text)
    sections = extract_sections(clean_text)
    skills_data = extract_skills(clean_text, custom_skills)
    languages_known = extract_languages_known(clean_text)
    area_of_interest = extract_area_of_interest(clean_text)

    # Missing sections detection
    missing_sections = []
    for s_name, s_content in sections.items():
        if not s_content.strip():
            # If skills section wasn't an explicit header but skills were detected in text
            if s_name == "skills" and len(skills_data["all_skills"]) >= 3:
                continue
            missing_sections.append(s_name.capitalize())

    # Extraction confidence estimate
    confidence = 1.0
    if not email:
        confidence -= 0.2
    if not phone:
        confidence -= 0.1
    if len(skills_data["all_skills"]) < 3:
        confidence -= 0.2
    if len(missing_sections) > 2:
        confidence -= 0.2
    confidence = max(0.2, round(confidence, 2))

    # --- Strict Resume Format Validation ---
    clean_lower = clean_text.lower()
    words_count = len(clean_text.split())

    # 1. Contact info check
    has_contact = bool(email or phone)

    # 2. Education keywords check
    education_terms = [
        "education", "academic", "bachelor", "master", "degree", "university",
        "college", "institute", "gpa", "cgpa", "b.tech", "b.e", "m.tech",
        "b.sc", "bca", "mca", "diploma", "school", "coursework", "graduation"
    ]
    has_education = any(re.search(r'\b' + re.escape(t) + r'\b', clean_lower) for t in education_terms)

    # 3. Experience / Projects / Internships check
    experience_terms = [
        "experience", "work history", "employment", "internship", "internships",
        "project", "projects", "responsibilities", "work experience",
        "professional experience", "contributions", "key achievements"
    ]
    has_experience_or_projects = any(re.search(r'\b' + re.escape(t) + r'\b', clean_lower) for t in experience_terms)

    # 4. Technical skills check
    skills_terms = [
        "skills", "technical skills", "technologies", "proficiencies",
        "core competencies", "tools & technologies", "technical proficiencies"
    ]
    has_skills_header = any(t in clean_lower for t in skills_terms)
    has_detected_skills = len(skills_data["all_skills"]) >= 2
    has_skills = has_skills_header or has_detected_skills

    # 5. Resume Header / Identity keywords
    resume_id_terms = [
        "resume", "curriculum vitae", "cv", "career objective",
        "professional summary", "about me", "summary of qualifications"
    ]
    has_resume_marker = any(t in clean_lower for t in resume_id_terms)

    # 6. Anti-resume keywords (invoices, recipes, homework, purchase orders, book excerpts, assignments)
    anti_resume_terms = [
        "invoice", "billing address", "shipping address", "subtotal", "amount due",
        "receipt", "purchase order", "ingredients", "preheat oven", "tablespoon",
        "chapter 1", "chapter 2", "terms and conditions", "license agreement",
        "homework assignment", "question paper", "assignment no", "assignment topics",
        "teamwork topics", "course code", "roll no.", "roll no", "lab manual",
        "textbook referred", "textbooks referred", "web references", "course outcome"
    ]
    is_anti_resume = any(t in clean_lower for t in anti_resume_terms)

    # Validation criteria:
    # A valid resume must have:
    # - Reasonable word length (at least 45 words)
    # - Must not contain explicit non-resume document markers (invoices, recipes, agreements)
    # - Core section context: must include candidate Education OR Experience/Projects
    # - Supporting profile context: must include Contact details OR Technical Skills OR explicit Resume header
    # - Must have at least 3 distinct structural indicators
    indicator_score = sum([has_contact, has_education, has_experience_or_projects, has_skills, has_resume_marker])
    has_academic_or_work = (has_education or has_experience_or_projects)
    has_profile_context = (has_contact or has_skills or has_resume_marker)

    is_valid_resume = (
        (words_count >= 45) and
        not is_anti_resume and
        has_academic_or_work and
        has_profile_context and
        (indicator_score >= 3)
    )

    error_msg = None
    if not is_valid_resume:
        error_msg = (
            "The uploaded document does not appear to be in a valid resume format. "
            "A standard resume requires structural sections such as contact information, education, technical skills, and experience or projects."
        )

    return {
        "full_name": name,
        "email": email,
        "phone": phone,
        "education": sections.get("education", ""),
        "experience": sections.get("experience", ""),
        "projects": sections.get("projects", ""),
        "certifications": sections.get("certifications", ""),
        "achievements": sections.get("achievements", ""),
        "technical_skills": skills_data["all_skills"],
        "categorized_skills": skills_data["categorized"],
        "programming_languages": skills_data["categorized"].get("Languages", []),
        "frameworks_tools": (
            skills_data["categorized"].get("Frameworks & Libraries", []) +
            skills_data["categorized"].get("Tools & Methodologies", [])
        ),
        "languages_known": languages_known,
        "area_of_interest": area_of_interest,
        "missing_sections": missing_sections,
        "extraction_confidence": confidence if is_valid_resume else 0.0,
        "is_valid_resume": is_valid_resume,
        "words_count": words_count,
        "raw_text": clean_text,
        "error": error_msg
    }
