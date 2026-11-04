"""
Comprehensive Test Suite for Strategic Career Advancement Platform (SCAP).
Validates authentication, role security, file validation, NLP parser,
resume scoring, ML skill categorization, bullet synthesizer, assessments, and database CRUD.
"""
import unittest
import time
from app import create_app
from database import db
from config import Config
from services.resume_parser import clean_and_normalize_text, extract_email, extract_phone, extract_skills, extract_sections
from services.resume_scorer import score_resume
from services.skill_classifier import skill_classifier
from services.resume_rewriter import synthesize_bullet_point
from services.assessment_service import AssessmentService

class TestSCAPPlatform(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.app.config['WTF_CSRF_ENABLED'] = False
        cls.client = cls.app.test_client()

    def setUp(self):
        db.init_db()
        # Always start tests with clean session
        with self.client.session_transaction() as sess:
            sess.clear()

    # 1. Authentication & Role-Based Authorization
    def test_01_user_registration_and_login(self):
        test_email = "test_candidate_1@scap.edu"
        
        # 1. Register candidate
        response = self.client.post('/register', data={
            'full_name': 'Candidate One',
            'email': test_email,
            'password': 'Password123',
            'confirm_password': 'Password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome", response.data)

        # Verify role is strictly 'user'
        user = db.get_user_by_email(test_email)
        self.assertIsNotNone(user)
        self.assertEqual(user['role'], 'user')

        # 2. Clear session to simulate a new guest attempting duplicate registration
        self.client.get('/logout')
        dup_resp = self.client.post('/register', data={
            'full_name': 'Duplicate User',
            'email': test_email,
            'password': 'Password123',
            'confirm_password': 'Password123'
        }, follow_redirects=True)
        self.assertIn(b"already exists", dup_resp.data)

    def test_02_admin_login_and_access_control(self):
        # 1. Candidate login
        self.client.get('/logout')
        self.client.post('/login', data={
            'email': 'test_candidate_1@scap.edu',
            'password': 'Password123'
        }, follow_redirects=True)
        
        # Non-admin trying to access admin dashboard should be blocked
        admin_resp = self.client.get('/admin/dashboard', follow_redirects=True)
        self.assertIn(b"Access denied", admin_resp.data)

        # 2. Admin login (clear session first)
        self.client.get('/logout')
        login_resp = self.client.post('/login', data={
            'email': Config.ADMIN_EMAIL,
            'password': Config.ADMIN_PASSWORD
        }, follow_redirects=True)
        self.assertEqual(login_resp.status_code, 200)
        self.assertIn(b"Administrator Control Center", login_resp.data)

        # Access admin dashboard as admin
        dash_resp = self.client.get('/admin/dashboard')
        self.assertEqual(dash_resp.status_code, 200)
        self.assertIn(b"Registered Candidates", dash_resp.data)

    # 2. NLP Resume Parser & Extraction Unit Tests
    def test_03_parser_regex_and_skill_detection(self):
        sample_text = """
        ALEX R. MORGAN
        Email: alex.morgan@example.com | Phone: (555) 234-5678
        Location: New York, NY

        EDUCATION
        B.S. in Computer Science, State University, 2024. GPA: 3.8/4.0

        TECHNICAL SKILLS
        Programming Languages: Python, JavaScript, TypeScript, SQL
        Frameworks: React, Flask, Django, Node.js
        Databases: Oracle Database, PostgreSQL, Redis
        DevOps: Docker, Git, AWS

        PROJECTS
        Campus Management System
        Developed full stack web application using Python Flask React and Oracle Database.
        Automated database schema migrations and reduced analytical query times by 35%.
        """
        clean = clean_and_normalize_text(sample_text)
        email = extract_email(clean)
        phone = extract_phone(clean)
        skills = extract_skills(clean)
        sections = extract_sections(clean)

        self.assertEqual(email, "alex.morgan@example.com")
        self.assertTrue("555" in phone)
        self.assertIn("Python", skills["all_skills"])
        self.assertIn("Oracle Database", skills["all_skills"])
        self.assertIn("React", skills["all_skills"])
        self.assertTrue(len(sections["education"]) > 10)
        self.assertTrue(len(sections["projects"]) > 10)

    # 3. Resume Quality Scoring Algorithm
    def test_04_resume_quality_scoring(self):
        parsed_mock = {
            "full_name": "Alex Morgan",
            "email": "alex@example.com",
            "phone": "555-123-4567",
            "education": "B.S. in Computer Science from State University, GPA 3.9",
            "experience": "Software Engineer Intern at Tech Corp for 6 months.",
            "projects": "Built RESTful microservice API using Flask, React, and Oracle Database with Docker containerization.",
            "technical_skills": ["Python", "Flask", "React", "Docker", "SQL", "Git", "Oracle Database", "TypeScript"],
            "categorized_skills": {
                "Languages": ["Python", "TypeScript", "SQL"],
                "Frameworks & Libraries": ["Flask", "React"],
                "Databases & Storage": ["Oracle Database"],
                "Cloud & DevOps": ["Docker"]
            },
            "raw_text": """Alex Morgan. Email: alex@example.com Phone: 555-123-4567.
            Education: B.S. in Computer Science.
            Projects: Developed full stack app using Python and Oracle. Implemented REST APIs. Optimized queries by 40%. Automated build pipeline."""
        }
        score_result = score_resume(parsed_mock)
        
        # Verify 0-100 bounds
        self.assertGreaterEqual(score_result["total"], 0)
        self.assertLessEqual(score_result["total"], 100)
        
        # Verify 5 components
        self.assertIn("completeness", score_result)
        self.assertIn("skills", score_result)
        self.assertIn("projects", score_result)
        self.assertIn("action_verbs", score_result)
        self.assertIn("readability", score_result)
        self.assertTrue(len(score_result["suggestions"]) > 0 or len(score_result["strengths"]) > 0)

    # 4. ML Model 3: Technical Skill Categorization
    def test_05_skill_classifier_prediction(self):
        web_dev_text = "Proficient in Python Flask Django React JavaScript HTML5 CSS3 REST APIs and PostgreSQL database."
        pred_web = skill_classifier.predict_category(web_dev_text)
        self.assertEqual(pred_web["primary_category"], "Software and Web Development")
        self.assertGreater(pred_web["confidence"], 0.35)

        data_sci_text = "Data scientist skilled in Python Pandas NumPy Matplotlib Seaborn SQL exploratory data analysis and statistics."
        pred_ds = skill_classifier.predict_category(data_sci_text)
        self.assertEqual(pred_ds["primary_category"], "Data Science and Analytics")
        self.assertGreater(pred_ds["confidence"], 0.35)

    # 5. ML Model 4: Resume Synthesizer & Factual Integrity
    def test_06_resume_synthesizer_rewriting(self):
        original = "Made a student management project using Python and Oracle."
        result = synthesize_bullet_point(original)
        
        self.assertIsNotNone(result)
        # Verify high-impact action verb substitution
        self.assertTrue(result["action_verb"] in ["Developed", "Implemented", "Engineered"])
        # Verify factual retention
        self.assertIn("Python", result["suggested"])
        self.assertIn("Oracle", result["suggested"])
        # Verify no hallucinated percentages
        self.assertNotIn("%", result["suggested"])

    # 6. Technical Interview & Aptitude Rubric Evaluation
    def test_07_assessment_evaluations(self):
        # MCQ Evaluation
        mcq_q = {
            "question_type": "MCQ",
            "correct_answer": "B",
            "explanation": "Encapsulation bundles data and methods."
        }
        is_correct, pts, fb = AssessmentService.evaluate_interview_response(mcq_q, "B")
        self.assertTrue(is_correct)
        self.assertEqual(pts, 10.0)

        # Descriptive Rubric Evaluation
        desc_q = {
            "question_type": "DESCRIPTIVE",
            "rubric_keywords": "idempotent,idempotency,GET,PUT,DELETE,POST",
            "explanation": "Idempotent operations yield identical state regardless of repetitions."
        }
        user_answer = "An operation is idempotent if multiple calls produce identical effects. Methods like GET and PUT are idempotent."
        is_ok, d_pts, d_fb = AssessmentService.evaluate_interview_response(desc_q, user_answer)
        self.assertGreaterEqual(d_pts, 5.0)
        self.assertTrue(is_ok)

    # 7. Database Layer & Versioning
    def test_08_database_versioning(self):
        # Create a unique test user for versioning validation
        uid = db.create_user("Version Tester", f"version_test_{int(time.time() * 1000)}@scap.edu", "dummyhash", "user")
        
        # Save resume v1
        rid1, v1 = db.save_resume(uid, "test_resume_v1.pdf", "/dummy/path1.pdf", "pdf", "raw text 1")
        self.assertEqual(v1, 1)

        # Save resume v2
        rid2, v2 = db.save_resume(uid, "test_resume_v2.pdf", "/dummy/path2.pdf", "pdf", "raw text 2")
        self.assertEqual(v2, 2)

        # Active resume should be v2
        latest = db.get_latest_resume_for_user(uid)
        self.assertEqual(latest['version_number'], 2)
        self.assertEqual(latest['resume_id'], rid2)

if __name__ == '__main__':
    unittest.main()
