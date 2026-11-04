"""
User Portal Routes.
Renders the primary student dashboard, candidate profile, and aggregated status overviews.
"""
import json
from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from routes.auth import login_required
from database import db

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    user = db.get_user_by_id(user_id)
    latest_resume = db.get_latest_resume_for_user(user_id)
    latest_analysis = db.get_latest_analysis_for_user(user_id)
    interviews = db.get_user_interviews(user_id)
    aptitudes = db.get_user_aptitude_attempts(user_id)
    user_skills = db.get_user_skills(user_id)

    # Parse JSON fields if available
    extracted_data = {}
    feedback_data = {}
    if latest_analysis:
        try:
            extracted_data = json.loads(latest_analysis.get('extracted_json') or '{}')
        except Exception:
            extracted_data = {}
        try:
            feedback_data = json.loads(latest_analysis.get('feedback_json') or '{}')
        except Exception:
            feedback_data = {}

    # Verify if document is not a resume
    import os
    from services.resume_parser import parse_resume
    if latest_resume and latest_resume.get('file_path') and os.path.exists(str(latest_resume['file_path'])):
        if extracted_data.get('is_valid_resume') is not False:
            custom_skills = db.get_all_skills()
            current_parsed = parse_resume(latest_resume['file_path'], custom_skills)
            if not current_parsed.get('is_valid_resume') or current_parsed.get('error'):
                extracted_data['is_valid_resume'] = False
                extracted_data['error'] = current_parsed.get('error')
                if latest_analysis:
                    latest_analysis['total_score'] = 0
                    latest_analysis['completeness_score'] = 0
                    latest_analysis['skills_score'] = 0
                    latest_analysis['projects_score'] = 0
                    latest_analysis['verbs_score'] = 0
                    latest_analysis['readability_score'] = 0
                    latest_analysis['predicted_category'] = 'Not a Resume'

    latest_interview = interviews[0] if interviews else None
    latest_aptitude = aptitudes[0] if aptitudes else None

    return render_template(
        'user_dashboard.html',
        user=user,
        latest_resume=latest_resume,
        latest_analysis=latest_analysis,
        extracted_data=extracted_data,
        feedback_data=feedback_data,
        user_skills=user_skills,
        latest_interview=latest_interview,
        latest_aptitude=latest_aptitude,
        total_interviews=len(interviews),
        total_aptitude=len(aptitudes)
    )

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session['user_id']
    user = db.get_user_by_id(user_id)
    skills = db.get_user_skills(user_id)
    resumes = db.get_all_resumes_for_user(user_id)

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip() or user.get('full_name')
        phone = request.form.get('phone', '').strip()
        degree = request.form.get('degree', '').strip()
        institution = request.form.get('institution', '').strip()
        graduation_year = request.form.get('graduation_year', '').strip()
        skills_input = request.form.get('skills', '').strip()
        experience = request.form.get('experience', '').strip()
        projects = request.form.get('projects', '').strip()
        bio = request.form.get('bio', '').strip()
        linkedin_url = request.form.get('linkedin_url', '').strip()
        github_url = request.form.get('github_url', '').strip()

        languages_known = request.form.get('languages_known', '').strip()
        area_of_interest = request.form.get('area_of_interest', '').strip()

        profile_dict = {
            'full_name': full_name,
            'phone': phone,
            'degree': degree,
            'institution': institution,
            'graduation_year': graduation_year,
            'skills': skills_input,
            'experience': experience,
            'projects': projects,
            'bio': bio,
            'linkedin_url': linkedin_url,
            'github_url': github_url,
            'languages_known': languages_known,
            'area_of_interest': area_of_interest
        }

        db.update_user_profile(user_id, profile_dict)
        session['full_name'] = full_name

        # Sync skills to USER_SKILL if an active resume exists
        if skills_input and resumes and len(resumes) > 0:
            skill_list = [s.strip() for s in skills_input.split(',') if s.strip()]
            active_resume_id = resumes[0]['resume_id']
            db.save_user_skills(user_id, active_resume_id, skill_list)

        flash("Candidate profile details saved successfully! You can now generate your verified resume.", "success")
        return redirect(url_for('user.profile'))

    return render_template('profile.html', user=user, skills=skills, resumes=resumes)

