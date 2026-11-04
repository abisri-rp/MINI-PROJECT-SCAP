"""
Resume Management, Parsing, Scoring, and Synthesis Routes.
Handles file uploads (PDF/DOCX), triggers the NLP extraction pipeline,
calculates advisory quality scores, predicts technical categories, and powers the Resume Synthesizer.
"""
import os
import json
from pathlib import Path
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
from config import Config
from database import db
from routes.auth import login_required
from services.resume_parser import parse_resume
from services.resume_scorer import score_resume
from services.skill_classifier import skill_classifier
from services.resume_rewriter import synthesize_resume_sections

resume_bp = Blueprint('resume', __name__, url_prefix='/resume')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@resume_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    user_id = session['user_id']
    if request.method == 'POST':
        if 'resume' not in request.files:
            flash("No file part selected.", "danger")
            return redirect(request.url)

        file = request.files['resume']
        if file.filename == '':
            flash("Please choose a PDF or DOCX resume to upload.", "danger")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("Invalid file format. Only PDF and DOCX files are allowed.", "danger")
            return redirect(request.url)

        # Secure filename and store uniquely
        original_name = secure_filename(file.filename)
        file_ext = original_name.rsplit('.', 1)[1].lower()
        
        # User-specific directory
        from pathlib import Path
        user_upload_dir = Path(Config.UPLOAD_FOLDER) / f"user_{user_id}"
        user_upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine version and save
        saved_name = f"resume_v_{original_name}"
        save_path = user_upload_dir / saved_name
        file.save(str(save_path))

        try:
            # 1. NLP Extraction Pipeline
            custom_skills = db.get_all_skills()
            parsed = parse_resume(save_path, custom_skills)
            
            # --- Strict Resume Format Validation Gate ---
            # If the uploaded file is not in resume format, do NOT calculate score,
            # do NOT predict or assign field/category, and do NOT perform any further operations.
            if not parsed.get("is_valid_resume") or parsed.get("error"):
                if save_path.exists():
                    try:
                        save_path.unlink()
                    except Exception:
                        pass
                
                flash(
                    "Upload rejected: The uploaded file is not in a valid resume format. "
                    "No quality score was given and no technical domain was predicted. "
                    "Please upload a standard resume (PDF or DOCX) containing your contact details, education, technical skills, and experience/projects.",
                    "danger"
                )
                return redirect(url_for('resume.upload'))

            raw_text = parsed.get("raw_text", "")

            # 2. Save Resume Record in Database
            resume_id, version_num = db.save_resume(
                user_id=user_id,
                filename=original_name,
                file_path=save_path,
                file_type=file_ext,
                raw_text=raw_text
            )

            # 3. ML Model 3: Technical Skill Categorization
            classification = skill_classifier.predict_category(
                raw_text, detected_skills=parsed.get("technical_skills", [])
            )
            predicted_cat = classification.get("primary_category", "Software and Web Development")
            confidence = classification.get("confidence", 0.0)

            # 4. ML Model 2: Resume Quality Scoring
            score_data = score_resume(parsed, target_role=predicted_cat)

            # 5. Persist Analysis in Database
            analysis_id = db.save_resume_analysis(
                resume_id=resume_id,
                user_id=user_id,
                extracted_dict=parsed,
                scores_dict=score_data,
                category=predicted_cat,
                confidence=confidence,
                feedback_dict=score_data
            )

            # 6. Save detected skills into USER_SKILL
            db.save_user_skills(
                user_id=user_id,
                resume_id=resume_id,
                skills_list=parsed.get("technical_skills", [])
            )

            # 7. Generate Initial Resume Synthesizer Suggestions
            combined_desc = (parsed.get("projects", "") + "\n" + parsed.get("experience", "")).strip()
            if not combined_desc:
                combined_desc = raw_text

            suggestions = synthesize_resume_sections(combined_desc)
            for s in suggestions:
                db.save_suggestion(
                    resume_id=resume_id,
                    original=s["original"],
                    suggested=s["suggested"],
                    verb=s["action_verb"],
                    explanation=s["explanation"]
                )

            flash(f"Resume uploaded and analyzed successfully! (Version {version_num})", "success")
            return redirect(url_for('resume.analysis', resume_id=resume_id))

        except Exception as e:
            flash(f"An error occurred while analyzing the resume: {str(e)}", "danger")
            return redirect(request.url)

    # GET request
    latest_resume = db.get_latest_resume_for_user(user_id)
    return render_template('upload_resume.html', latest_resume=latest_resume)

