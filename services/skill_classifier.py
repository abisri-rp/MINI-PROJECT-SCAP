"""
Technical Skill Categorization Service (ML Model 3).
Loads trained TF-IDF vectorizer and Logistic Regression classifier.
Provides predictions with confidence estimates, secondary domains, and uncertainty handling.
"""
import os
import joblib
import logging
from pathlib import Path
from config import Config

logger = logging.getLogger(__name__)

VECTORIZER_PATH = Config.ML_MODEL_DIR / "tfidf_vectorizer.joblib"
CLASSIFIER_PATH = Config.ML_MODEL_DIR / "skill_classifier.joblib"

class SkillClassifierService:
    def __init__(self):
        self.vectorizer = None
        self.classifier = None
        self.is_loaded = False
        self._load_models()

    def _load_models(self):
        try:
            if VECTORIZER_PATH.exists() and CLASSIFIER_PATH.exists():
                self.vectorizer = joblib.load(VECTORIZER_PATH)
                self.classifier = joblib.load(CLASSIFIER_PATH)
                self.is_loaded = True
                logger.info("ML Skill Classifier and TF-IDF Vectorizer loaded successfully.")
            else:
                logger.warning(f"ML Model artifacts not found in {Config.ML_MODEL_DIR}. Model will attempt auto-training.")
                from ml.train_classifier import train
                train()
                if VECTORIZER_PATH.exists() and CLASSIFIER_PATH.exists():
                    self.vectorizer = joblib.load(VECTORIZER_PATH)
                    self.classifier = joblib.load(CLASSIFIER_PATH)
                    self.is_loaded = True
        except Exception as e:
            logger.error(f"Failed to load or train skill classifier: {e}")
            self.is_loaded = False

    def predict_category(self, resume_text, detected_skills=None, is_valid_resume=True):
        """
        Predicts technical category with calibrated probabilities.
        Suspends prediction if the document is not in valid resume format.
        """
        if not is_valid_resume:
            return {
                "primary_category": "Not Classified (Not a Resume)",
                "confidence": 0.0,
                "confidence_percentage": 0.0,
                "secondary_categories": [],
                "is_uncertain": True,
                "message": "The uploaded file is not in a valid resume format. Technical domain prediction is disabled.",
                "supporting_skills": []
            }

        if not self.is_loaded or not self.vectorizer or not self.classifier:
            return {
                "primary_category": "Software and Web Development",
                "confidence": 0.50,
                "secondary_categories": [],
                "is_uncertain": True,
                "message": "Classification model is currently offline. You may manually select your target category.",
                "supporting_skills": detected_skills or []
            }

        if not resume_text or len(resume_text.strip()) < 20:
            return {
                "primary_category": "Software and Web Development",
                "confidence": 0.30,
                "secondary_categories": [],
                "is_uncertain": True,
                "message": "Insufficient text provided to confidently predict a technical domain.",
                "supporting_skills": []
            }

        try:
            vec = self.vectorizer.transform([resume_text])
            probabilities = self.classifier.predict_proba(vec)[0]
            classes = self.classifier.classes_

            # Sort categories by probability
            ranked = sorted(zip(classes, probabilities), key=lambda x: x[1], reverse=True)
            primary_cat, top_prob = ranked[0]
            
            # Secondary categories with meaningful probabilities (> 10%)
            secondary = [
                {"category": cat, "probability": round(float(prob) * 100, 1)}
                for cat, prob in ranked[1:3] if prob >= 0.10
            ]

            # Uncertainty check: if top probability is below 35%
            is_uncertain = top_prob < 0.35

            # Find which detected skills correlate with the primary category
            supporting = []
            if detected_skills:
                supporting = detected_skills[:6]

            return {
                "primary_category": primary_cat,
                "confidence": round(float(top_prob), 4),
                "confidence_percentage": round(float(top_prob) * 100, 1),
                "secondary_categories": secondary,
                "is_uncertain": is_uncertain,
                "message": "Category prediction uncertain. Consider manual verification." if is_uncertain else "Category predicted with strong statistical confidence.",
                "supporting_skills": supporting
            }
        except Exception as e:
            logger.error(f"Prediction exception: {e}")
            return {
                "primary_category": "Software and Web Development",
                "confidence": 0.40,
                "secondary_categories": [],
                "is_uncertain": True,
                "message": f"Prediction error: {str(e)}",
                "supporting_skills": detected_skills or []
            }

skill_classifier = SkillClassifierService()
