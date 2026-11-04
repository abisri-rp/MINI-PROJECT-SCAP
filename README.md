# STRATEGIC CAREER ADVANCEMENT PLATFORM AND RESUME SYNTHESIZER (SCAP)

**A Full-Stack Career Intelligence, Resume NLP Synthesis, and Assessment Platform**  
*College Mini-Project Implementation*

---

## 📌 Executive Summary

The **Strategic Career Advancement Platform and Resume Synthesizer (SCAP)** is a comprehensive web-based career advancement system. It analyzes technical resumes, extracts structured candidate information using Natural Language Processing (NLP), calculates 5-component advisory quality scores, suggests fact-preserving bullet point syntheses, classifies candidates into technical domains using scikit-learn, and delivers personalized technical mock interviews and aptitude assessments in a continuous **closed-loop progression pipeline**.

The platform is designed with two distinct, role-secured portals:
1. **Candidate User Portal** — Dashboard, profile verification, resume upload, advisory quality scoring, resume synthesizer, domain taxonomy, mock interviews, aptitude exams, and progress tracking.
2. **Administrator & Faculty Portal** — System KPI analytics, candidate user management, review queue, domain verification, extraction error corrections, and improvement requests.

---

## 🔄 Closed-Loop Career Advancement Architecture

```
[Candidate Registration & Login]
              ↓
      [Resume Upload] (PDF / DOCX)
              ↓
  [ML Model 1: NLP Extraction] (PyMuPDF / pypdf, python-docx, Regex, Skill Taxonomy)
              ↓
 [ML Model 2: Quality Scoring] (5 Factors: Completeness, Skills, Projects, Verbs, Readability)
              ↓
[ML Model 3: Skill Classification] (TF-IDF Vectorizer + Logistic Regression, 93.3% Accuracy)
              ↓
 [Admin Review & Verification] (Approved / Improvement Required + Feedback Comments)
              ↓
[ML Model 4: Resume Synthesizer] (Action-Verb Transformation, Factual Preservation)
              ↓
  [Technical Mock Interview] (Category-Specific MCQs + Descriptive Rubric Evaluation)
              ↓
    [Aptitude Assessment] (Quantitative, Logical, Verbal Timed Evaluation)
              ↓
[Closed-Loop Progress Tracking] (Version Evolution, Weak Topic Detection, Recommended Resources)
```

---

## 🛠️ Technology Stack

| Layer | Technologies | Purpose |
|---|---|---|
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla ES6) | Modern responsive dashboard, score meters, dropzone upload, timer clock |
| **Backend** | Python 3.13, Flask 3.1 | Modular Blueprints, session auth, RESTful endpoints, CSRF protection |
| **Database** | **Oracle Database 19c/21c XE**, `python-oracledb` | Enterprise relational database, identity columns, foreign keys, bind variables |
| **Fallback DB** | SQLite3 (`sqlite3`) | Automatic zero-configuration fallback if Oracle XE service is offline |
| **Document NLP** | PyMuPDF, `pypdf`, `python-docx`, Regular Expressions | Multi-format text extraction, regex contact parser, section segmentation |
| **Machine Learning**| `scikit-learn`, `numpy`, `pandas`, `joblib` | TF-IDF feature extraction, Logistic Regression (6 categories), model persistence |
| **Scoring Engine** | Weighted Rule-Based Algorithm | Transparent 0–100 advisory quality scoring across 5 weighted components |
| **Synthesizer** | Rule & Template Engine + Action Verb Mapping | Factual bullet point refinement without fabricating percentages or skills |

---

## 🗄️ Database Architecture & Relational Schema

The database architecture is normalized with relational constraints, primary keys, foreign keys with `ON DELETE CASCADE`, and check constraints across 14 tables:

