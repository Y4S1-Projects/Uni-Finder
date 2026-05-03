# AI-driven Career Pathway, Skill Gap and Job Match Recommender for Sri Lanka IT Industry

## 1. System Overview

### 1.1 Purpose

This system is implemented as the career intelligence subsystem of Uni-Finder. Its purpose is to produce three tightly coupled outputs from a user skill/profile input:

1. Job-role match ranking.
2. Skill-gap and readiness diagnostics.
3. Career progression guidance with next-step laddering.

The production API is served by a FastAPI service at [career-service/app.py](../career-service/app.py), and the underlying data/model assets are bundled inside [career-service/career-ml](../career-service/career-ml).

### 1.2 Key Functionalities

1. Predict current role from skills using a trained decision tree via `/predict_role`.
2. Recommend top N roles using cosine similarity + multi-component weighted scoring via `/recommend_careers`.
3. Compute role-specific gaps and readiness via `/simulate_path` and role gap internals.
4. Generate explainability narratives (Gemini-first, template fallback) via `/explain_career`.
5. Expose career ladder and progression endpoints via `/career_ladder/{domain}`, `/analyze_career_progression`, and `/compare_career_paths`.

### 1.3 Sri Lankan Skill Gap Relevance

The project operationalizes job-market evidence from Sri Lankan-style job board pipelines (TopJobs/MyJobs style inputs are codified in ingestion scripts) and transforms that into role-level skill requirements. By mapping user profiles against this market-derived representation, the system addresses the common mismatch between university graduate skill portfolios and local employer requirements.

The critical design contribution is the separation of:

1. Match score (multi-factor suitability and ranking).
2. Readiness score (immediate execution readiness from core/supporting skill coverage).

This prevents overconfident recommendations for users with only superficial overlap.

## 2. Full Architecture

### 2.1 Microservice Topology

At repository level, Uni-Finder is multi-service and containerized via [docker-compose.yml](../docker-compose.yml):

1. React frontend: [frontend](../frontend).
2. Node API: [backend](../backend).
3. Degree service: [degree-recommendation-service](../degree-recommendation-service).
4. Career service: [career-service](../career-service).
5. Budget service and scholarship service.

Career intelligence is isolated in FastAPI service [career-service/app.py](../career-service/app.py), with local model/data loading at startup from [career-service/data_loader.py](../career-service/data_loader.py).

### 2.2 Backend-ML Interaction Model

The career service does not call an external model server at inference time. Instead, it embeds ML artifacts and data tables directly:

1. Data and vectors are loaded into `DataStore` in-memory singleton.
2. Classifier model is loaded from `.pkl` (V1 or V2 based on config).
3. Recommender computes cosine similarity in-process.
4. Scoring engine applies deterministic weighted ranking and penalties/boosts.

This lowers runtime coupling and avoids network latency between backend and ML runtime.

### 2.3 End-to-End Data Flow

1. Frontend submits profile and skills through [frontend/src/services/careerApi.js](../frontend/src/services/careerApi.js).
2. FastAPI endpoint receives typed payload per [career-service/schemas.py](../career-service/schemas.py).
3. Recommender in [career-service/services/recommender.py](../career-service/services/recommender.py):
   1. Vectorizes user profile (`UserVectorizer` for enhanced mode, binary vector for legacy mode).
   2. Runs cosine similarity against role profile matrices.
   3. Runs full scoring engine in [career-service/services/scoring_engine.py](../career-service/services/scoring_engine.py).
   4. Attaches skill gaps, ladder position, next role, and explainability features.
4. Frontend requests detailed explanation via `/explain_career` and renders detail modal using [frontend/src/components/career/CareerDetailModal.jsx](../frontend/src/components/career/CareerDetailModal.jsx).

### 2.4 API Communication Style

1. JSON-over-HTTP, synchronous request/response.
2. Typed request contracts with Pydantic.
3. CORS configurable through environment variable in [career-service/config.py](../career-service/config.py).

## 3. Component-Level Breakdown

### 3.1 Career Pathway Engine

