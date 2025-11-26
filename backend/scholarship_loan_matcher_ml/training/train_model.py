"""Baseline TF-IDF training pipeline for scholarship & loan matching."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import List

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from scholarship_loan_matcher_ml.preprocessing.clean_data import preprocess_data

ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"
PROCESSED_DATA_PATH = ARTIFACT_DIR / "processed_dataset.json"
VECTORIZER_PATH = ARTIFACT_DIR / "tfidf_vectorizer.joblib"
MODEL_PATH = ARTIFACT_DIR / "knn_similarity_model.joblib"
METADATA_PATH = ARTIFACT_DIR / "metadata.json"

TEXT_FIELDS = [
    "name",
    "description",
    "eligibility",
    "program_type",
    "loan_type",
    "region",
    "special_benefits",
]


def _ensure_artifact_dir() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


def _build_corpus(df: pd.DataFrame, fields: List[str]) -> pd.Series:
    """Combine relevant text columns into a single lowercase corpus."""
    safe_df = df.copy()
    for field in fields:
        if field not in safe_df.columns:
            safe_df[field] = ""
    corpus = (
        safe_df[fields]
        .fillna("")
        .agg(lambda row: " ".join(part for part in row if part), axis=1)
        .str.lower()
    )
    return corpus


def _train_vectorizer(corpus: pd.Series, max_features: int) -> TfidfVectorizer:
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=(1, 2),
        min_df=1,
        strip_accents="unicode",
    )
    vectorizer.fit(corpus)
    return vectorizer


def _fit_similarity_model(embeddings) -> NearestNeighbors:
    model = NearestNeighbors(metric="cosine", algorithm="brute")
    model.fit(embeddings)
    return model


def train_model(data_dir: Path, max_features: int = 8000) -> None:
    """Run preprocessing, build embeddings, and persist artifacts."""
    _ensure_artifact_dir()
    processed_df = preprocess_data(data_dir=data_dir)
    processed_df["text_corpus"] = _build_corpus(processed_df, TEXT_FIELDS)

    vectorizer = _train_vectorizer(processed_df["text_corpus"], max_features)
    embeddings = vectorizer.transform(processed_df["text_corpus"])
    similarity_model = _fit_similarity_model(embeddings)

    processed_df.to_json(
        PROCESSED_DATA_PATH,
        orient="records",
        force_ascii=False,
        indent=2,
    )
    joblib.dump(vectorizer, VECTORIZER_PATH)
    joblib.dump(similarity_model, MODEL_PATH)
    metadata = {
        "record_count": int(len(processed_df)),
        "text_fields": TEXT_FIELDS,
        "vectorizer_path": str(VECTORIZER_PATH),
        "model_path": str(MODEL_PATH),
        "processed_dataset_path": str(PROCESSED_DATA_PATH),
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2))
    print(f"Artifacts saved to {ARTIFACT_DIR}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train baseline matcher model.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Directory containing scholarships.csv and loans.csv (defaults to backend/data).",
    )
    parser.add_argument(
        "--max-features",
        type=int,
        default=8000,
        help="Maximum vocabulary size for TF-IDF.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_dir = args.data_dir or Path(__file__).resolve().parents[2] / "data"
    train_model(data_dir=data_dir, max_features=args.max_features)


if __name__ == "__main__":
    main()

