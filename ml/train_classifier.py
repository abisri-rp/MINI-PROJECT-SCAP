"""
Model training script for Technical Skill Categorization.
Trains a TF-IDF + Logistic Regression classifier on labeled technical profiles with train/test split.
Evaluates accuracy, precision, recall, F1-score, and confusion matrix, then persists artifacts with joblib.
"""
import os
import json
import joblib
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix

ML_DIR = Path(__file__).resolve().parent
DATASET_FILE = ML_DIR / "dataset" / "resume_data.csv"
MODELS_DIR = ML_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

VECTORIZER_FILE = MODELS_DIR / "tfidf_vectorizer.joblib"
CLASSIFIER_FILE = MODELS_DIR / "skill_classifier.joblib"
METRICS_FILE = MODELS_DIR / "metrics.json"

def train():
    if not DATASET_FILE.exists():
        from prepare_dataset import generate_dataset
        df = generate_dataset()
    else:
        df = pd.read_csv(DATASET_FILE)

    print(f"[*] Loaded dataset with {len(df)} records across {df['category'].nunique()} categories.")
    
    X = df["text"]
    y = df["category"]

    # Stratified train/test split (80/20 or 75/25)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    print(f"[*] Training samples: {len(X_train)}, Testing samples: {len(X_test)}")

    # TF-IDF Feature Extraction with unigrams and bigrams
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=2500,
        sublinear_tf=True,
        stop_words="english"
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # Train Logistic Regression Classifier with balanced class weights
    classifier = LogisticRegression(
        C=2.0,
        max_iter=1000,
        random_state=42,
        class_weight="balanced"
    )
    classifier.fit(X_train_vec, y_train)

    # Predictions and Evaluation on Unseen Test Split
    y_pred = classifier.predict(X_test_vec)

    accuracy = float(accuracy_score(y_test, y_pred))
    precision = float(precision_score(y_test, y_pred, average="weighted", zero_division=0))
    recall = float(recall_score(y_test, y_pred, average="weighted", zero_division=0))
    f1 = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))

    classes = list(classifier.classes_)
    cm = confusion_matrix(y_test, y_pred, labels=classes).tolist()
    report = classification_report(y_test, y_pred, zero_division=0, output_dict=True)

    print("\n================ MODEL EVALUATION REPORT ================")
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1-Score:  {f1:.4f}")
    print("\nDetailed Per-Class Performance:")
    print(classification_report(y_test, y_pred, zero_division=0))

    # Save trained vectorizer and classifier using joblib
    joblib.dump(vectorizer, VECTORIZER_FILE)
    joblib.dump(classifier, CLASSIFIER_FILE)
    print(f"[SUCCESS] Persisted vectorizer to: {VECTORIZER_FILE}")
    print(f"[SUCCESS] Persisted classifier to: {CLASSIFIER_FILE}")

    # Save metrics JSON for inspection and dashboard display
    metrics = {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "classes": classes,
        "confusion_matrix": cm,
        "classification_report": report
    }
    with open(METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"[SUCCESS] Metrics saved to: {METRICS_FILE}")

    return metrics

if __name__ == "__main__":
    train()