@user_bp.route('/populate_from_resume')
@login_required
def populate_from_resume():
    user_id = session['user_id']
    latest_analysis = db.get_latest_analysis_for_user(user_id)
    if not latest_analysis or not latest_analysis.get('extracted_json'):
        flash("No parsed resume found. Please upload a resume first or enter details manually.", "warning")
        return redirect(url_for('user.profile'))

    try:
        extracted = json.loads(latest_analysis['extracted_json'])
        curr = db.get_user_by_id(user_id)

        profile_dict = {
            'full_name': extracted.get('full_name') or curr.get('full_name'),
            'phone': extracted.get('phone') or curr.get('phone'),
            'degree': curr.get('degree') or 'Bachelor of Technology in Computer Science',
            'institution': extracted.get('education') or curr.get('institution') or 'University Institute of Engineering',
            'graduation_year': curr.get('graduation_year') or '2026',
            'skills': ", ".join(extracted.get('technical_skills', [])) or curr.get('skills'),
            'experience': extracted.get('experience') or curr.get('experience'),
            'projects': extracted.get('projects') or curr.get('projects'),
            'bio': curr.get('bio') or f"Dedicated software engineering candidate with technical focus in {latest_analysis.get('predicted_category', 'Software Engineering')}.",
            'linkedin_url': curr.get('linkedin_url'),
            'github_url': curr.get('github_url'),
            'languages_known': extracted.get('languages_known') or curr.get('languages_known') or 'English',
            'area_of_interest': extracted.get('area_of_interest') or curr.get('area_of_interest') or latest_analysis.get('predicted_category', 'Software Engineering')
        }

        db.update_user_profile(user_id, profile_dict)
        flash("Successfully auto-filled profile details from your uploaded resume! You can review and adjust any field below.", "success")
    except Exception as e:
        flash(f"Error populating profile from resume: {e}", "danger")

    return redirect(url_for('user.profile'))

@user_bp.route('/generate_resume', methods=['GET', 'POST'])
@login_required
def generate_resume():
    user_id = session['user_id']
    curr_user = db.get_user_by_id(user_id)

    if request.method == 'POST':
        languages_known = request.form.get('languages_known', '').strip()
        area_of_interest = request.form.get('area_of_interest', '').strip()
        skills_input = request.form.get('skills', curr_user.get('skills') or '').strip()

        profile_dict = {
            'full_name': request.form.get('full_name', curr_user.get('full_name') or '').strip() or curr_user.get('full_name'),
            'phone': request.form.get('phone', curr_user.get('phone') or '').strip(),
            'degree': request.form.get('degree', curr_user.get('degree') or '').strip(),
            'institution': request.form.get('institution', curr_user.get('institution') or '').strip(),
            'graduation_year': request.form.get('graduation_year', curr_user.get('graduation_year') or '').strip(),
            'skills': skills_input,
            'experience': request.form.get('experience', curr_user.get('experience') or '').strip(),
            'projects': request.form.get('projects', curr_user.get('projects') or '').strip(),
            'bio': request.form.get('bio', curr_user.get('bio') or '').strip(),
            'linkedin_url': curr_user.get('linkedin_url') or '',
            'github_url': curr_user.get('github_url') or '',
            'languages_known': languages_known,
            'area_of_interest': area_of_interest
        }
        db.update_user_profile(user_id, profile_dict)
        flash("Resume updated with your Languages Known and Area of Interest!", "success")
        return redirect(url_for('user.generate_resume'))

    user = db.get_user_by_id(user_id)
    latest_analysis = db.get_latest_analysis_for_user(user_id)
    skills = db.get_user_skills(user_id)

    # Collect candidate profile info
    skills_list = []
    if user.get('skills'):
        skills_list = [s.strip() for s in str(user['skills']).split(',') if s.strip()]
    elif skills:
        skills_list = [s['skill_name'] for s in skills]

    extracted_data = {}
    if latest_analysis and latest_analysis.get('extracted_json'):
        try:
            extracted_data = json.loads(latest_analysis['extracted_json'])
        except Exception:
            extracted_data = {}

    return render_template(
        'generated_resume.html',
        user=user,
        skills=skills_list,
        extracted=extracted_data,
        analysis=latest_analysis
    )