@resume_bp.route('/analysis')
@resume_bp.route('/analysis/<int:resume_id>')
@login_required
def analysis(resume_id=None):
    user_id = session['user_id']
    if resume_id:
        resume = db.get_resume_by_id(resume_id)
    else:
        resume = db.get_latest_resume_for_user(user_id)

    if not resume or resume['user_id'] != user_id:
        flash("No analyzed resume found. Please upload a resume first.", "info")
        return redirect(url_for('resume.upload'))

    analysis_record = db.get_analysis_by_resume_id(resume['resume_id'])
    if not analysis_record:
        flash("Analysis not completed for this resume.", "warning")
        return redirect(url_for('resume.upload'))

    review = db.execute_query(
        "SELECT * FROM ADMIN_REVIEW WHERE analysis_id = :1",
        (analysis_record['analysis_id'],), fetchone=True
    )

    extracted_data = json.loads(analysis_record.get('extracted_json') or '{}')
    feedback_data = json.loads(analysis_record.get('feedback_json') or '{}')
    all_resumes = db.get_all_resumes_for_user(user_id)

    # Re-verify document validity so non-resume content files never show quality scores or domains
    file_path = resume.get('file_path')
    if file_path and os.path.exists(str(file_path)):
        if extracted_data.get('is_valid_resume') is not False:
            custom_skills = db.get_all_skills()
            current_parsed = parse_resume(file_path, custom_skills)
            if not current_parsed.get('is_valid_resume') or current_parsed.get('error'):
                extracted_data['is_valid_resume'] = False
                extracted_data['error'] = current_parsed.get('error')
                analysis_record['total_score'] = 0
                analysis_record['completeness_score'] = 0
                analysis_record['skills_score'] = 0
                analysis_record['projects_score'] = 0
                analysis_record['verbs_score'] = 0
                analysis_record['readability_score'] = 0
                analysis_record['predicted_category'] = 'Not a Resume'
                analysis_record['confidence_score'] = 0
                try:
                    db.execute_query(
                        """UPDATE RESUME_ANALYSIS 
                           SET total_score = 0, completeness_score = 0, skills_score = 0,
                               projects_score = 0, verbs_score = 0, readability_score = 0,
                               predicted_category = 'Not a Resume', confidence_score = 0,
                               extracted_json = :1
                           WHERE analysis_id = :2""",
                        (json.dumps(extracted_data), analysis_record['analysis_id']),
                        commit=True
                    )
                except Exception:
                    pass

    return render_template(
        'resume_analysis.html',
        resume=resume,
        analysis=analysis_record,
        review=review,
        extracted=extracted_data,
        feedback=feedback_data,
        all_resumes=all_resumes
    )

@resume_bp.route('/analysis/<int:analysis_id>/update-profile', methods=['POST'])
@login_required
def update_extracted_profile(analysis_id):
    """Allows candidate to verify and correct extracted profile fields."""
    user_id = session['user_id']
    analysis_record = db.execute_query(
        "SELECT * FROM RESUME_ANALYSIS WHERE analysis_id = :1 AND user_id = :2",
        (analysis_id, user_id), fetchone=True
    )
    if not analysis_record:
        flash("Analysis record not found.", "danger")
        return redirect(url_for('user.dashboard'))

    extracted = json.loads(analysis_record.get('extracted_json') or '{}')
    
    # Update with verified inputs
    extracted['full_name'] = request.form.get('full_name', extracted.get('full_name', ''))
    extracted['email'] = request.form.get('email', extracted.get('email', ''))
    extracted['phone'] = request.form.get('phone', extracted.get('phone', ''))
    extracted['education'] = request.form.get('education', extracted.get('education', ''))
    extracted['experience'] = request.form.get('experience', extracted.get('experience', ''))
    extracted['projects'] = request.form.get('projects', extracted.get('projects', ''))

    # Technical skills comma-separated
    skills_input = request.form.get('technical_skills', '')
    if skills_input:
        new_skills = [s.strip() for s in skills_input.split(',') if s.strip()]
        extracted['technical_skills'] = new_skills
        db.save_user_skills(user_id, analysis_record['resume_id'], new_skills)

    # Recalculate advisory score with user-corrected data
    updated_scores = score_resume(extracted, target_role=analysis_record.get('predicted_category'))

    db.execute_query(
        """UPDATE RESUME_ANALYSIS 
           SET extracted_json = :1, total_score = :2, completeness_score = :3,
               skills_score = :4, projects_score = :5, verbs_score = :6,
               readability_score = :7, feedback_json = :8
           WHERE analysis_id = :9""",
        (json.dumps(extracted), updated_scores['total'], updated_scores['completeness'],
         updated_scores['skills'], updated_scores['projects'], updated_scores['action_verbs'],
         updated_scores['readability'], json.dumps(updated_scores), analysis_id),
        commit=True
    )

    flash("Profile information updated and resume score recalculated successfully!", "success")
    return redirect(url_for('resume.analysis', resume_id=analysis_record['resume_id']))

