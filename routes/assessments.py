"""
Assessment and Progress Routes.
Manages technical mock interviews, descriptive rubric evaluations,
aptitude assessments, and closed-loop progress visualization.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database import db
from routes.auth import login_required
from services.assessment_service import AssessmentService

assessments_bp = Blueprint('assessments', __name__, url_prefix='/assessments')

@assessments_bp.route('/interview', methods=['GET', 'POST'])
@login_required
def interview():
    user_id = session['user_id']
    latest_analysis = db.get_latest_analysis_for_user(user_id)
    default_cat = latest_analysis.get('predicted_category') if latest_analysis else "Software and Web Development"

    if request.method == 'POST':
        # Grade interview submission
        q_count = int(request.form.get('total_questions', 0))
        cat_id = request.form.get('category_id') or 1
        difficulty = request.form.get('difficulty', 'Intermediate')

        total_earned = 0.0
        max_possible = q_count * 10.0
        graded_responses = []

        for i in range(q_count):
            q_id = request.form.get(f'question_id_{i}')
            if not q_id:
                continue

            q = db.get_question_by_id(int(q_id))
            if not q:
                continue

            user_ans = request.form.get(f'answer_{i}', '').strip()
            is_correct, points, feedback = AssessmentService.evaluate_interview_response(q, user_ans)
            total_earned += points

            graded_responses.append({
                "question": q,
                "user_answer": user_ans,
                "is_correct": is_correct,
                "points": points,
                "feedback": feedback
            })

        score_pct = round((total_earned / max(max_possible, 1.0)) * 100, 1)

        # Store in database
        interview_id = db.create_mock_interview(
            user_id=user_id,
            category_id=cat_id,
            difficulty=difficulty,
            total_q=q_count,
            score_pct=score_pct
        )

        for g in graded_responses:
            db.save_interview_response(
                interview_id=interview_id,
                question_id=g["question"]["question_id"],
                user_ans=g["user_answer"],
                is_correct=1 if g["is_correct"] else 0,
                points=g["points"],
                feedback=g["feedback"]
            )

        flash(f"Mock Interview submitted! Your performance score: {score_pct}%", "success")
        return render_template(
            'interview_result.html',
            score_pct=score_pct,
            difficulty=difficulty,
            graded_responses=graded_responses,
            category_name=default_cat
        )

    # GET request - load interview questions
    selected_difficulty = request.args.get('difficulty', 'Intermediate')
    selected_category = request.args.get('category', default_cat)
    try:
        selected_count = int(request.args.get('count', 10))
    except (ValueError, TypeError):
        selected_count = 10
    categories = db.get_skill_categories()

    questions = AssessmentService.get_interview_questions_for_user(
        category_name=selected_category,
        difficulty=selected_difficulty,
        count=selected_count
    )

    return render_template(
        'technical_interview.html',
        questions=questions,
        categories=categories,
        selected_category=selected_category,
        selected_difficulty=selected_difficulty,
        selected_count=selected_count
    )

@assessments_bp.route('/aptitude', methods=['GET', 'POST'])
@login_required
def aptitude():
    user_id = session['user_id']
    if request.method == 'POST':
        # Collect answers: {q_id: selected_option}
        responses = {}
        for key, val in request.form.items():
            if key.startswith('q_'):
                q_id = key.replace('q_', '')
                responses[q_id] = val

        eval_result = AssessmentService.evaluate_aptitude_submission(user_id, responses)
        if not eval_result:
            flash("No responses received. Please answer the assessment questions.", "warning")
            return redirect(url_for('assessments.aptitude'))

        return render_template('aptitude_result.html', result=eval_result)

    # GET request: load aptitude questions
    try:
        selected_count = int(request.args.get('count', 15))
    except (ValueError, TypeError):
        selected_count = 15
    questions = AssessmentService.get_aptitude_test_questions(limit=selected_count)
    return render_template('aptitude_test.html', questions=questions, selected_count=selected_count)

@assessments_bp.route('/history')
@login_required
def history():
    user_id = session['user_id']
    interviews = db.get_user_interviews(user_id)
    aptitudes = db.get_user_aptitude_attempts(user_id)
    return render_template('assessment_history.html', interviews=interviews, aptitudes=aptitudes)

@assessments_bp.route('/progress')
@login_required
def progress():
    user_id = session['user_id']
    timeline = db.get_user_progress_timeline(user_id)
    latest_analysis = db.get_latest_analysis_for_user(user_id)
    target_category = latest_analysis.get('predicted_category') if latest_analysis else None
    
    # Identify weak areas from latest aptitude attempt
    weak_topics = []
    if timeline["aptitudes"]:
        latest_apt = timeline["aptitudes"][0]
        if latest_apt.get("quant_score", 100) < 60:
            weak_topics.append("Quantitative")
        if latest_apt.get("logical_score", 100) < 60:
            weak_topics.append("Logical")
        if latest_apt.get("verbal_score", 100) < 60:
            weak_topics.append("Verbal")

    resources = db.get_learning_resources(target_category, weak_topics)

    return render_template(
        'progress.html',
        timeline=timeline,
        target_category=target_category,
        weak_topics=weak_topics,
        resources=resources
    )