#### 3.1.1 Ladder Assets

Career pathway data is stored in JSON/CSV artifacts under [career-service/career-ml/career_path](../career-service/career-ml/career_path), including:

1. `career_ladders_enhanced.json`.
2. `role_level_transitions.csv`.
3. `pathway_engine.ipynb`.

Generation utilities include [career-service/career-ml/scripts/generate_career_ladders.py](../career-service/career-ml/scripts/generate_career_ladders.py) and [career-service/career-ml/scripts/generate_role_transitions.py](../career-service/career-ml/scripts/generate_role_transitions.py).

#### 3.1.2 Runtime Ladder Logic

Implemented in [career-service/services/career_service.py](../career-service/services/career_service.py):

1. `get_career_ladder(domain)` returns full domain ladder.
2. `analyze_career_progression(...)` predicts current level and computes level-wise readiness and match.
3. `compare_career_paths(...)` compares user fit across candidate domains.
4. `get_next_role(...)` supports graceful fallback and seniority-aware progression.

#### 3.1.3 Simulation Mechanism

`/simulate_path` in [career-service/app.py](../career-service/app.py) executes:

1. Current role to next role mapping.
2. Skill gap extraction for next role.
3. Readiness score and missing skill output.

### 3.2 Skill Gap Analyzer

#### 3.2.1 Core Comparison Logic

`detect_skill_gap(...)` in [career-service/services/career_service.py](../career-service/services/career_service.py):

1. Selects role-required skills where importance >= threshold.
2. Computes set intersection and difference against user skills.
3. Computes readiness = matched_required / total_required.

#### 3.2.2 Skill Categorization

Category and tier logic are defined in [career-service/career-ml/scripts/skill_normalizer.py](../career-service/career-ml/scripts/skill_normalizer.py):

1. Alias normalization for near-duplicate skill strings.
2. Domain-specific cluster assignment.
3. Tiering into core, supporting, optional, generic soft, and domain signal.

#### 3.2.3 Similarity Algorithms

1. Production recommendation similarity is cosine similarity (scikit-learn pairwise).
2. Set overlap operations are used for gap and top-skill coverage.
3. Jaccard is not used in the production inference path in current service modules.

### 3.3 Job Recommendation System

#### 3.3.1 Inference Pipeline

Implemented in [career-service/services/recommender.py](../career-service/services/recommender.py):

1. Input normalization and entry-level classification.
2. Enhanced mode (profile-aware) if enhanced assets and profile context exist.
3. Legacy mode fallback (skill-only).
4. Optional enhanced+legacy merge for roles absent in enhanced matrix.
5. Full score composition through `score_role_for_user`.
6. Tie-break ranking by final score, core coverage, confidence.

#### 3.3.2 Feature Vector Construction

1. Legacy: binary skill vector over role skill matrix columns.
2. Enhanced: user vector from [career-service/services/user_vectorizer.py](../career-service/services/user_vectorizer.py).

#### 3.3.3 Scoring and Ranking

`FullScoreBreakdown` captures:

1. Skill match.
2. Core coverage.
3. Domain preference.
4. Experience fit.
5. Current status fit.
6. Education fit.
7. Career goal fit.
8. Seniority fit.
9. Confidence.

Final recommendation payload includes match score, readiness score, explanation factors, skill clusters, ladder metadata, and profile source confidence.

## 4. Algorithms Used

### 4.1 Decision Tree Classifier

Training and artifact generation are in [career-service/career-ml/scripts/train_decision_tree_v2.py](../career-service/career-ml/scripts/train_decision_tree_v2.py):

1. Model: `DecisionTreeClassifier` with `class_weight="balanced"`.
2. Feature space: 1147 skill columns.
3. Search: GridSearchCV (weighted F1 objective).
4. Split: stratified 70/15/15.

Stored artifacts:

1. [career-service/career-ml/models/role_classifier_v2.pkl](../career-service/career-ml/models/role_classifier_v2.pkl).
2. [career-service/career-ml/models/skill_columns_v2.pkl](../career-service/career-ml/models/skill_columns_v2.pkl).

