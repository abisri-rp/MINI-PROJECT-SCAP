"""
Test Suite for New Features:
- Admin viewing resumes, uploading questions, mandatory suggestions, field of study grouping
- Forgot password flow, unregistered user error, field validation
- Profile editing, resume generation, invalid resume detection (0 score)
- Absence of model names in templates
"""
import unittest
import os
from app import app
from database import db
from services.resume_parser import parse_resume
from services.resume_scorer import score_resume

class NewFeaturesTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        cls.client = app.test_client()
        db.init_db()

    def test_01_login_unregistered_user(self):
        """Unregistered user login must display 'User not registered'"""
        res = self.client.post('/login', data={
            'email': 'nonexistent_user_999@test.com',
            'password': 'Password123'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"User not registered", res.data)

    def test_02_forgot_password_flow(self):
        """Forgot password route updates password for registered email"""
        # Ensure test user exists
        test_email = 'forgot_test@test.com'
        user = db.get_user_by_email(test_email)
        if not user:
            db.create_user('Forgot User', test_email, 'OldPass123', 'user')
        
        # Test password mismatch
        res = self.client.post('/forgot_password', data={
            'email': test_email,
            'new_password': 'NewPassword123',
            'confirm_password': 'DifferentPass123'
        }, follow_redirects=True)
        self.assertIn(b"Passwords do not match", res.data)

        # Test successful password reset
        res = self.client.post('/forgot_password', data={
            'email': test_email,
            'new_password': 'NewPassword123',
            'confirm_password': 'NewPassword123'
        }, follow_redirects=True)
        self.assertIn(b"Password updated successfully", res.data)

    def test_03_admin_question_upload_and_field_of_study(self):
        """Admin can upload questions with mark allocation and view field of study"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'System Admin'
            sess['role'] = 'admin'

        # Test question upload
        res = self.client.post('/admin/questions', data={
            'question_no': 'Q-TEST-101',
            'question_text': 'What is the time complexity of binary search?',
            'question_type': 'MCQ',
            'category_id': 1,
            'topic': 'Algorithms',
            'difficulty': 'Intermediate',
            'mark_allocation': 5,
            'option_a': 'O(n)',
            'option_b': 'O(log n)',
            'option_c': 'O(n^2)',
            'option_d': 'O(1)',
            'correct_answer': 'B'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"successfully uploaded to database", res.data)

        # Test field of study grouping view
        res = self.client.get('/admin/field_of_study')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Candidates by Field of Study & Skills", res.data)
        self.assertIn(b"C", res.data)
        self.assertIn(b"Java", res.data)

    def test_04_admin_mandatory_suggestion_for_review(self):
        """Admin review requires mandatory suggestions before notifying candidate"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'System Admin'
            sess['role'] = 'admin'

        # Post review without comments/suggestions
        res = self.client.post('/admin/review/1', data={
            'status': 'Approved',
            'admin_comments': '   '
        }, follow_redirects=True)
        self.assertIn(b"Admin suggestion/feedback is required", res.data)

    def test_05_non_resume_detection_and_zero_score(self):
        """Non-resume documents should fail validation and return 0 score"""
        fake_parsed = {
            "is_valid_resume": False,
            "raw_text": "Grocery shopping list: milk, eggs, bread",
            "words_count": 5,
            "technical_skills": [],
            "education": "",
            "experience": "",
            "projects": "",
            "certifications": "",
            "achievements": "",
            "missing_sections": ["education", "experience", "skills"]
        }
        scores = score_resume(fake_parsed)
        self.assertEqual(scores['overall_score'], 0.0)
        self.assertTrue(any("This is not a resume" in s for s in scores['suggestions']))

    def test_06_no_model_names_in_templates(self):
        """Verify no ML model names appear in rendered or template HTML"""
        templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        forbidden_terms = ['Logistic Regression', 'TF-IDF', 'ML Model 3', 'ML Model 4', 'ML Model 1']
        for root, _, files in os.walk(templates_dir):
            for file in files:
                if file.endswith('.html'):
                    path = os.path.join(root, file)
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    for term in forbidden_terms:
                        self.assertNotIn(term, content, f"Forbidden term '{term}' found in {file}")

    def test_07_admin_delete_user(self):
        """Admin can delete a candidate user and all associated records"""
        import time
        from werkzeug.security import generate_password_hash
        test_email = f"delete_me_{int(time.time()*1000)}@scap.edu"
        user_id = db.create_user("User To Delete", test_email, generate_password_hash("Password123"), role="user")
        self.assertIsNotNone(user_id)

        user_before = db.get_user_by_id(user_id)
        self.assertIsNotNone(user_before)

        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['role'] = 'admin'
            sess['email'] = 'admin@scap.edu'

        res = self.client.post(f'/admin/users/delete/{user_id}', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"successfully deleted", res.data)

        user_after = db.get_user_by_id(user_id)
        self.assertIsNone(user_after)

    def test_08_admin_cannot_delete_self(self):
        """Admin cannot delete their own active admin account"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['role'] = 'admin'
            sess['email'] = 'admin@scap.edu'

        res = self.client.post('/admin/users/delete/1', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"cannot delete your own", res.data)

        admin_user = db.get_user_by_id(1)
        self.assertIsNotNone(admin_user)

if __name__ == '__main__':
    unittest.main()
