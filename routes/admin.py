import os
import json
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_from_directory, jsonify
from database import db
from routes.auth import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    kpis = db.get_admin_kpis()
    recent_reviews = db.list_all_reviews()[:8]
    return render_template(
        'admin_dashboard.html',
        kpis=kpis,
        recent_reviews=recent_reviews
    )

@admin_bp.route('/users')
@admin_required
def users():
    users_list = db.list_all_users()
    return render_template('admin_users.html', users=users_list)

@admin_bp.route('/reviews')
@admin_required
def reviews():
    all_reviews = db.list_all_reviews()
    return render_template('admin_reviews_list.html', reviews=all_reviews)

@admin_bp.route('/view_resume/<int:resume_id>')
@admin_required
def view_resume(resume_id):
    resume = db.get_resume_by_id(resume_id)
    if not resume or not resume.get('file_path'):
        flash("Resume record not found.", "danger")
        return redirect(url_for('admin.reviews'))

    file_path = resume['file_path']
    if not os.path.exists(file_path):
        flash("Resume file does not exist on disk.", "warning")
        return redirect(url_for('admin.reviews'))

    directory = os.path.dirname(os.path.abspath(file_path))
    filename = os.path.basename(file_path)
    return send_from_directory(directory, filename)

@admin_bp.route('/review/<int:review_id>', methods=['GET', 'POST'])
@admin_required
def review_resume(review_id):
    review = db.get_review_by_id(review_id)
    if not review:
        flash("Review record not found.", "danger")
        return redirect(url_for('admin.dashboard'))

    categories = db.get_skill_categories()
    user_id = review['user_id']
    all_resumes = db.get_all_resumes_for_user(user_id)

    extracted_data = json.loads(review.get('extracted_json') or '{}')
    feedback_data = json.loads(review.get('feedback_json') or '{}')
    corrected_data = json.loads(review.get('corrected_data_json') or '{}')

    if request.method == 'POST':
        action_status = request.form.get('review_status', 'Pending Review')
        admin_comments = request.form.get('admin_comments', '').strip()
        verified_cat = request.form.get('verified_category', review.get('predicted_category'))

        # Validation: Admin must write a suggestion before review can be submitted and sent
        if not admin_comments:
            flash("Admin suggestion/feedback is required before you can send the review and notify the candidate.", "danger")
            return redirect(url_for('admin.review_resume', review_id=review_id))

        # Corrections submitted by admin
        correction_dict = {
            "full_name": request.form.get('corr_full_name', extracted_data.get('full_name')),
            "email": request.form.get('corr_email', extracted_data.get('email')),
            "education": request.form.get('corr_education', extracted_data.get('education')),
            "verified_skills": request.form.get('corr_skills', ", ".join(extracted_data.get('technical_skills', [])))
        }

        admin_id = session.get('user_id')

        db.submit_admin_review(
            review_id=review_id,
            admin_id=admin_id,
            status=action_status,
            comments=admin_comments,
            verified_cat=verified_cat,
            corrected_json=json.dumps(correction_dict)
        )

        flash(f"Resume review updated to status: '{action_status}'. Feedback notification sent to candidate.", "success")
        return redirect(url_for('admin.review_resume', review_id=review_id))

    return render_template(
        'admin_review.html',
        review=review,
        categories=categories,
        extracted=extracted_data,
        feedback=feedback_data,
        corrected=corrected_data,
        all_resumes=all_resumes
    )

@admin_bp.route('/questions', methods=['GET', 'POST'])
@admin_required
def questions():
    categories = db.get_skill_categories()
    if request.method == 'POST':
        question_no = request.form.get('question_no', '').strip()
        q_type = request.form.get('question_type', 'DESCRIPTIVE')
        category_id = request.form.get('category_id') or None
        topic = request.form.get('topic', 'General').strip()
        difficulty = request.form.get('difficulty', 'Intermediate')
        question_text = request.form.get('question_text', '').strip()
        
        try:
            mark_allocation = int(request.form.get('mark_allocation', 5))
        except (ValueError, TypeError):
            mark_allocation = 5

        option_a = request.form.get('option_a', '').strip() or None
        option_b = request.form.get('option_b', '').strip() or None
        option_c = request.form.get('option_c', '').strip() or None
        option_d = request.form.get('option_d', '').strip() or None
        correct_answer = request.form.get('correct_answer', '').strip()
        explanation = request.form.get('explanation', '').strip()
        rubric_keywords = request.form.get('rubric_keywords', '').strip()
        aptitude_section = request.form.get('aptitude_section') or None

        if not question_text:
            flash("Question text is required.", "danger")
            return redirect(url_for('admin.questions'))

        if not correct_answer:
            flash("Correct answer or grading solution is required.", "danger")
            return redirect(url_for('admin.questions'))

        db.add_question({
            'question_no': question_no,
            'question_type': q_type,
            'category_id': category_id,
            'topic': topic,
            'difficulty': difficulty,
            'question_text': question_text,
            'mark_allocation': mark_allocation,
            'option_a': option_a,
            'option_b': option_b,
            'option_c': option_c,
            'option_d': option_d,
            'correct_answer': correct_answer,
            'explanation': explanation,
            'rubric_keywords': rubric_keywords,
            'aptitude_section': aptitude_section
        })

        flash(f"Question #{question_no or ''} successfully uploaded to database with {mark_allocation} marks allocation!", "success")
        return redirect(url_for('admin.questions'))

    all_questions = db.list_all_questions(limit=250)
    return render_template('admin_questions.html', questions=all_questions, categories=categories)

@admin_bp.route('/questions/delete/<int:question_id>', methods=['POST'])
@admin_required
def delete_question(question_id):
    db.delete_question(question_id)
    flash("Question successfully removed from Question Bank.", "info")
    return redirect(url_for('admin.questions'))

@admin_bp.route('/field_of_study')
@admin_required
def field_of_study():
    data = db.get_users_by_field_of_study()
    selected_skill = request.args.get('skill', '')
    return render_template(
        'admin_field_of_study.html',
        skill_groups=data['skills'],
        category_groups=data['categories'],
        total_candidates=data['total_candidates'],
        selected_skill=selected_skill
    )

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    current_admin_id = session.get('user_id')
    if user_id == current_admin_id:
        flash("You cannot delete your own active admin account.", "warning")
        return redirect(url_for('admin.users'))

    target_user = db.get_user_by_id(user_id)
    if not target_user:
        flash("User record not found or already deleted.", "danger")
        return redirect(url_for('admin.users'))

    user_name = target_user.get('full_name') or target_user.get('email')
    success = db.delete_user(user_id)
    if success:
        flash(f"User '{user_name}' and all associated records have been successfully deleted.", "success")
    else:
        flash(f"An error occurred while attempting to delete user '{user_name}'.", "danger")

    referrer = request.referrer or ''
    if 'field_of_study' in referrer:
        return redirect(url_for('admin.field_of_study'))
    return redirect(url_for('admin.users'))