### 4.2 Similarity-Based Matching

1. Cosine similarity in both enhanced and legacy recommendation branches.
2. Role-level ranking then adjusted by multi-factor scoring engine.

### 4.3 Rule-Based Fallback Logic

If Gemini is unavailable/fails, fallback explanations are generated by [career-service/services/fallback_templates.py](../career-service/services/fallback_templates.py) using structured scoring outputs.

### 4.4 Explainability Logic (SHAP-like but deterministic)

There is no SHAP dependency in the service path. Explainability is generated by:

1. Deterministic feature decomposition (`score_breakdown`, penalties, boosts).
2. Human-readable reason synthesis (`generate_ranking_explanation`).
3. LLM narrative formatting with strict contextual prompt in [career-service/services/explainability.py](../career-service/services/explainability.py).

### 4.5 Random Forest Status

Random Forest is not implemented in production scoring/prediction path in the current service modules. The classifier stack in deployed code is decision-tree based.

## 5. Data Processing Pipeline (Raw to Prediction)

### 5.1 Raw Job Ingestion and Unification

1. Multi-source scraping scripts feed raw CSVs.
2. Merge and dedup handled by [career-service/career-ml/scripts/deduplicate_and_merge_jobs.py](../career-service/career-ml/scripts/deduplicate_and_merge_jobs.py):
   1. Exact dedup by title+company hash.
   2. Fuzzy dedup via token similarity thresholds.

### 5.2 Data Cleaning and Standardization

[career-service/career-ml/scripts/clean_and_standardize_jobs.py](../career-service/career-ml/scripts/clean_and_standardize_jobs.py) performs:

1. Title normalization.
2. Experience parsing.
3. Salary parsing.
4. Job type and remote policy detection.
5. Industry tagging.
6. Location normalization.

### 5.3 Skill Expansion and Normalization

1. Skill catalog expansion in [career-service/career-ml/scripts/expand_skills_comprehensive.py](../career-service/career-ml/scripts/expand_skills_comprehensive.py).
2. Alias and domain-tier normalization in [career-service/career-ml/scripts/skill_normalizer.py](../career-service/career-ml/scripts/skill_normalizer.py).

### 5.4 Vector and Role Profile Construction

1. Job-skill matrix: [career-service/career-ml/scripts/build_job_skill_vectors_v2.py](../career-service/career-ml/scripts/build_job_skill_vectors_v2.py).
2. Role profiles (frequency, TF-IDF importance): [career-service/career-ml/scripts/build_role_skill_profiles_v2.py](../career-service/career-ml/scripts/build_role_skill_profiles_v2.py).
3. Enhanced v3 rebuild: [career-service/career-ml/scripts/rebuild_enhanced_features_v3.py](../career-service/career-ml/scripts/rebuild_enhanced_features_v3.py).

### 5.5 Model Training and Artifact Export

Decision tree training in [career-service/career-ml/scripts/train_decision_tree_v2.py](../career-service/career-ml/scripts/train_decision_tree_v2.py), then inference in [career-service/services/predictor.py](../career-service/services/predictor.py).

## 6. Feature Engineering

### 6.1 Skill Vector Creation

Job-level vectors include metadata + binary skill columns (`skill_sk###`).

### 6.2 Role Vector Mapping

Role vectors are constructed by aggregating job vectors per role (mean frequency, TF-IDF-style importance) and persisted as role profile CSVs.

### 6.3 User Profile Encoding

In [career-service/services/user_vectorizer.py](../career-service/services/user_vectorizer.py), user vectors combine:

1. Skill dimensions.
2. One-hot encoded experience, education, domain, status, job type.

Metadata is read from [career-service/career-ml/data/processed/enhanced_feature_columns.json](../career-service/career-ml/data/processed/enhanced_feature_columns.json) (and v3 variant for rebuilt assets).

## 7. Database Design

### 7.1 Career Subsystem Storage Model

Career intelligence is primarily file-backed and in-memory:

1. CSV/JSON/PKL assets under [career-service/career-ml/data](../career-service/career-ml/data) and [career-service/career-ml/models](../career-service/career-ml/models).
2. Runtime object cache in `DataStore` from [career-service/data_loader.py](../career-service/data_loader.py).

### 7.2 Application-Wide Persistent Storage

The broader Uni-Finder platform uses MongoDB via Node backend models:

1. [backend/models/user.model.js](../backend/models/user.model.js).
2. [backend/models/manager.model.js](../backend/models/manager.model.js).
3. [backend/models/review.model.js](../backend/models/review.model.js).
4. [backend/models/budgetPrediction.model.js](../backend/models/budgetPrediction.model.js).

Career-specific recommendations are currently not persisted as a dedicated Mongo collection in the FastAPI career service layer.

### 7.3 Conceptual Entity Groups for Thesis Schema Section

For thesis documentation, the implemented data entities can be organized as:

1. Skills: `skills_v2.csv`.
2. Jobs: `jobs_*` processed vectors and features.
3. Roles and ladders: `role_*`, `career_ladders_*`, transitions.
4. User input profile: transient API payload (not persisted by career service).

## 8. API Design

### 8.1 Core Endpoints

Defined in [career-service/app.py](../career-service/app.py):

1. `GET /health`
2. `POST /predict_role`
3. `POST /recommend_careers`
4. `POST /simulate_path`
5. `POST /explain_career`
6. `GET /career_ladder/{domain}`
7. `GET /career_ladders/list`
8. `POST /analyze_career_progression`
9. `POST /compare_career_paths`
10. `GET /skill_details/{skill_id}`

### 8.2 Example Request/Response Contracts

#### 8.2.1 /recommend_careers Request

Based on [career-service/schemas.py](../career-service/schemas.py):

```json
{
  "user_skill_ids": ["SK004", "SK031", "SK124"],
  "top_n": 5,
  "experience_level": "1-3",
  "current_status": "working",
  "education_level": "bachelors",
  "career_goal": "get_promoted",
  "preferred_domain": "ai_ml",
  "preferred_job_type": "full_time"
}
```

#### 8.2.2 /recommend_careers Response (abridged)

Empirically verified from [career-service/sample_entry_level.json](../career-service/sample_entry_level.json):

```json
{
  "recommendations": [
    {
      "role_id": "AI_ML_ENGINEER_INT",
      "match_score": 0.4536,
      "readiness_score": 0.235,
      "score_breakdown": {
        "skill_match_score": 0.4523,
        "core_skill_coverage_score": 0.0,
        "final_match_score": 0.4536,
        "penalties_applied": ["weak_core_coverage(0%)"],
        "boosts_applied": ["perfect_seniority", "career_goal_aligned"]
      },
      "matched_core_skills": [],
      "missing_critical_skills": [{ "id": "SK004", "name": "python" }],
      "is_best_match": true,
      "profile_source": "synthetic_repair"
    }
  ],
  "total_roles_compared": 62,
  "mode": "enhanced+legacy",
  "domain_filter_applied": false,
  "profile_used": {
    "experience_level": "student"
  }
}
```

#### 8.2.3 /predict_role Request

```json
{
  "user_skill_ids": ["SK001", "SK003", "SK018"]
}
```

#### 8.2.4 /predict_role Response (shape)

```json
{
  "predicted_role": "JR_BE_DEV",
  "predicted_role_title": "Junior Backend Developer",
  "confidence": 0.73,
  "domain": "BACKEND_ENGINEERING",
  "next_role": "BE_DEV",
  "next_role_title": "Backend Developer",
  "skill_gap": { "readiness_score": 0.42 },
  "skills_used": ["sk001", "sk003", "sk018"]
}
```

#### 8.2.5 /analyze_career_progression Request

```json
{
  "user_skill_ids": ["SK002", "SK005", "SK006"],
  "current_role_id": "JR_FE_DEV",
  "target_domain": "FRONTEND_ENGINEERING",
  "show_all_levels": true
}
```