1. **`USERS`**: Manages authentication, hashed passwords (`scrypt`), and roles (`user`, `admin`).
2. **`RESUME`**: Tracks resume versions per candidate (`pdf`, `docx`), file paths, raw text, and active version status.
3. **`RESUME_ANALYSIS`**: Stores extracted JSON profiles, 5 component scores, total advisory score, predicted category, and confidence.
4. **`ADMIN_REVIEW`**: Records admin determinations (`Pending Review`, `Approved`, `Improvement Required`), verified categories, and audit comments.
5. **`SKILL_CATEGORY`**: Master catalog of the 6 technical career domains.
6. **`SKILL`**: 40+ categorized technical skills with alias matching patterns.
7. **`USER_SKILL`**: Detected candidate skill associations linked to specific resume versions.
8. **`RESUME_SUGGESTION`**: Stores original bullets, revised action-verb bullets, status (`PENDING`, `ACCEPTED`, `REJECTED`, `EDITED`), and custom text.
9. **`QUESTION_BANK`**: Curated technical questions (MCQ + descriptive with rubric keywords) and aptitude questions (Quant, Logical, Verbal).
10. **`MOCK_INTERVIEW`**: Records technical interview sessions, chosen difficulty, and final scores.
11. **`INTERVIEW_RESPONSE`**: Captures candidate responses, points earned, and algorithmic rubric feedback.
12. **`APTITUDE_ATTEMPT`**: Tracks timed aptitude exams, overall percentage, and sectional scores.
13. **`APTITUDE_RESPONSE`**: Records individual MCQ selections and correctness.
14. **`LEARNING_RESOURCE`**: Maps recommended guides, tutorials, and practice resources to weak topics and career tracks.

---

## 🤖 Machine Learning Models Specification

### Model 1: NLP Resume Parser & Extraction
- **Input:** Raw binary PDF or DOCX file.
- **Engine:** PyMuPDF (`fitz`) with automatic fallback to `pypdf.PdfReader` and `docx.Document`.
- **Extraction Logic:**
  - Standardizes text and normalizes whitespace.
  - Regex patterns for email and international/US phone formats.
  - Pattern-based section segmentation: Education, Experience, Projects, Skills, Certifications, Achievements.
  - Multi-token word-boundary dictionary matching against 40+ skills with aliases.

### Model 2: Resume Quality Scoring Algorithm
- **Range:** 0 to 100 points.
- **Components:**
  1. *Section Completeness* (20 pts): Validates contact details, education, skills, projects, and experience.
  2. *Relevant Skills Breadth* (20 pts): Rewards technical volume and cross-domain stack diversity.
  3. *Project Description Depth* (20 pts): Evaluates architecture keywords, technical tools, and word density.
  4. *Action Verbs & Metrics* (20 pts): Assesses decisive engineering verbs and quantitative evidence.
  5. *Readability & Formatting* (20 pts): Penalizes run-on blocks; rewards structured bullet points and standard length.
- **Advisory Disclaimer:** Explicitly stated as an advisory quality score, not a scientifically validated hiring score.

### Model 3: Technical Skill Categorization Classifier
- **Model:** Logistic Regression with balanced class weighting.
- **Vectorization:** TF-IDF with unigrams + bigrams (`ngram_range=(1,2)`), sublinear term frequency scaling, and English stopword elimination.
- **Categories:**
  1. *Software and Web Development*
  2. *Data Science and Analytics*
  3. *Artificial Intelligence and Machine Learning*
  4. *Database Development*
  5. *Networking and Cybersecurity*
  6. *Cloud Computing and DevOps*
- **Evaluation Performance (Unseen Test Split):**
  - **Accuracy:** 93.3%
  - **Precision:** 95.2%
  - **Recall:** 93.3%
  - **F1-Score:** 93.5%
- **Artifacts:** Serialized in `ml/models/skill_classifier.joblib` and `ml/models/tfidf_vectorizer.joblib`.
- **Uncertainty Guard:** Flags classification uncertainty if top probability < 35%.

### Model 4: Resume Synthesizer & Bullet Point Rewriter
- **Goal:** Transforms passive, vague bullets into high-impact accomplishment statements.
- **Verb Taxonomy:** Developed, Implemented, Designed, Automated, Optimized, Analyzed, Built, Tested, Improved.
- **Strict Guardrails:** Preserves 100% of factual context. **Never hallucinates fake percentages, metrics, tools, or responsibilities**.
- **Interactive Workflow:** Candidates can Accept, Reject, or Manually Edit every suggestion.

---

