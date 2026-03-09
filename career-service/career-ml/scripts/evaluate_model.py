#!/usr/bin/env python3
import json
import logging
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedShuffleSplit
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s")
log = logging.getLogger(__name__)

# Paths
ROOT = Path(__file__).resolve().parent.parent.parent
DATA_CSV = ROOT / "career-ml" / "data" / "processed" / "job_skill_vectors_v3.csv"
if not DATA_CSV.exists():
    DATA_CSV = ROOT / "career-ml" / "data" / "processed" / "job_skill_vectors_v2_fixed.csv"
MODEL_PATH = ROOT / "career-ml" / "models" / "role_classifier_v2.pkl"
COLUMNS_PATH = ROOT / "career-ml" / "models" / "skill_columns_v2.pkl"

OUT_DIR = ROOT / "evaluation_results"
OUT_DIR.mkdir(exist_ok=True, parents=True)
OUT_METRICS_JSON = OUT_DIR / "metrics.json"
OUT_METRICS_CSV = OUT_DIR / "metrics.csv"
OUT_CONFUSION = OUT_DIR / "confusion_matrix.png"

import sys
sys.path.insert(0, str(ROOT / "career-ml" / "scripts"))
from train_decision_tree_v2 import stratified_split

def load_data():
    df = pd.read_csv(DATA_CSV)
    skill_cols = joblib.load(COLUMNS_PATH)
    X = df[skill_cols].values.astype(np.float32)
    y = df["role_id"].values
    return X, y, skill_cols

from sklearn.model_selection import train_test_split

def get_test_split(X, y):
    # Use a larger test split if we have more data now
    log.info(f"Splitting dataset of {len(y)} samples...")
    # Try stratified if possible, fall back to random
    try:
        _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        log.info("Status: Successful stratified split.")
    except Exception:
        log.warning("Status: Stratification failed, using random split.")
        _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_test, y_test

def save_confusion_matrix(cm, class_names, path):
    fig_size = max(8, len(class_names) * 0.4)
    fig, ax = plt.subplots(figsize=(fig_size, fig_size))
    sns.heatmap(
        cm, annot=False, cmap="Blues",
        xticklabels=class_names, yticklabels=class_names,
        ax=ax, linewidths=0.5,
    )
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title("Confusion Matrix - Offline Evaluation")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    log.info(f"Saved confusion matrix -> {path}")

def evaluate():
    if not MODEL_PATH.exists():
        log.error(f"Model not found at {MODEL_PATH}")
        return
        
    log.info("Loading model and data...")
    model = joblib.load(MODEL_PATH)
    X, y, skill_cols = load_data()
    
    # Filter to only include roles the model was trained on (known classes)
    known_classes = set(model.classes_)
    log.info(f"Model knows {len(known_classes)} classes (Entry-level specialisation)")
    
    mask = np.isin(y, list(known_classes))
    X_filtered = X[mask]
    y_filtered = y[mask]
    
    log.info(f"Samples after filtering for known classes: {len(y_filtered)} (from {len(y)})")
    
    X_test, y_test = get_test_split(X_filtered, y_filtered)
    class_names = [str(c) for c in model.classes_]
    
    log.info("Running inference...")
    y_pred = model.predict(X_test)
    
    # Debug table
    log.info("\nDEBUG LABELS (True vs Predicted):")
    for i in range(min(20, len(y_test))):
        log.info(f"  {i:2d}: True={y_test[i]:<25} Pred={y_pred[i]:<25} Match={y_test[i]==y_pred[i]}")
    
    # Ensure both are strings and stripped
    y_test = np.array([str(s).strip() for s in y_test])
    y_pred = np.array([str(s).strip() for s in y_pred])
    
    acc = accuracy_score(y_test, y_pred)
    f1_w = f1_score(y_test, y_pred, average="weighted", zero_division=0)
    prec_w = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    rec_w = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    cm = confusion_matrix(y_test, y_pred, labels=class_names)
    
    # Diagnostics - show some hits
    matches = (y_test == y_pred)
    log.info(f"Verified {matches.sum()} correct predictions in test set")
    
    report_dict = classification_report(y_test, y_pred, labels=class_names, target_names=class_names, zero_division=0, output_dict=True)
    
    metrics = {
        "model_type": "Entry-level Role Classifier",
        "accuracy": float(acc),
        "precision_weighted": float(prec_w),
        "recall_weighted": float(rec_w),
        "f1_weighted": float(f1_w),
        "test_samples": int(len(y_test)),
        "total_classes": int(len(class_names))
    }
    
    with open(OUT_METRICS_JSON, "w") as f:
        json.dump(metrics, f, indent=4)
    log.info(f"Saved metrics -> {OUT_METRICS_JSON}")
    
    df_metrics = pd.DataFrame(report_dict).transpose()
    df_metrics.to_csv(OUT_METRICS_CSV)
    log.info(f"Saved detailed metrics CSV -> {OUT_METRICS_CSV}")
    
    # Save Confusion Matrix
    save_confusion_matrix(cm, class_names, OUT_CONFUSION)
    
    log.info("Evaluation Complete.")
    log.info(f"Accuracy: {acc:.4f} | F1: {f1_w:.4f}")

if __name__ == "__main__":
    evaluate()