## 9. Integration Between Components

### 9.1 Backend Calls to ML Logic

In-process invocation graph:

1. Endpoint -> service orchestrator in [career-service/services/recommender.py](../career-service/services/recommender.py).
2. Recommender -> scoring in [career-service/services/scoring_engine.py](../career-service/services/scoring_engine.py).
3. Recommender -> path and gap helpers in [career-service/services/career_service.py](../career-service/services/career_service.py).
4. Explain endpoint -> [career-service/services/explainability.py](../career-service/services/explainability.py).

### 9.2 Result Aggregation

The recommender aggregates into one response object:

1. Ranking scores.
2. Readiness and gap details.
3. Ladder placement.
4. Explainability vectors/text fields.

Frontend then composes this into recommendation cards and detailed modal views.

## 10. Deployment Architecture

### 10.1 Containerization

Career service Docker definition in [career-service/Dockerfile](../career-service/Dockerfile):

1. Python 3.11 slim base.
2. Dependencies from `requirements.txt`.
3. Uvicorn host `0.0.0.0:5004`.
4. Health check on `/health`.

### 10.2 Multi-Service Local Deployment

[docker-compose.yml](../docker-compose.yml) defines service mesh, ports, and frontend env wiring to career endpoint.

### 10.3 Azure Deployment Path

Azure Container Apps deployment automation script in [deploy/deploy-unifinder-local.ps1](../deploy/deploy-unifinder-local.ps1):

1. Pull images from ACR.
2. Deploy/update per service.
3. Apply CORS configuration and service URLs.

## 11. Testing Strategy

### 11.1 Unit/Component Tests

1. Scenario scripts such as [career-service/test_phase_b.py](../career-service/test_phase_b.py) and [career-service/test_phase_d.py](../career-service/test_phase_d.py).
2. Data diagnostics and repair scripts (for data consistency) such as [career-service/career-ml/autofix_data_pipeline.py](../career-service/career-ml/autofix_data_pipeline.py).

### 11.2 Recommendation Accuracy Tests

[career-service/career-ml/test_recommendation_accuracy.py](../career-service/career-ml/test_recommendation_accuracy.py) executes:

1. 10 profile test cases.
2. Edge-case suite (empty skills, single skill, invalid skill IDs).
3. Role expectation checks in top-N.

### 11.3 ML Evaluation Artifacts

1. Training report: [career-service/career-ml/models/training_report_v2.txt](../career-service/career-ml/models/training_report_v2.txt).
2. Confusion matrix: [career-service/career-ml/models/confusion_matrix_v2.png](../career-service/career-ml/models/confusion_matrix_v2.png).
3. Feature importance: [career-service/career-ml/models/feature_importance_v2.csv](../career-service/career-ml/models/feature_importance_v2.csv).
4. Validation outputs: [career-service/evaluation_results](../career-service/evaluation_results).

## 12. Evaluation Metrics

### 12.1 Classifier Metrics (V2)

From [career-service/career-ml/models/training_report_v2.txt](../career-service/career-ml/models/training_report_v2.txt):

1. Accuracy: 0.7895
2. Weighted F1: 0.7982
3. Weighted precision: 0.82 (approx from report table context)
4. Weighted recall: 0.79

### 12.2 Recommendation Quality Metrics

Evidence in [career-service/evaluation_results/VALIDATION_SUMMARY.md](../career-service/evaluation_results/VALIDATION_SUMMARY.md) and scenario logs indicates:

1. Scenario routing checks pass for tested frontend/data/backend profiles.
2. Logical consistency checks on missing vs matched skills are explicitly validated.

### 12.3 Data Quality Metrics

From [career-service/career-ml/data/reports/skill_coverage_summary.txt](../career-service/career-ml/data/reports/skill_coverage_summary.txt):

1. Total skills: 1147
2. Orphan skills: 207
3. Weak skills: 118
4. Well-mapped skills: 822

## 13. Explainability System

### 13.1 Explanation Generation Stack

