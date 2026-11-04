import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import docx
from services.resume_parser import parse_resume
from app import create_app
from database import db

# 1. Create a non-resume DOCX (e.g. apple pie recipe)
non_resume_path = Path("uploads/non_resume_test.docx")
doc = docx.Document()
doc.add_heading("Delicious Apple Pie Recipe", 0)
doc.add_paragraph("Mix flour, butter, cinnamon, and sugar in a large bowl. Peel and slice 5 apples into thin slices.")
doc.add_paragraph("Preheat the oven to 375 degrees Fahrenheit. Bake for 45 minutes until golden brown. Serve hot with vanilla ice cream.")
doc.save(str(non_resume_path))

parsed_non_resume = parse_resume(non_resume_path)
print("Non-resume validation:", parsed_non_resume.get("is_valid_resume"))
print("Non-resume error message:", parsed_non_resume.get("error"))
assert parsed_non_resume.get("is_valid_resume") is False, "Non-resume must NOT be considered valid!"
assert parsed_non_resume.get("error") is not None, "Non-resume must have an error message!"

# 2. Create a valid resume DOCX
valid_resume_path = Path("uploads/valid_resume_test.docx")
doc2 = docx.Document()
doc2.add_heading("Jane Doe", 0)
doc2.add_paragraph("Email: jane.doe@example.com | Phone: +1-555-019-2834 | LinkedIn: linkedin.com/in/janedoe")
doc2.add_heading("Professional Summary", 1)
doc2.add_paragraph("Dedicated Computer Science and Engineering student with strong foundation in full-stack software development and database design.")
doc2.add_heading("Education", 1)
doc2.add_paragraph("Bachelor of Technology in Computer Science and Engineering, State University, 2026, CGPA: 9.1/10")
doc2.add_heading("Technical Skills", 1)
doc2.add_paragraph("Programming Languages: Python, Java, C++, SQL, JavaScript. Frameworks: Flask, React, Docker, Git.")
doc2.add_heading("Languages Known", 1)
doc2.add_paragraph("English, Spanish, French")
doc2.add_heading("Area of Interest", 1)
doc2.add_paragraph("Artificial Intelligence, Cloud Computing, Distributed Systems")
doc2.add_heading("Projects", 1)
doc2.add_paragraph("Automated Career Advancement Platform: Developed full-stack web application with relational database and automated resume analysis.")
doc2.save(str(valid_resume_path))

parsed_valid = parse_resume(valid_resume_path)
print("Valid resume validation:", parsed_valid.get("is_valid_resume"))
print("Languages known extracted:", parsed_valid.get("languages_known"))
print("Area of interest extracted:", parsed_valid.get("area_of_interest"))
assert parsed_valid.get("is_valid_resume") is True, "Valid resume must pass validation!"

# 3. Test Flask routes using test client
app = create_app()
with app.test_client() as client:
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['role'] = 'user'
        sess['full_name'] = 'Test Student'

    # Test Upload with non-resume
    with open(non_resume_path, 'rb') as f:
        resp = client.post('/resume/upload', data={'resume': (f, 'non_resume_test.docx')}, follow_redirects=True)
        assert resp.status_code == 200
        page_html = resp.data.decode('utf-8')
        assert "not in a valid resume format" in page_html, "Non-resume upload must show failure flash message!"
        assert "No quality score was given" in page_html, "Non-resume upload must state no score given!"
        assert "no technical domain was predicted" in page_html, "Non-resume upload must state no domain predicted!"
        print("Upload non-resume test PASSED: correctly rejected with danger flash, no score/domain assigned!")

    # Test Profile update with languages_known and area_of_interest
    resp_prof = client.post('/user/profile', data={
        'full_name': 'Test Student',
        'phone': '1234567890',
        'degree': 'B.Tech CSE',
        'institution': 'State Univ',
        'graduation_year': '2026',
        'skills': 'Python, SQL, React',
        'languages_known': 'English, Tamil, Hindi',
        'area_of_interest': 'Artificial Intelligence & Machine Learning',
        'bio': 'Aspiring AI engineer',
        'projects': 'NLP Platform',
        'experience': 'Intern at Tech Corp'
    }, follow_redirects=True)
    assert resp_prof.status_code == 200
    user_db = db.get_user_by_id(1)
    assert user_db.get('languages_known') == 'English, Tamil, Hindi'
    assert user_db.get('area_of_interest') == 'Artificial Intelligence & Machine Learning'
    print("User profile update with languages_known and area_of_interest PASSED!")

    # Test Generate Resume GET
    resp_gen = client.get('/user/generate_resume')
    assert resp_gen.status_code == 200
    gen_html = resp_gen.data.decode('utf-8')
    assert 'name="languages_known"' in gen_html, "generate_resume must have languages_known textbox!"
    assert 'name="area_of_interest"' in gen_html, "generate_resume must have area_of_interest textbox!"
    assert 'English, Tamil, Hindi' in gen_html, "generate_resume must display languages_known in resume sheet!"
    assert ('Artificial Intelligence &amp; Machine Learning' in gen_html or 'Artificial Intelligence' in gen_html), "generate_resume must display area_of_interest in resume sheet!"
    print("Resume Generator GET with textboxes and resume display PASSED!")

    # Test Generate Resume POST
    resp_gen_post = client.post('/user/generate_resume', data={
        'languages_known': 'English, French, German',
        'area_of_interest': 'Cloud Computing & DevOps',
        'skills': 'Python, Docker, Kubernetes'
    }, follow_redirects=True)
    assert resp_gen_post.status_code == 200
    user_db2 = db.get_user_by_id(1)
    assert user_db2.get('languages_known') == 'English, French, German'
    assert user_db2.get('area_of_interest') == 'Cloud Computing & DevOps'
    gen_post_html = resp_gen_post.data.decode('utf-8')
    assert 'English, French, German' in gen_post_html
    assert ('Cloud Computing &amp; DevOps' in gen_post_html or 'Cloud Computing' in gen_post_html)
    print("Resume Generator POST update PASSED!")

# Cleanup test files
non_resume_path.unlink(missing_ok=True)
valid_resume_path.unlink(missing_ok=True)
print("\nALL VERIFICATION TESTS COMPLETED WITH 100% SUCCESS!")
