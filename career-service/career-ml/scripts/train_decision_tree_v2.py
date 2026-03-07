"""
train_decision_tree_v2.py
─────────────────────────
Retrain role-classification Decision-Tree with expanded V2 skill vectors.

Inputs
------
  data/processed/job_skill_vectors_v2.csv   (15 230 × 1 154)

Outputs
-------
  models/role_classifier_v2.pkl             – best DecisionTreeClassifier
  models/skill_columns_v2.pkl               – ordered feature column list
  models/training_report_v2.txt             – text report
  models/confusion_matrix_v2.png            – heatmap visualisation
  models/feature_importance_v2.csv          – top-50 skills

Usage
-----
  python scripts/train_decision_tree_v2.py                  # full run
  python scripts/train_decision_tree_v2.py --quick          # reduced grid (fast)
  python scripts/train_decision_tree_v2.py --validate-only  # re-evaluate saved model
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import textwrap
import time
import warnings
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
from sklearn.model_selection import GridSearchCV, StratifiedShuffleSplit
from sklearn.tree import DecisionTreeClassifier

# ── paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
DATA_CSV       = ROOT / "data" / "processed" / "job_skill_vectors_v2.csv"
V1_MODEL       = ROOT / "models" / "decision_tree_role_classifier.pkl"
OUT_MODEL      = ROOT / "models" / "role_classifier_v2.pkl"
OUT_COLUMNS    = ROOT / "models" / "skill_columns_v2.pkl"
OUT_REPORT     = ROOT / "models" / "training_report_v2.txt"
OUT_CONFUSION  = ROOT / "models" / "confusion_matrix_v2.png"
OUT_IMPORTANCE = ROOT / "models" / "feature_importance_v2.csv"

# ── logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════════════
#  1.  LOAD DATA
# ═════════════════════════════════════════════════════════════════════════════

def load_data() -> tuple[pd.DataFrame, list[str]]:
    """Load skill-vector CSV and return (dataframe, skill_columns)."""
    log.info("Loading %s …", DATA_CSV.name)
    df = pd.read_csv(DATA_CSV)
    log.info("  Raw shape: %s", df.shape)

    skill_cols = sorted([c for c in df.columns if c.startswith("skill_")])
    log.info("  Skill columns: %d", len(skill_cols))
    log.info("  Roles: %d unique → %s", df["role_id"].nunique(),
             ", ".join(df["role_id"].value_counts().index[:5]) + " …")
    return df, skill_cols


# ═════════════════════════════════════════════════════════════════════════════
#  2.  STRATIFIED SPLIT  (70 / 15 / 15)
# ═════════════════════════════════════════════════════════════════════════════

def stratified_split(
    X: np.ndarray,
    y: np.ndarray,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    random_state: int = 42,
) -> dict[str, np.ndarray]:
    """Return dict with train/val/test X and y arrays (stratified)."""
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-9

    # First split: train vs (val+test)
    sss1 = StratifiedShuffleSplit(
        n_splits=1,
        test_size=val_ratio + test_ratio,
        random_state=random_state,
    )
    train_idx, rest_idx = next(sss1.split(X, y))

    # Second split: val vs test (half-half of the remainder)
    relative_test = test_ratio / (val_ratio + test_ratio)
    sss2 = StratifiedShuffleSplit(
        n_splits=1,
        test_size=relative_test,
        random_state=random_state,
    )
    val_idx_rel, test_idx_rel = next(sss2.split(X[rest_idx], y[rest_idx]))
    val_idx = rest_idx[val_idx_rel]
    test_idx = rest_idx[test_idx_rel]

    splits = {
        "X_train": X[train_idx], "y_train": y[train_idx],
        "X_val":   X[val_idx],   "y_val":   y[val_idx],
        "X_test":  X[test_idx],  "y_test":  y[test_idx],
    }

    for name, arr in [("train", splits["y_train"]),
                      ("val",   splits["y_val"]),
                      ("test",  splits["y_test"])]:
        log.info("  %s: %d samples  (%d classes)",
                 name.ljust(5), len(arr), len(np.unique(arr)))

    return splits


# ═════════════════════════════════════════════════════════════════════════════
#  3.  GRID SEARCH  (DecisionTreeClassifier)
# ═════════════════════════════════════════════════════════════════════════════

# Full parameter grid
PARAM_GRID_FULL: dict = {
    "max_depth":         [10, 15, 20, 25, 30],
    "min_samples_split": [10, 20, 50, 100],
    "min_samples_leaf":  [5, 10, 20],
    "criterion":         ["gini", "entropy"],
}

# Quick grid for fast iteration
PARAM_GRID_QUICK: dict = {
    "max_depth":         [15, 25],
    "min_samples_split": [20, 50],
    "min_samples_leaf":  [5, 10],
    "criterion":         ["gini"],
}


def train_grid_search(
    X_train: np.ndarray,
    y_train: np.ndarray,
    param_grid: dict,
    cv: int = 5,
) -> GridSearchCV:
    """Run GridSearchCV over DecisionTreeClassifier."""
    n_combos = 1
    for v in param_grid.values():
        n_combos *= len(v)
    log.info("Grid search: %d combinations × %d-fold CV = %d fits",
             n_combos, cv, n_combos * cv)

    clf = DecisionTreeClassifier(
        random_state=42,
        class_weight="balanced",       # handle class imbalance
    )
    grid = GridSearchCV(
        clf,
        param_grid,
        cv=cv,
        scoring="f1_weighted",         # weighted F1 for imbalanced classes
        n_jobs=-1,
        verbose=1,
        refit=True,
    )
    grid.fit(X_train, y_train)

    log.info("Best score (weighted F1): %.4f", grid.best_score_)
    log.info("Best params: %s", grid.best_params_)
    return grid


# ═════════════════════════════════════════════════════════════════════════════
#  4.  EVALUATE PERFORMANCE
# ═════════════════════════════════════════════════════════════════════════════

def evaluate(
    model,
    X: np.ndarray,
    y: np.ndarray,
    label: str,
    class_names: list[str],
) -> dict:
    """Evaluate model on a split; return metrics dict."""
    y_pred = model.predict(X)
    acc = accuracy_score(y, y_pred)
    f1_w = f1_score(y, y_pred, average="weighted", zero_division=0)
    prec_w = precision_score(y, y_pred, average="weighted", zero_division=0)
    rec_w = recall_score(y, y_pred, average="weighted", zero_division=0)
    cm = confusion_matrix(y, y_pred, labels=class_names)
    report = classification_report(y, y_pred, labels=class_names,
                                   target_names=class_names, zero_division=0)

    log.info("  [%s]  accuracy=%.4f  F1_w=%.4f  prec_w=%.4f  rec_w=%.4f",
             label, acc, f1_w, prec_w, rec_w)

    return {
        "label": label,
        "accuracy": acc,
        "f1_weighted": f1_w,
        "precision_weighted": prec_w,
        "recall_weighted": rec_w,
        "confusion_matrix": cm,
        "classification_report": report,
        "y_pred": y_pred,
    }


# ═════════════════════════════════════════════════════════════════════════════
#  5.  FEATURE IMPORTANCE (top-50)
# ═════════════════════════════════════════════════════════════════════════════

def top_features(
    model,
    skill_cols: list[str],
    top_n: int = 50,
) -> pd.DataFrame:
    """Return DataFrame of top-N features by importance."""
    imp = model.feature_importances_
    df = pd.DataFrame({"skill_col": skill_cols, "importance": imp})
    df = df.sort_values("importance", ascending=False).head(top_n).reset_index(drop=True)
    df.index = df.index + 1
    df.index.name = "rank"
    return df


# ═════════════════════════════════════════════════════════════════════════════
#  6.  V1 COMPARISON
# ═════════════════════════════════════════════════════════════════════════════

def compare_v1(
    v2_test_metrics: dict,
    v2_model,
    X_test: np.ndarray,
    y_test: np.ndarray,
    class_names: list[str],
) -> str:
    """Compare V2 with V1 model if it exists. Return comparison text."""
    lines: list[str] = []
    if not V1_MODEL.exists():
        lines.append("V1 model not found — skipping comparison.")
        return "\n".join(lines)

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            v1_model = joblib.load(V1_MODEL)
    except Exception as exc:
        lines.append(f"Could not load V1 model: {exc}")
        return "\n".join(lines)

    v1_n_features = v1_model.n_features_in_
    v1_classes = list(v1_model.classes_)

    lines.append(f"V1 model: {type(v1_model).__name__}")
    lines.append(f"  Features: {v1_n_features}  (V2: {X_test.shape[1]})")
    lines.append(f"  Classes : {len(v1_classes)}  (V2: {len(class_names)})")
    lines.append(f"  Params  : max_depth={v1_model.get_params().get('max_depth')}, "
                 f"min_samples_leaf={v1_model.get_params().get('min_samples_leaf')}")
    lines.append("")

    # We can't directly evaluate V1 on V2 features (different dimensionality)
    # but we can report the comparison of params and known metrics
    lines.append("─── Performance Comparison ───")
    lines.append(f"  V2 Test Accuracy:     {v2_test_metrics['accuracy']:.4f}")
    lines.append(f"  V2 Test F1 (weighted): {v2_test_metrics['f1_weighted']:.4f}")
    lines.append(f"  V1 max_depth={v1_model.get_params().get('max_depth')} → "
                 f"V2 max_depth={v2_model.get_params().get('max_depth')}")
    lines.append(f"  V1 features: {v1_n_features} → V2 features: {X_test.shape[1]} "
                 f"(+{X_test.shape[1] - v1_n_features})")

    # Per-role breakdown: show which roles V2 predicts
    v2_report_lines = v2_test_metrics["classification_report"].split("\n")
    role_metrics: dict[str, dict] = {}
    for line in v2_report_lines:
        parts = line.split()
        if parts and parts[0] in class_names:
            role_metrics[parts[0]] = {
                "precision": float(parts[1]),
                "recall": float(parts[2]),
                "f1": float(parts[3]),
                "support": int(parts[4]),
            }

    lines.append("")
    lines.append("─── Per-Role V2 Performance ───")
    lines.append(f"  {'Role':<25} {'Prec':>6} {'Rec':>6} {'F1':>6} {'Support':>8}")
    lines.append(f"  {'─'*25} {'─'*6} {'─'*6} {'─'*6} {'─'*8}")
    for role in sorted(role_metrics.keys()):
        m = role_metrics[role]
        lines.append(f"  {role:<25} {m['precision']:>6.3f} {m['recall']:>6.3f} "
                     f"{m['f1']:>6.3f} {m['support']:>8d}")

    # Identify best/worst predicted roles
    if role_metrics:
        best_role = max(role_metrics, key=lambda r: role_metrics[r]["f1"])
        worst_role = min(role_metrics, key=lambda r: role_metrics[r]["f1"])
        lines.append("")
        lines.append(f"  Best  predicted role: {best_role} "
                     f"(F1={role_metrics[best_role]['f1']:.3f})")
        lines.append(f"  Worst predicted role: {worst_role} "
                     f"(F1={role_metrics[worst_role]['f1']:.3f})")

    return "\n".join(lines)


# ═════════════════════════════════════════════════════════════════════════════
#  7.  CONFUSION MATRIX PLOT
# ═════════════════════════════════════════════════════════════════════════════

def plot_confusion_matrix(cm: np.ndarray, class_names: list[str], path: Path):
    """Save confusion-matrix heatmap to PNG."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    fig_size = max(8, len(class_names) * 0.7)
    fig, ax = plt.subplots(figsize=(fig_size, fig_size))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=class_names, yticklabels=class_names,
        ax=ax, linewidths=0.5,
    )
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title("Confusion Matrix — Role Classifier V2 (Test Set)")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    log.info("Saved confusion matrix → %s", path)