## 🚀 Installation & Execution Guide

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Optional: Oracle Database 19c or 21c Express Edition (XE)

### 2. Environment Setup
```bash
# Clone or navigate to the workspace
cd c:\Users\abira\SCAP

# Install required dependencies
python -m pip install -r requirements.txt
```

### 3. Database Configuration (.env)
The platform features a **universal connection layer**:
- Set `DB_ENGINE=auto` in `.env`: The app will attempt to connect to Oracle XE on `localhost:1521/XEPDB1`. If the Oracle service is offline or unreachable, it **automatically falls back to local SQLite** (`scap_database.db`) with zero manual effort and zero downtime!

To test and configure native Oracle Database:
```powershell
# 1. Start Oracle XE services in PowerShell (as Administrator)
Start-Service OracleServiceXE
Start-Service OracleOraDB21Home1TNSListener

# 2. Run the automated Oracle setup script
python oracle_setup.py
```

### 4. Retrain or Verify ML Models (Optional)
The ML models are already pre-trained and serialized. To retrain from scratch:
```bash
python ml/prepare_dataset.py
python ml/train_classifier.py
```

### 5. Run the Automated Test Suite
```bash
python -m unittest tests/test_scap.py
```
*(All 8 end-to-end integration tests will run and pass: Auth, Role Security, Parser, Scorer, ML Classifier, Synthesizer, Assessments, and DB Versioning).*

### 6. Launch the Web Application
```bash
python app.py
```
Open your browser and navigate to:
**`http://127.0.0.1:5000`**

---

## 🔑 Default Credentials for Evaluation

| Role | Email | Password | Access Privileges |
|---|---|---|---|
| **Administrator** | `admin@scap.edu` | `Admin@SCAP2026` | Admin Dashboard, Candidate Reviews, KPI Analytics |
| **New Candidate** | Click **Register** on UI | *(Choose any password)* | Candidate Portal, Upload, Synthesizer, Tests |

*(Note: On the login page, you can click the **"👑 Administrator Account Auto-Fill"** button for 1-click evaluation access).*

---

## 📂 Project Directory Structure

```
SCAP/
├── app.py                      # Main Flask application & routes registration
├── config.py                   # Configuration, upload limits, database settings
├── database.py                 # Universal database layer (Oracle DB + SQLite fallback)
├── oracle_setup.py             # Diagnostic and DDL execution script for Oracle XE
├── requirements.txt            # Python dependencies specification
├── schema.sql                  # Enterprise Oracle SQL 14-table relational DDL
├── seed_data.sql               # Curated Oracle SQL seed data (admin, skills, questions)
├── .env                        # Local environment variables
├── .env.example                # Template environment variables
├── README.md                   # Complete architectural & operational guide
│
├── routes/                     # Modular Flask Blueprints
│   ├── auth.py                 # Session authentication & role-based access control
│   ├── user.py                 # Candidate user dashboard & profile
│   ├── resume.py               # Resume upload, parsing, scoring & synthesizer
│   ├── admin.py                # Admin portal, candidate reviews & KPI tracking
│   └── assessments.py          # Technical mock interviews & aptitude tests
│
├── services/                   # Business Logic & Model Inference
│   ├── resume_parser.py        # PDF/DOCX text parsing, regex, section segmentation
│   ├── resume_scorer.py        # 5-factor 0-100 advisory quality scoring algorithm
│   ├── skill_classifier.py     # ML Model 3 inference with confidence calibration
│   ├── resume_rewriter.py      # ML Model 4 bullet synthesizer & factual guardrails
│   └── assessment_service.py   # Rubric keyword evaluator & aptitude sectional scorer
│
├── ml/                         # Machine Learning Modules
│   ├── prepare_dataset.py      # Generates 120 curated profiles across 6 domains
│   ├── train_classifier.py     # Trains TF-IDF + Logistic Regression (93.3% accuracy)
│   ├── dataset/
│   │   └── resume_data.csv     # Labeled training dataset
│   └── models/
│       ├── skill_classifier.joblib   # Persisted scikit-learn classifier
│       ├── tfidf_vectorizer.joblib   # Persisted TF-IDF vectorizer
│       └── metrics.json              # Accuracy, precision, recall & confusion matrix
│
├── samples/                    # Pre-packaged Sample Resumes for Testing
│   ├── sample_software_engineer_resume.docx
│   └── sample_data_scientist_resume.pdf
│
├── static/
│   ├── css/
│   │   └── style.css           # Modern, responsive design system & UI components
│   └── js/
│       └── app.js              # Drag & drop upload, quiz timer, synthesizer AJAX
│
├── templates/                  # Jinja2 Modular Templates
│   ├── base.html               # Responsive sidebar, navigation & database indicator
│   ├── index.html              # Landing page with 12-step closed-loop workflow
│   ├── login.html              # Sign-in card with demo auto-fill
│   ├── register.html           # Candidate registration form
│   ├── user_dashboard.html     # Candidate overview with status & scores
│   ├── profile.html            # Profile details & skills inventory
│   ├── upload_resume.html      # Drag & drop upload workstation
│   ├── resume_analysis.html    # 5-factor score breakdown & profile verification
│   ├── resume_synthesizer.html # Original vs revised bullet comparison workstation
│   ├── skill_category.html     # ML category confidence & domain taxonomy
│   ├── technical_interview.html# Category-filtered mock interview (MCQ + Descriptive)
│   ├── interview_result.html   # Rubric scoring & conceptual feedback
│   ├── aptitude_test.html      # 15-minute timed aptitude examination
│   ├── aptitude_result.html    # Sectional performance & weak area detection
│   ├── assessment_history.html # Historical assessment attempts archive
│   ├── progress.html           # Closed-loop version timeline & recommended resources
│   ├── admin_dashboard.html    # System analytics & 7 KPI metric cards
│   ├── admin_users.html        # Candidate directory
│   ├── admin_reviews_list.html # Review queue
│   ├── admin_review.html       # Admin review & verification workstation
│   └── error.html              # Clean 404, 413, and 500 error pages
│
└── tests/
    └── test_scap.py            # Comprehensive 8-suite automated integration tests
```

