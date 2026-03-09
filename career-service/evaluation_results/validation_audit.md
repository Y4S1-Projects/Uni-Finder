# Validation Audit Report

## Existing validation-related code found
1. `career-ml/test_recommendation_accuracy.py`
   - **What it does:** Runs 10 predefined skill scenarios against the recommender and verifies if the expected role is in the top 10. Also tests score distribution and career ladder consistency.
   - **Usability:** Usable, but it only outputs to the console.
   - **Incomplete:** Yes, it does not generate exportable JSON/CSV files or comprehensive metrics.

2. `career-ml/scripts/train_decision_tree_v2.py`
   - **What it does:** Trains the job-role classifier and generates an initial classification report text file and confusion matrix PNG inside `career-ml/models/`.
   - **Usability:** Usable. The outputs prove the model was evaluated.
   - **Incomplete:** Yes, there is no standalone offline evaluation script dedicated strictly to inference and metric saving (like `metrics.json` tracking).

3. `test_phase_b.py` and `test_phase_d.py`
   - **What it does:** Manual HTTP payload testing scripts that save small sample JSON files (e.g. `sample_backend.json`).
   - **Usability:** Useful for API visual inspection but not automated validation.
   - **Incomplete:** Not a rigorous scenario-based validation suite.

## Missing validation capabilities
- **No offline evaluation script:** A standalone script that accurately evaluates the prediction model locally without training it.
- **No saved metrics JSON:** `metrics.json` doesn't exist for automated tracking.
- **No scenario-based validation reporter:** Existing test scripts print to console, but do not export `scenario_test_results.json`.
- **No explainability validation report:** No checks to ensure that the skill gaps strictly align with the user profile vs role requirements.
- **No frontend/demo validation view:** (Though out of scope for a backend artifacts ticket).

## Recommended implementation plan
1. **ML Evaluation Script:** Create `career-ml/evaluation/evaluate_model.py`. This script will load the saved dataset and model `role_classifier_v2.pkl`, compute accuracy, precision, recall, and F1 over the test split, generate a `metrics.json` and a `confusion_matrix.png` directly into an `evaluation_results` folder.
2. **Scenario-Based Validation:** Create `career-ml/evaluation/run_scenario_validation.py`. This will load dynamic user profiles (e.g., student vs senior API dev) and pass them to the inference logic, asserting exact logic flows and saving to `scenario_test_results.json`.
3. **Explainability Logic Validator:** Create `career-ml/evaluation/validate_explainability.py`. It will test recommendation payloads, cross-checking that all "missing_critical_skills" are actually NOT in the user's skillset, and save a `recommendation_validation_report.csv`.
4. **Result Consolidation:** Add a `npm run validate` or pure Python commands that generate all of the above artifacts into `career-service/evaluation_results/`.
5. **Documentation:** Create a `VALIDATION.md` outlining the suite.