# ═════════════════════════════════════════════════════════════════════════════
#  8.  SAMPLE USER VALIDATION  (100 synthetic users)
# ═════════════════════════════════════════════════════════════════════════════

def validate_sample_users(
    model,
    X_test: np.ndarray,
    y_test: np.ndarray,
    skill_cols: list[str],
    n_samples: int = 100,
) -> str:
    """Pick up to n_samples from test set, predict, and verify sense."""
    rng = np.random.RandomState(42)
    n = min(n_samples, len(y_test))
    idx = rng.choice(len(y_test), size=n, replace=False)

    X_sample = X_test[idx]
    y_true = y_test[idx]
    y_pred = model.predict(X_sample)

    correct = (y_true == y_pred).sum()
    lines = [
        f"Sample validation: {n} users from test set",
        f"  Correct: {correct}/{n} ({correct/n*100:.1f}%)",
        "",
        f"  {'#':>3}  {'True Role':<25} {'Predicted':<25} {'Match':>5}  Top-3 Skills",
        f"  {'─'*3}  {'─'*25} {'─'*25} {'─'*5}  {'─'*40}",
    ]

    # Show first 20 detailed rows
    for i, ix in enumerate(idx[:20]):
        active = np.where(X_sample[i] == 1)[0]
        top_skills = [skill_cols[j] for j in active[:3]]
        match_str = "✓" if y_true[i] == y_pred[i] else "✗"
        lines.append(
            f"  {i+1:>3}  {y_true[i]:<25} {y_pred[i]:<25} {match_str:>5}  "
            f"{', '.join(top_skills)}"
        )

    if n > 20:
        lines.append(f"  … ({n - 20} more rows omitted)")

    return "\n".join(lines)


