# Career Recommendation System - Validation Suite Summary

**Evaluation Date:** 2026-03-09  
**System Version:** Phase D + v3 Data Migration  
**Core Methodology:** 9-Component Scoring Engine + Discrete Role Classification

## 1. Data Foundation (v3 Build)
The current recommendation engine is powered by the **v3 Data Migration**, which drastically improved coverage and reliability compared to previous versions:

- **Volume:** 15,230 Jobs processed and indexed.
- **Granularity:** 1,147 distinct skills mapped (increased from 300).
- **Diversity:** 20 distinct career domains supported (increased from 7).
- **Quality:** Tier-weighted skill profiles (Core vs. Supporting) for every role.

## 2. Model Accuracy & Evaluation
The system utilizes a specialized **Role Classifier** (`role_classifier_v2.pkl`) for high-precision routing into entry-level paths.

| Metric | Performance |
|--------|-------------|
| **Accuracy** | 78.95% |
| **F1 Score (weighted)** | 0.80 |
| **Classes Covered** | 15 Junior/Entry-level specialist roles |
| **Validation Method** | Stratified Hold-out Test Set (v3) |

- **Artifacts:** `metrics.json`, `metrics.csv`, `confusion_matrix.png`

## 3. Systematic Rule Validation (Scenarios)
We executed a suite of "Synthetic User" scenarios to verify that the **Scoring Engine** (weights, penalties, boosts) produces logically correct rankings.

| Scenario Profile | Key Skills Provided | Predicted Matches | Confidence |
|------------------|---------------------|-------------------|------------|
| Frontend Heavy   | React, JS, HTML, CSS | FE_DEV, FS_DEV    | High       |
| Data Science     | Python, ML, Stats    | ML Scientist, DA  | High       |
| Backend Heavy    | Java, Spring, SQL    | BE_DEV, JR_BE_DEV | High       |

- **Result:** **100% Success Rate** for primary career path routing.
- **Safety check:** Junior users correctly receive "Entry-level" role suggestions via the `classify_user_level` logic.

## 4. Explainability & Logic Integrity
The system's "Why this role?" engine was audited for consistency. We verified that for any recommendation:
1.  **Missing Skills** are never found within the user's **Provided Skills** (Logical correctness).
2.  **Readiness Score** correctly penalizes users who lack "Core" skills even if their "Supporting" skills match.
3.  **Seniority Fit** reflects the user's input experience (e.g., a student is not recommended a 'Lead Engineer' role).

- **Logic Verification Log:** `recommendation_validation_report.csv`

## 5. Artifact Directory
The following files are generated in `/evaluation_results/` as demonstrable proof:
- `metrics.json`: Summary stats.
- `metrics.csv`: Per-role detail.
- `confusion_matrix.png`: Visual distinctiveness map.
- `scenario_test_results.json`: Scenario execution log.
- `recommendation_validation_report.csv`: Logic verification evidence.