---

## 🏆 Demonstration Workflows for College Project Evaluation

To demonstrate the complete closed-loop workflow during viva/evaluation:

1. **Candidate Registration & Login:**
   - Go to `http://127.0.0.1:5000/register` and create an account.
2. **Resume Upload & NLP Parsing:**
   - Navigate to **Upload Resume**. Drag and drop `samples/sample_software_engineer_resume.docx` or `samples/sample_data_scientist_resume.pdf`.
   - The NLP pipeline extracts candidate contact info, sections, and technical skills.
3. **Inspect Advisory Quality Score & Domain:**
   - The system displays the 5-factor quality score (e.g. 82/100) and predicts the technical category (*Software and Web Development* or *Data Science and Analytics*) with high statistical confidence.
4. **Candidate Profile Verification:**
   - On the Analysis page, candidates can modify parsed fields and click **"Save Verified Profile & Recalculate Score"**.
5. **Resume Synthesizer:**
   - Open **Resume Synthesizer**. Inspect passive sentences transformed into active engineering accomplishment statements. Click **Accept**, **Keep Original**, or **Edit Manually**.
6. **Faculty / Admin Review:**
   - In another browser window or incognito tab, log in as `admin@scap.edu` (Password: `Admin@SCAP2026`).
   - Open **Resume Reviews**, click **Review & Verify**, inspect the component scores, verify the category, enter faculty comments, and change status to **Approved**.
   - Notice the status updates immediately on the candidate's dashboard!
7. **Technical Mock Interview:**
   - As the candidate, take a technical interview filtered for your predicted category. Answer both MCQs and descriptive architectural questions.
   - The system runs objective evaluation on MCQs and transparent keyword rubric scoring on descriptive answers.
8. **Timed Aptitude Assessment:**
   - Complete the 15-minute aptitude assessment across Quantitative, Logical, and Verbal sections.
   - View your sectional breakdown and identified weak topics.
9. **Closed-Loop Progress & Learning Resources:**
   - Open **Progress Tracking**. Observe your resume score evolution across versions, assessment scores over time, and customized learning links tailored to your detected weak areas!