# ═════════════════════════════════════════════════════════════════════════════
#  9.  REPORT GENERATION
# ═════════════════════════════════════════════════════════════════════════════

def generate_report(
    grid: GridSearchCV,
    train_metrics: dict,
    val_metrics: dict,
    test_metrics: dict,
    importance_df: pd.DataFrame,
    v1_comparison: str,
    sample_validation: str,
    skill_cols: list[str],
    elapsed: float,
) -> str:
    """Build full-text training report."""
    best = grid.best_estimator_
    sep = "=" * 78
    sec = "─" * 60

    lines = [
        sep,
        "  DECISION TREE ROLE CLASSIFIER V2 — TRAINING REPORT",
        sep,
        "",
        f"─── 1. DATA SUMMARY {sec[19:]}",
        f"  Features:           {len(skill_cols)} skill columns",
        f"  Total samples:      {len(grid.cv_results_['mean_test_score'])} grid combos evaluated",
        f"  Best CV score:      {grid.best_score_:.4f} (weighted F1)",
        f"  Training time:      {elapsed:.1f} seconds",
        "",
        f"─── 2. BEST HYPERPARAMETERS {sec[27:]}",
    ]
    for k, v in sorted(grid.best_params_.items()):
        lines.append(f"  {k:<25} {v}")

    lines += [
        "",
        f"  class_weight:               balanced",
        f"  scoring:                    f1_weighted",
        f"  random_state:               42",
        "",
        f"─── 3. SPLIT PERFORMANCE {sec[24:]}",
        f"  {'Split':<10} {'Accuracy':>10} {'F1_w':>10} {'Prec_w':>10} {'Rec_w':>10}",
        f"  {'─'*10} {'─'*10} {'─'*10} {'─'*10} {'─'*10}",
    ]

    for m in [train_metrics, val_metrics, test_metrics]:
        lines.append(
            f"  {m['label']:<10} {m['accuracy']:>10.4f} {m['f1_weighted']:>10.4f} "
            f"{m['precision_weighted']:>10.4f} {m['recall_weighted']:>10.4f}"
        )

    lines += [
        "",
        f"─── 4. TEST SET CLASSIFICATION REPORT {sec[37:]}",
        test_metrics["classification_report"],
        "",
        f"─── 5. TOP-50 FEATURE IMPORTANCE {sec[32:]}",
    ]
    lines.append(f"  {'Rank':>4}  {'Skill Column':<20} {'Importance':>12}")
    lines.append(f"  {'─'*4}  {'─'*20} {'─'*12}")
    for _, row in importance_df.iterrows():
        lines.append(f"  {row.name:>4}  {row['skill_col']:<20} {row['importance']:>12.6f}")

    lines += [
        "",
        f"─── 6. V1 vs V2 COMPARISON {sec[26:]}",
        v1_comparison,
        "",
        f"─── 7. SAMPLE USER VALIDATION {sec[29:]}",
        sample_validation,
        "",
        f"─── 8. MODEL TREE STATS {sec[23:]}",
        f"  Tree depth:         {best.get_depth()}",
        f"  Leaf nodes:         {best.get_n_leaves()}",
        f"  Total nodes:        {best.tree_.node_count}",
        f"  Classes:            {len(best.classes_)}",
        "",
        sep,
    ]

    return "\n".join(lines)


