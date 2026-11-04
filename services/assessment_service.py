"""
Assessment Service.
Handles Technical Mock Interview generation, MCQ and descriptive rubric-based evaluation,
and Aptitude Test timed assessments, topic scoring, and feedback generation.
"""
import re
from database import db

class AssessmentService:
    @staticmethod
    def get_interview_questions_for_user(category_name, difficulty="Intermediate", count=10):
        """Fetches curated questions matching the candidate's predicted or chosen category."""
        questions = db.get_technical_questions(category_name, difficulty, limit=count)
        if not questions:
            # Fallback to general software engineering questions
            questions = db.get_technical_questions("Software and Web Development", difficulty, limit=count)
        return questions

    @staticmethod
    def evaluate_interview_response(question, user_answer):
        """
        Evaluates user answers:
        - For MCQ: exact option match (A/B/C/D)
        - For Descriptive: transparent rubric-based keyword and conceptual density matching.
        """
        q_type = question.get("question_type", "MCQ")
        correct_ans = question.get("correct_answer", "").strip()

        if q_type == "MCQ":
            is_correct = user_answer.strip().upper() == correct_ans.upper()
            points = 10.0 if is_correct else 0.0
            feedback = (
                "Correct! " + (question.get("explanation") or "")
                if is_correct else
                f"Incorrect. The correct option is ({correct_ans}). " + (question.get("explanation") or "")
            )
            return is_correct, points, feedback

        else:
            # Descriptive answer rubric evaluation
            rubric_raw = question.get("rubric_keywords", "")
            keywords = [k.strip().lower() for k in rubric_raw.split(',') if k.strip()]
            user_text_lower = user_answer.lower().strip()

            if not user_text_lower:
                return False, 0.0, "No answer provided. Expected explanation referencing core architectural principles."

            # Count keyword hits
            hits = [kw for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', user_text_lower)]
            hit_ratio = len(hits) / max(len(keywords), 1)
            word_count = len(user_text_lower.split())

            # Transparent Rubric Scoring (0 - 10 points)
            # 60% based on keyword coverage, 40% based on elaboration length (min 20 words for full elaboration score)
            kw_points = min(6.0, hit_ratio * 7.5)
            length_points = min(4.0, (word_count / 25.0) * 4.0)
            total_points = round(kw_points + length_points, 1)

            is_acceptable = total_points >= 5.0
            matched_str = ", ".join(hits) if hits else "None"
            missing_str = ", ".join([k for k in keywords if k not in hits][:4])

            feedback = (
                f"Score: {total_points}/10. Identified key concepts: [{matched_str}]. "
                + (f"Consider elaborating on: [{missing_str}]. " if missing_str else "")
                + f"Ideal reference explanation: {question.get('explanation')}"
            )
            return is_acceptable, total_points, feedback

    @staticmethod
    def get_aptitude_test_questions(limit=15):
        """Retrieves questions across Quantitative, Logical, and Verbal sections."""
        return db.get_aptitude_questions(limit=limit)

    @staticmethod
    def evaluate_aptitude_submission(user_id, responses_dict):
        """
        Evaluates full aptitude test submission across topics.
        Calculates sectional scores (Quantitative, Logical, Verbal) and stores results.
        """
        total_questions = len(responses_dict)
        if total_questions == 0:
            return None

        correct_count = 0
        section_stats = {
            "Quantitative": {"total": 0, "correct": 0},
            "Logical": {"total": 0, "correct": 0},
            "Verbal": {"total": 0, "correct": 0}
        }
        detailed_results = []

        for q_id_str, selected_opt in responses_dict.items():
            try:
                q_id = int(q_id_str)
            except ValueError:
                continue

            q = db.get_question_by_id(q_id)
            if not q:
                continue

            section = q.get("aptitude_section", "General")
            if section not in section_stats:
                section_stats[section] = {"total": 0, "correct": 0}

            section_stats[section]["total"] += 1
            is_correct = (selected_opt.strip().upper() == q.get("correct_answer", "").strip().upper())
            
            if is_correct:
                correct_count += 1
                section_stats[section]["correct"] += 1

            detailed_results.append({
                "question": q,
                "selected_option": selected_opt.strip().upper(),
                "correct_option": q.get("correct_answer"),
                "is_correct": is_correct,
                "explanation": q.get("explanation")
            })

        # Calculate percentages
        overall_pct = round((correct_count / total_questions) * 100, 1) if total_questions > 0 else 0
        
        def calc_sec_pct(sec_name):
            tot = section_stats.get(sec_name, {}).get("total", 0)
            corr = section_stats.get(sec_name, {}).get("correct", 0)
            return round((corr / tot) * 100, 1) if tot > 0 else 0.0

        quant_pct = calc_sec_pct("Quantitative")
        logical_pct = calc_sec_pct("Logical")
        verbal_pct = calc_sec_pct("Verbal")

        # Save to database
        attempt_id = db.create_aptitude_attempt(
            user_id=user_id,
            total=total_questions,
            correct=correct_count,
            score_pct=overall_pct,
            quant=quant_pct,
            logical=logical_pct,
            verbal=verbal_pct
        )

        for res in detailed_results:
            db.save_aptitude_response(
                attempt_id=attempt_id,
                question_id=res["question"]["question_id"],
                option=res["selected_option"],
                is_correct=1 if res["is_correct"] else 0,
                points=1.0 if res["is_correct"] else 0.0
            )

        # Identify weak areas (sections below 60%)
        weak_sections = []
        if quant_pct < 60:
            weak_sections.append("Quantitative Aptitude")
        if logical_pct < 60:
            weak_sections.append("Logical Reasoning")
        if verbal_pct < 60:
            weak_sections.append("Verbal Ability")

        return {
            "attempt_id": attempt_id,
            "total_questions": total_questions,
            "correct_count": correct_count,
            "overall_score": overall_pct,
            "quant_score": quant_pct,
            "logical_score": logical_pct,
            "verbal_score": verbal_pct,
            "weak_sections": weak_sections,
            "detailed_results": detailed_results
        }
