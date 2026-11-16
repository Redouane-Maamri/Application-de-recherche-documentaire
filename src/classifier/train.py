from pathlib import Path
import json

import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, make_scorer
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline


ROOT = Path(__file__).resolve().parents[2]

DATASET_FILE = ROOT / "data/training/processed_documents.csv"
MODEL_DIR = ROOT / "models"

MODEL_FILE = MODEL_DIR / "document_classifier.joblib"
METRICS_FILE = MODEL_DIR / "classifier_metrics.json"


def main():
    print("Loading training dataset...")

    if not DATASET_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET_FILE}")

    df = pd.read_csv(DATASET_FILE)

    required_columns = {"filename", "category", "text"}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"Dataset must contain: {required_columns}")

    df = df.dropna(subset=["category", "text"])
    df["text"] = df["text"].astype(str)
    df["category"] = df["category"].astype(str)

    df = df[df["text"].str.strip().str.len() >= 100]

    X = df["text"]
    y = df["category"]

    distribution = y.value_counts().to_dict()

    print("\n===== DATASET =====")
    print("Documents:", len(df))
    print("Categories:", distribution)

    if len(distribution) < 2:
        raise ValueError("At least two categories are required.")

    minimum_class_count = min(distribution.values())

    if minimum_class_count < 2:
        raise ValueError(
            "Each category needs at least two documents "
            "for two-fold stratified cross-validation."
        )

    pipeline = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                lowercase=True,
                strip_accents="unicode",
                ngram_range=(1, 2),
                max_features=10000,
                sublinear_tf=True
            )
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                random_state=42
            )
        )
    ])

    print("\n===== CROSS-VALIDATION =====")

    cv = StratifiedKFold(
        n_splits=2,
        shuffle=True,
        random_state=42
    )

    scorer = make_scorer(f1_score, average="macro", zero_division=0)

    scores = cross_val_score(
        pipeline,
        X,
        y,
        cv=cv,
        scoring=scorer
    )

    print("Fold F1 macro scores:", scores.round(3).tolist())
    print("Mean F1 macro:", round(float(scores.mean()), 3))

    print("\n===== FINAL TRAINING =====")

    pipeline.fit(X, y)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_FILE)

    metrics = {
        "model": "TF-IDF + Logistic Regression",
        "documents": int(len(df)),
        "categories": distribution,
        "cross_validation": {
            "method": "StratifiedKFold",
            "folds": 2,
            "f1_macro_scores": [float(s) for s in scores],
            "mean_f1_macro": float(scores.mean())
        },
        "warning": (
            "Very small dataset. Results are preliminary and "
            "do not demonstrate reliable real-world performance."
        )
    }

    with METRICS_FILE.open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=4)

    print("\n===== TRAINING COMPLETED =====")
    print("Model saved:", MODEL_FILE)
    print("Metrics saved:", METRICS_FILE)


if __name__ == "__main__":
    main()