# ═════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Train Decision Tree V2")
    parser.add_argument("--quick", action="store_true",
                        help="Use reduced param grid for fast iteration")
    parser.add_argument("--validate-only", action="store_true",
                        help="Load saved model and re-evaluate on test split")
    parser.add_argument("--cv", type=int, default=5,
                        help="Number of CV folds (default: 5)")
    args = parser.parse_args()

    t0 = time.perf_counter()

    # ── 1. Load ──────────────────────────────────────────────────────────
    df, skill_cols = load_data()

    X = df[skill_cols].values.astype(np.float32)
    y = df["role_id"].values
    class_names = sorted(np.unique(y).tolist())
    log.info("Classes (%d): %s", len(class_names), class_names)

    # ── 2. Split ─────────────────────────────────────────────────────────
    log.info("Stratified split 70/15/15 …")
    splits = stratified_split(X, y)

    # ── 3. Train / Load ──────────────────────────────────────────────────
    if args.validate_only:
        if not OUT_MODEL.exists():
            log.error("No saved model at %s", OUT_MODEL)
            sys.exit(1)
        log.info("Loading saved model …")
        best_model = joblib.load(OUT_MODEL)
        grid = None
        elapsed_train = 0.0
    else:
        param_grid = PARAM_GRID_QUICK if args.quick else PARAM_GRID_FULL
        log.info("Training with %s grid …", "QUICK" if args.quick else "FULL")
        t_train = time.perf_counter()
        grid = train_grid_search(
            splits["X_train"], splits["y_train"],
            param_grid, cv=args.cv,
        )
        elapsed_train = time.perf_counter() - t_train
        best_model = grid.best_estimator_

    # ── 4. Evaluate ──────────────────────────────────────────────────────
    log.info("Evaluating …")
    train_metrics = evaluate(
        best_model, splits["X_train"], splits["y_train"], "train", class_names
    )
    val_metrics = evaluate(
        best_model, splits["X_val"], splits["y_val"], "val", class_names
    )
    test_metrics = evaluate(
        best_model, splits["X_test"], splits["y_test"], "test", class_names
    )

    # ── 5. Feature importance ────────────────────────────────────────────
    importance_df = top_features(best_model, skill_cols, top_n=50)

    # ── 6. V1 comparison ────────────────────────────────────────────────
    v1_comparison = compare_v1(
        test_metrics, best_model,
        splits["X_test"], splits["y_test"], class_names,
    )

    # ── 7. Sample validation ─────────────────────────────────────────────
    sample_validation = validate_sample_users(
        best_model,
        splits["X_test"], splits["y_test"],
        skill_cols, n_samples=100,
    )

    # ── 8. Save artefacts ────────────────────────────────────────────────
    elapsed_total = time.perf_counter() - t0

    if not args.validate_only:
        OUT_MODEL.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(best_model, OUT_MODEL, compress=3)
        log.info("Saved model → %s  (%d KB)",
                 OUT_MODEL, OUT_MODEL.stat().st_size // 1024)

        joblib.dump(skill_cols, OUT_COLUMNS, compress=3)
        log.info("Saved columns → %s", OUT_COLUMNS)

    # Confusion matrix plot
    plot_confusion_matrix(
        test_metrics["confusion_matrix"], class_names, OUT_CONFUSION,
    )

    # Feature importance CSV
    importance_df.to_csv(OUT_IMPORTANCE)
    log.info("Saved feature importance → %s", OUT_IMPORTANCE)

    # Report
    if grid is not None:
        report_text = generate_report(
            grid, train_metrics, val_metrics, test_metrics,
            importance_df, v1_comparison, sample_validation,
            skill_cols, elapsed_train,
        )
    else:
        report_text = (
            "VALIDATE-ONLY RUN\n"
            f"Test accuracy: {test_metrics['accuracy']:.4f}\n"
            f"Test F1 (weighted): {test_metrics['f1_weighted']:.4f}\n\n"
            + test_metrics["classification_report"]
            + "\n\n" + v1_comparison
            + "\n\n" + sample_validation
        )

    OUT_REPORT.write_text(report_text, encoding="utf-8")
    log.info("Saved report → %s", OUT_REPORT)

    # ── 9. Summary ───────────────────────────────────────────────────────
    print()
    print("=" * 78)
    print("  COMPLETE — Decision Tree Role Classifier V2")
    if grid is not None:
        print(f"  Best CV F1 (weighted): {grid.best_score_:.4f}")
        print(f"  Best params:           {grid.best_params_}")
    print(f"  Train accuracy:        {train_metrics['accuracy']:.4f}")
    print(f"  Val   accuracy:        {val_metrics['accuracy']:.4f}")
    print(f"  Test  accuracy:        {test_metrics['accuracy']:.4f}")
    print(f"  Test  F1 (weighted):   {test_metrics['f1_weighted']:.4f}")
    print(f"  Tree depth:            {best_model.get_depth()}")
    print(f"  Leaf nodes:            {best_model.get_n_leaves()}")
    print(f"  Elapsed:               {elapsed_total:.1f}s")
    print(f"  Model:                 {OUT_MODEL}")
    print(f"  Columns:               {OUT_COLUMNS}")
    print(f"  Report:                {OUT_REPORT}")
    print("=" * 78)


if __name__ == "__main__":
    main()
