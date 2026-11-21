"""
Trains a TF-IDF + Logistic Regression baseline classifier and saves it to
ai_engine/trained_model.joblib, where classifier.py will automatically pick
it up in place of the heuristic fallback.

Usage:
    python ai_engine/train_baseline.py path/to/dataset.csv

The CSV must have at least two columns: `text` and `label`, where label is
one of: real, fake  (e.g. the Kaggle "Fake and Real News" dataset, or LIAR
dataset reshaped to two columns).

Example (from backend/ directory):
    python ai_engine/train_baseline.py data/news_dataset.csv
"""
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


def main(csv_path: str):
    df = pd.read_csv(csv_path)
    if "text" not in df.columns or "label" not in df.columns:
        raise SystemExit("CSV must contain 'text' and 'label' columns.")

    df = df.dropna(subset=["text", "label"])
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=0.2, random_state=42, stratify=df["label"]
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=20000, ngram_range=(1, 2), stop_words="english")),
        ("clf", LogisticRegression(max_iter=1000)),
    ])

    pipeline.fit(X_train, y_train)

    preds = pipeline.predict(X_test)
    print(classification_report(y_test, preds))

    out_path = Path(__file__).resolve().parent / "trained_model.joblib"
    joblib.dump(pipeline, out_path)
    print(f"Saved trained model to {out_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python train_baseline.py <path_to_csv>")
    main(sys.argv[1])