1. Structured factor generation in scoring engine (`score_breakdown`, domain impact, why-ranked, readiness limits).
2. Narrative generation via Gemini in [career-service/services/explainability.py](../career-service/services/explainability.py).
3. Deterministic fallback templates in [career-service/services/fallback_templates.py](../career-service/services/fallback_templates.py).

### 13.2 Trust and Transparency Controls

1. `profile_source` field explicitly flags synthetic role profiles.
2. `confidence_score` quantifies mapping confidence based on profile depth and job evidence.
3. Explanations include concrete matched/missing critical skills, not only generic text.

## 14. Limitations

### 14.1 Data Limitations

1. Non-trivial orphan/weak skill counts remain in coverage audit.
2. Some domains/roles rely on synthetic expert profiles (`synthetic_expert`, `synthetic_repair`) due to sparse market samples.
3. Legacy and enhanced profile spaces can diverge; merge mode (`enhanced+legacy`) is used to avoid role omission.

### 14.2 Model Limitations

1. Decision tree model exhibits class-imbalance sensitivity on very low-support roles (e.g., intern-level single-sample classes in report).
2. Current classifier class space is role IDs derived from available labeled data, not full theoretical ladder universe.

### 14.3 Scalability and Operational Limits

1. Startup preloads large CSV matrices into memory; this simplifies runtime but increases memory footprint.
2. Data pipeline scripts are batch-oriented and predominantly file-based, not stream/warehouse native.
3. Explainability LLM path depends on external API availability; fallback mitigates but does not equal LLM richness.

## Appendix A: Key Runtime Files

1. API entrypoint: [career-service/app.py](../career-service/app.py)
2. Data loader and cache: [career-service/data_loader.py](../career-service/data_loader.py)
3. Request schemas: [career-service/schemas.py](../career-service/schemas.py)
4. Recommender orchestration: [career-service/services/recommender.py](../career-service/services/recommender.py)
5. Scoring engine: [career-service/services/scoring_engine.py](../career-service/services/scoring_engine.py)
6. Skill helper: [career-service/services/skill_service.py](../career-service/services/skill_service.py)
7. User vectorizer: [career-service/services/user_vectorizer.py](../career-service/services/user_vectorizer.py)
8. Career ladder services: [career-service/services/career_service.py](../career-service/services/career_service.py)
9. Explainability service: [career-service/services/explainability.py](../career-service/services/explainability.py)
10. Fallback templates: [career-service/services/fallback_templates.py](../career-service/services/fallback_templates.py)

## Appendix B: Referenced Pipeline Scripts

1. [career-service/career-ml/scripts/deduplicate_and_merge_jobs.py](../career-service/career-ml/scripts/deduplicate_and_merge_jobs.py)
2. [career-service/career-ml/scripts/clean_and_standardize_jobs.py](../career-service/career-ml/scripts/clean_and_standardize_jobs.py)
3. [career-service/career-ml/scripts/expand_skills_comprehensive.py](../career-service/career-ml/scripts/expand_skills_comprehensive.py)
4. [career-service/career-ml/scripts/build_job_skill_vectors_v2.py](../career-service/career-ml/scripts/build_job_skill_vectors_v2.py)
5. [career-service/career-ml/scripts/build_role_skill_profiles_v2.py](../career-service/career-ml/scripts/build_role_skill_profiles_v2.py)
6. [career-service/career-ml/scripts/rebuild_enhanced_features_v3.py](../career-service/career-ml/scripts/rebuild_enhanced_features_v3.py)
7. [career-service/career-ml/scripts/train_decision_tree_v2.py](../career-service/career-ml/scripts/train_decision_tree_v2.py)
8. [career-service/career-ml/scripts/generate_career_ladders.py](../career-service/career-ml/scripts/generate_career_ladders.py)
9. [career-service/career-ml/scripts/generate_role_transitions.py](../career-service/career-ml/scripts/generate_role_transitions.py)
10. [career-service/career-ml/autofix_data_pipeline.py](../career-service/career-ml/autofix_data_pipeline.py)