@resume_bp.route('/synthesizer')
@resume_bp.route('/synthesizer/<int:resume_id>')
@login_required
def synthesizer(resume_id=None):
    user_id = session['user_id']
    if resume_id:
        resume = db.get_resume_by_id(resume_id)
    else:
        resume = db.get_latest_resume_for_user(user_id)

    if not resume or resume['user_id'] != user_id:
        flash("Please upload a resume first to access the Resume Synthesizer.", "info")
        return redirect(url_for('resume.upload'))

    suggestions = db.get_suggestions_for_resume(resume['resume_id'])
    
    # If no suggestions exist yet, generate from raw text
    if not suggestions and resume.get('raw_text'):
        new_suggs = synthesize_resume_sections(resume['raw_text'])
        for s in new_suggs:
            db.save_suggestion(
                resume_id=resume['resume_id'],
                original=s["original"],
                suggested=s["suggested"],
                verb=s["action_verb"],
                explanation=s["explanation"]
            )
        suggestions = db.get_suggestions_for_resume(resume['resume_id'])

    return render_template(
        'resume_synthesizer.html',
        resume=resume,
        suggestions=suggestions
    )

@resume_bp.route('/synthesizer/action', methods=['POST'])
@login_required
def synthesizer_action():
    """Accepts, rejects, or edits a synthesized bullet point suggestion."""
    user_id = session['user_id']
    suggestion_id = request.form.get('suggestion_id')
    action = request.form.get('action') # 'accept', 'reject', 'edit'
    user_final = request.form.get('user_final_text', '').strip()

    if not suggestion_id or action not in ['accept', 'reject', 'edit']:
        return jsonify({"success": False, "error": "Invalid action parameters"}), 400

    sugg = db.execute_query(
        """SELECT s.*, r.user_id FROM RESUME_SUGGESTION s
           JOIN RESUME r ON s.resume_id = r.resume_id
           WHERE s.suggestion_id = :1""",
        (suggestion_id,), fetchone=True
    )

    if not sugg or sugg['user_id'] != user_id:
        return jsonify({"success": False, "error": "Suggestion not found or unauthorized"}), 403

    if action == 'accept':
        status = 'ACCEPTED'
        final_text = sugg['suggested_text']
    elif action == 'reject':
        status = 'REJECTED'
        final_text = sugg['original_text']
    else: # edit
        status = 'EDITED'
        final_text = user_final or sugg['suggested_text']

    db.update_suggestion_status(suggestion_id, status, final_text)

    # Return JSON for AJAX or redirect
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"success": True, "status": status, "final_text": final_text})

    flash(f"Suggestion {status.lower()} successfully.", "success")
    return redirect(url_for('resume.synthesizer', resume_id=sugg['resume_id']))

@resume_bp.route('/skill-category')
@login_required
def skill_category():
    user_id = session['user_id']
    latest_resume = db.get_latest_resume_for_user(user_id)
    latest_analysis = db.get_latest_analysis_for_user(user_id)
    categories = db.get_skill_categories()
    user_skills = db.get_user_skills(user_id)

    predicted_cat = latest_analysis.get('predicted_category') if latest_analysis else "Software and Web Development"
    confidence = latest_analysis.get('confidence_score') if latest_analysis else 0.85

    return render_template(
        'skill_category.html',
        latest_resume=latest_resume,
        latest_analysis=latest_analysis,
        categories=categories,
        predicted_cat=predicted_cat,
        confidence=confidence,
        user_skills=user_skills
    )
