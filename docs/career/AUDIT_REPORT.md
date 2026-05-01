# Career Recommendation System — Full Architecture + Data Quality Audit

**Date:** 2026-03-09  
**Scope:** career-service backend, career-ml data pipeline, frontend career components  
**Data Version Active:** `v2_fixed`

---

## PHASE 1 — ARCHITECTURE SCAN

### A. Data Sources (loaded at startup via `data_loader.py`)

| Data Asset              | Config Variable                 | File Path                                                   | Contents                                                                      |
| ----------------------- | ------------------------------- | ----------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Skills CSV              | `SKILLS_CSV`                    | `career-ml/data/expanded/skills_v2.csv`                     | 1,147 skills (id, name, aliases, category, type)                              |
| Job-Skill Vectors       | `JOB_SKILL_VECTORS_CSV`         | `career-ml/data/processed/job_skill_vectors_v2_fixed.csv`   | 15,230 jobs × 1,147 skill columns + 6 metadata cols                           |
| Role Skill Profiles     | `ROLE_PROFILE_CSV`              | `career-ml/data/processed/role_skill_profiles_v2_fixed.csv` | 8,679 rows (role_id, skill_id, frequency, importance) for 62 roles            |
| Career Ladders          | `CAREER_LADDERS_JSON`           | `career-ml/data/processed/career_ladders_v2.json`           | 20 domains, 173 total roles in ladders                                        |
| Role Metadata           | `ROLE_METADATA_JSON`            | `career-ml/data/processed/role_metadata.json`               | 175 entries (role_id → role_title mapping)                                    |
| Role Classifier Model   | `ROLE_CLASSIFIER_PKL`           | `career-ml/models/role_classifier_v2.pkl`                   | Decision tree trained on 1,147 features                                       |
| Skill Columns Order     | `SKILL_COLUMNS_PKL`             | `career-ml/models/skill_columns_v2.pkl`                     | 1,147 skill column names                                                      |
| Enhanced Role Profiles  | `ROLE_ENHANCED_PROFILES_CSV`    | `career-ml/data/processed/role_enhanced_profiles.csv`       | 62 roles × **330 dims** (300 skill + 30 categorical)                          |
| Enhanced Feature Meta   | `ENHANCED_FEATURE_COLUMNS_JSON` | `career-ml/data/processed/enhanced_feature_columns.json`    | Feature schema: only **300 skill cols** + 30 onehot, only **7 domain values** |
| Jobs Enhanced Features  | `JOBS_ENHANCED_FEATURES_CSV`    | `career-ml/data/processed/jobs_enhanced_features.csv`       | 5,470 jobs with extracted categorical features                                |
| Career Ladders Enhanced | (hardcoded path in `app.py`)    | `career-ml/career_path/career_ladders_enhanced.json`        | Enhanced ladders with level detail for ladder endpoints                       |

### B. Data Generation Scripts (`career-ml/scripts/`)

| Script                               | Purpose                                        | Input → Output                                                               |
| ------------------------------------ | ---------------------------------------------- | ---------------------------------------------------------------------------- |
| `expand_skills_comprehensive.py`     | Expand skills from ~300 to 1,147               | raw skills → `data/expanded/skills_v2.csv`                                   |
| `retag_jobs_with_expanded_skills.py` | Tag all jobs with expanded 1,147-skill set     | jobs_unified + skills_v2 → `job_skill_vectors_v2.csv`                        |
| `build_job_skill_vectors_v2.py`      | Build binary skill vector matrix               | tagged jobs → `job_skill_vectors_v2.csv`                                     |
| `build_role_skill_profiles_v2.py`    | Aggregate job vectors into role profiles       | JSV + role assignments → `role_skill_profiles_v2.csv`                        |
| `fix_recommendation_pipeline.py`     | Fix seniority-aware role assignment            | JSV → `job_skill_vectors_v2_fixed.csv`                                       |
| `rebuild_enhanced_role_profiles.py`  | Rebuild profiles from fixed vectors            | JSV_fixed → `role_skill_profiles_v2_fixed.csv`                               |
| `build_enhanced_features.py`         | Build 330-dim enhanced features                | JSV + skills → `role_enhanced_profiles.csv`, `enhanced_feature_columns.json` |
| `expand_career_ladders_v2.py`        | Expand ladders from 7→20 domains, 15→173 roles | old ladders + metadata → `career_ladders_v2.json`                            |
| `train_decision_tree_v2.py`          | Train role classifier on 1,147 features        | JSV → `role_classifier_v2.pkl`                                               |
| `regenerate_career_ladders.py`       | Regenerate career ladders                      | profiles → ladders                                                           |
| `generate_role_transitions.py`       | Build role transition CSV                      | ladders → `role_level_transitions.csv`                                       |

### C. Recommendation Pipeline (request → response)

| Step                           | File                          | Function                                                                |
| ------------------------------ | ----------------------------- | ----------------------------------------------------------------------- |
| 1. Request parsing             | `app.py`                      | `recommend_careers(req: RecommendRequest)`                              |
| 2. Skill normalization         | `services/recommender.py`     | `user_skills_upper = set(s.strip().upper() ...)`                        |
| 3. Enhanced vs Legacy decision | `services/recommender.py`     | `_enhanced_available()` + check if any profile fields set               |
| 4a. Enhanced path: user vector | `services/user_vectorizer.py` | `UserVectorizer.create_user_vector()` → 330-dim                         |
| 4b. Legacy path: skill vector  | `services/recommender.py`     | `_build_legacy_user_vector()` → binary over `role_skill_matrix` columns |
| 5. Cosine similarity           | `services/recommender.py`     | `cosine_similarity(user_vector, role_matrix)` against **62 roles**      |
| 6. Skill gap/readiness         | `services/career_service.py`  | `detect_skill_gap()` per role                                           |
| 7. Weighted scoring            | `services/scoring.py`         | `compute_final_score()` — 5 components                                  |
| 8. Ranking                     | `services/recommender.py`     | Sort by `final_match_score` descending                                  |
| 9. Top-N selection             | `services/recommender.py`     | Slice top N, `rank==0` → `is_best_match`                                |
| 10. Explanation                | `services/scoring.py`         | `generate_ranking_explanation()`                                        |
| 11. Career ladder lookup       | `services/career_service.py`  | `get_next_role()`, `get_domain_for_role()`                              |

**Scoring Weights (with domain preference):**

- `skill_match`: 40%
- `domain_preference`: 30%
- `experience_fit`: 15%
- `career_goal_fit`: 10%
- `education_fit`: 5%

**Scoring Weights (no domain preference):**

- `skill_match`: 55%
- `domain_preference`: 10%
- `experience_fit`: 20%
- `career_goal_fit`: 10%
- `education_fit`: 5%

### D. Frontend Components

| Component            | File                                                            | Role                                                              |
| -------------------- | --------------------------------------------------------------- | ----------------------------------------------------------------- |
| Profile Form         | `frontend/src/components/career/CareerProfileForm.jsx`          | 5 dropdowns + skill multi-selector, 21 domain options             |
| Skill Selector       | `frontend/src/components/career/SkillSelector.jsx`              | Loads `data/skills.json`, category grouping, search, multi-select |
| Recommendation Cards | `frontend/src/components/career/CareerRecommendationCard.jsx`   | Match %, readiness %, skill chips, next-step, View Details        |
| Best Match Badge     | (inline in `CareerRecommendationCard.jsx` L62-65)               | Purple badge when `isBestMatch` flag is true                      |
| Career Detail Modal  | `frontend/src/components/career/CareerDetailModal.jsx`          | Full modal with AI explanation, scores, skills lists              |
| Ladder Network       | `frontend/src/components/CareerLadder/CareerLadderNetwork.jsx`  | ReactFlow graph visualization                                     |
| Ladder Timeline      | `frontend/src/components/CareerLadder/CareerLadderTimeline.jsx` | Vertical timeline view                                            |
| Path Comparator      | `frontend/src/components/CareerLadder/CareerPathComparator.jsx` | Side-by-side domain comparison                                    |
| Page Orchestrator    | `frontend/src/pages/CareerPath.jsx`                             | Wires form → API → cards → modal                                  |
| Ladder Page          | `frontend/src/pages/CareerLadderPage.jsx`                       | Ladder visualization page                                         |
| API Layer            | `frontend/src/services/careerApi.js`                            | `getCareerRecommendations`, `getCareerExplanation`                |
| Hooks                | `frontend/src/hooks/useCareerRecommendations.js`                | `useCareerRecommendations`, `useCareerDetail`                     |

---

## PHASE 2 — DATA QUALITY AUDIT

### 1. Skill Coverage

| Metric                                        | Value                          |
| --------------------------------------------- | ------------------------------ |
| Total skills in `skills_v2.csv`               | **1,147** across 22 categories |
| Skill columns in JSV (v2_fixed)               | **1,147**                      |
| Skills mapped to ≥1 job                       | **940** (81.9%)                |
| **Orphan skills** (mapped to 0 jobs)          | **207** (18.1%)                |
| Weakly mapped (1-2 jobs only)                 | **65**                         |
| Skill columns in enhanced profiles            | **300** (only 26.2% of total)  |
| Skills in `skill_columns_v2.pkl` (classifier) | **1,147**                      |

**Category Coverage in 300-dim Enhanced Set:**

| Category       | Total  | In Enhanced 300 | Coverage  |
| -------------- | ------ | --------------- | --------- |
| other          | 228    | 228             | 100%      |
| certification  | 121    | 0               | **0%**    |
| cloud          | 105    | 4               | **3.8%**  |
| devops         | 82     | 7               | **8.5%**  |
| **ai_ml**      | **79** | **0**           | **0%** ❌ |
| backend        | 76     | 18              | 23.7%     |
| frontend       | 57     | 10              | 17.5%     |
| communication  | 55     | 0               | **0%**    |
| database       | 51     | 11              | 21.6%     |
| **security**   | **40** | **0**           | **0%** ❌ |
| mobile         | 40     | 10              | 25%       |
| **leadership** | **40** | **0**           | **0%** ❌ |
| data           | 34     | 0               | **0%**    |
| project_mgmt   | 30     | 0               | **0%**    |
| business       | 24     | 0               | **0%**    |
| **blockchain** | **21** | **0**           | **0%** ❌ |
| **embedded**   | **19** | **0**           | **0%** ❌ |
| **game_dev**   | **18** | **0**           | **0%** ❌ |
| analytics      | 12     | 3               | 25%       |
| fullstack      | 6      | 0               | **0%**    |
| ml_ai          | 5      | 5               | 100%      |
| soft_skill     | 4      | 4               | 100%      |

**Near-Duplicate Skills Found:**

- `SK014` (c) vs `SK251` (c ++)
- `SK185` (elastic search) vs `SK728` (elasticsearch)
- `SK293` (java script) vs `SK002` (javascript)
- `SK016` (security) vs `SK1059` (security+)

### 2. Job Coverage

| Metric                | Value                                                                |
| --------------------- | -------------------------------------------------------------------- |
| Total jobs in JSV     | **15,230**                                                           |
| Unique roles assigned | **62**                                                               |
| Roles with < 5 jobs   | **16** (including INTERN_SE=1, AI_ML_ENGINEER_INT=1, JR_CLOUD_ENG=1) |
| Most common roles     | BE_DEV (2,978), FE_DEV (2,593), MOBILE_DEV (2,329)                   |

**Roles with very few jobs (< 5):**

- `INTERN_SE`: 1 job → profile based on 1 data point
- `AI_ML_ENGINEER_INT`: 1 job → 6 skills total in profile
- `JR_CLOUD_ENG`: 1 job
- `JR_UI_UX_DESIGNER`: 1 job
- `SENIOR_FS_DEV`: 1 job
- `PRINCIPAL_DESIGNER`: 1 job
- `JR_IT_SUPPORT`: 1 job
- `PRINCIPAL_DATA_SCIENTIST`: 1 job
- `PRINCIPAL_ENGINEER`: 2 jobs
- `PRINCIPAL_ML_ENGINEER`: 2 jobs
- `CLOUD_PLATFORM_LEAD`: 2 jobs
- `DATA_ENGINEER_INT`: 2 jobs
- `PROGRAM_MANAGER`: 2 jobs

**Suspicious Generic Skill Problem:**
The `AI_ML_ENGINEER_INT` profile has only 6 skills, including `SK057 (network engineer)`, `SK107 (network)`, `SK132 (networking)`, `SK209 (network administrator)` — these are **networking/sysadmin skills**, not AI/ML skills. This is caused by having only 1 source job with bad tagging.

### 3. Role Coverage

| Metric                                   | Value                               |
| ---------------------------------------- | ----------------------------------- |
| Roles in metadata                        | **175**                             |
| Roles in profiles/JSV                    | **62**                              |
| Roles in enhanced profiles               | **62**                              |
| Roles in ladders                         | **173**                             |
| **Roles in ladders but NOT in profiles** | **111** (64%) ❌                    |
| Roles in profiles but NOT in ladders     | 2 (`JR_IT_SUPPORT`, `JR_SYS_ADMIN`) |

**Domains with ZERO roles in profiles/recommendations:**

| Domain                 | Ladder Roles | In Profiles | Status          |
| ---------------------- | ------------ | ----------- | --------------- |
| **GAME_DEVELOPMENT**   | 8            | **0**       | ❌ Fully absent |
| **BLOCKCHAIN_WEB3**    | 7            | **0**       | ❌ Fully absent |
| **EMBEDDED_SYSTEMS**   | 7            | **0**       | ❌ Fully absent |
| **TECHNICAL_WRITING**  | 6            | **0**       | ❌ Fully absent |
| **PRODUCT_MANAGEMENT** | 9            | **0**       | ❌ Fully absent |
| **BUSINESS_ANALYSIS**  | 7            | **0**       | ❌ Fully absent |

**Domains with severe gaps:**

| Domain                | Ladder Roles | In Profiles | Missing                                                     |
| --------------------- | ------------ | ----------- | ----------------------------------------------------------- |
| SOFTWARE_ENGINEERING  | 14           | 5           | 9 missing (JR_SE, SE_I, TECH_LEAD, etc.)                    |
| AI_ML                 | 10           | 5           | 5 missing (JR_ML_ENGINEER, ML_ENGINEER, AI_ARCHITECT, etc.) |
| DEVOPS_SRE            | 13           | 4           | 9 missing (DEVOPS_ENGINEER, JR_SRE, etc.)                   |
| SECURITY              | 11           | 3           | 8 missing (SECURITY_ANALYST, CISO, etc.)                    |
| DATA_SCIENCE          | 9            | 4           | 5 missing (DATA_SCIENTIST, etc.)                            |
| DATA_ENGINEERING      | 13           | 6           | 7 missing (DATA_ANALYST, etc.)                              |
| QA_TESTING            | 8            | 4           | 4 missing                                                   |
| FULLSTACK_ENGINEERING | 6            | 2           | 4 missing                                                   |
| PROJECT_MANAGEMENT    | 7            | 3           | 4 missing                                                   |

### 4. Ladder Coverage

| Metric                                         | Value                               |
| ---------------------------------------------- | ----------------------------------- |
| Domains                                        | 20                                  |
| Total ladder roles                             | 173                                 |
| Roles with skill profiles (can be recommended) | **62**                              |
| Roles that CANNOT be recommended               | **111**                             |
| Roles with no domain mapping                   | 2 (`JR_IT_SUPPORT`, `JR_SYS_ADMIN`) |

**Critical Ladder Gaps:**

- **AI_ML**: Missing `JR_ML_ENGINEER` and `ML_ENGINEER` — so the ladder jumps from `AI_ML_ENGINEER_INT` (1 job) to `ML_RESEARCH_SCIENTIST`. No mid-level AI/ML role exists in recommendations.
- **GAME_DEVELOPMENT**: ALL 8 roles missing (`JR_GAME_DEV` through `GAME_DIRECTOR`). Zero game dev recommendations possible.
- **BLOCKCHAIN_WEB3**: ALL 7 roles missing.
- **EMBEDDED_SYSTEMS**: ALL 7 roles missing.
- **SOFTWARE_ENGINEERING**: Missing `JR_SE` and `SE_I` — these are the natural entry points. Only `INTERN_SE` (1 job) → `SE_II` exists.
- **DEVOPS_SRE**: Missing `DEVOPS_ENGINEER`, `JR_DEVOPS_ENG`, `JR_SRE` — no entry-level DevOps roles.
- **SECURITY**: Missing `SECURITY_ANALYST` (entry role) and most mid/senior roles.

### 5. Enhanced Feature Dimension Mismatch

**Critical Issue:** The enhanced feature system uses only **300 skill dimensions** while the data has **1,147 skills**.

The `build_enhanced_features.py` script was run on the original ~300-skill dataset **before** the skill expansion to 1,147. It was **never rebuilt** after expansion.

This means:

- 847 skills (74%) are **invisible** to the enhanced cosine similarity engine
- All `ai_ml`, `game_dev`, `blockchain`, `security`, `cloud`, `devops`, `embedded`, `certification` skills (except 5 ml_ai) are NOT in the 300-dim vector
- Users selecting these skills get **zero signal** in the enhanced path

### 6. Enhanced Domain Values Mismatch

**Only 7 domain values** in enhanced features: `SOFTWARE_ENGINEERING, DATA, AI_ML, DEVOPS, QA, MOBILE, UI_UX`

But the **frontend offers 21 domains** and **ladders have 20 domains**. Missing from enhanced:

- `FRONTEND_ENGINEERING`, `BACKEND_ENGINEERING`, `FULLSTACK_ENGINEERING`
- `CLOUD_ENGINEERING`, `SECURITY`
- `PRODUCT_MANAGEMENT`, `BUSINESS_ANALYSIS`, `PROJECT_MANAGEMENT`
- `TECHNICAL_WRITING`, `BLOCKCHAIN_WEB3`, `GAME_DEVELOPMENT`, `EMBEDDED_SYSTEMS`
- `DATA_ENGINEERING` (separate from `DATA`)

When a user picks one of these 13 missing domains, the domain one-hot dimension is all-zeros — no domain signal in cosine similarity.

---

## PHASE 3 — FAILURE ANALYSIS

### Root Cause 1: **111 roles in ladders have NO profile data (SEVERITY: CRITICAL)**

**Impact:** 64% of all ladder roles cannot be recommended, matched, or scored. Entire domains (Game Dev, Blockchain, Embedded, Tech Writing, Product Management, Business Analysis) are dead.

**Why:** The role profiles and JSV are built from real scraped job data. These domains had no jobs scraped, or jobs were not assigned to these role IDs.

### Root Cause 2: **Enhanced vectors use only 300/1,147 skills (SEVERITY: CRITICAL)**

**Impact:** When the user provides profile fields (experience, status, domain, etc.), the system uses the enhanced 330-dim path. In this mode, **847 skills (74%) are invisible** — including ALL ai_ml, game_dev, blockchain, security, cloud, devops, embedded, and certification skills.

A user selecting TensorFlow, PyTorch, Unity, or Kubernetes gets zero signal from those skills in enhanced mode. Only in legacy mode (no profile fields) do all 1,147 skills participate through `role_skill_matrix`.

**But even in legacy mode**, cosine similarity is against the `role_skill_matrix` which is built from role profiles — and those only cover 62 roles. The legacy mode uses all 1,147 skill columns because `role_skill_matrix` is pivoted from `role_skill_profiles_v2_fixed.csv` which does reference 1,147 skills, but only for those 62 roles.

### Root Cause 3: **No core-skill gate on recommendations (SEVERITY: HIGH)**

**Impact:** A job can be recommended even when the user has NONE of the core skills. The system ranks by cosine similarity + weighted scoring, but never checks "does this user have at least N% of the defining skills for this role."

Example: A user with only HTML/CSS skills could get recommended for `ML_RESEARCH_SCIENTIST` if the domain preference and experience scores happen to push it up.

### Root Cause 4: **Entry-level roles have very few jobs, tiny profiles (SEVERITY: HIGH)**

**Impact:** `INTERN_SE` has 1 job and 6 skills. `AI_ML_ENGINEER_INT` has 1 job and 6 skills (including networking skills, not AI skills). These profiles are statistically unreliable and produce random matches.

A student selecting "student" experience + "first_job" goal relies on these sparse profiles to get intern/JR recommendations. The `experience_fit` scoring does boost JR/INTERN roles, but if those profiles have bad skill signals, the boost still lands on wrong roles.

### Root Cause 5: **Domain values mismatch between enhanced features (7) and system (20) (SEVERITY: HIGH)**

**Impact:** 13 of 20 domains get zero signal in the enhanced one-hot dimension. Users selecting "backend_engineering", "cloud_engineering", "frontend_engineering" etc. get no domain cosine boost from the enhanced vector — only from post-hoc weighted scoring (which is domain_preference_score at 30%).

But the 30% domain_preference_score uses string matching, not vector similarity, so it partially compensates. However, the skill similarity (40%) is damaged because the enhanced role profiles only reflect 300 skills.

### Root Cause 6: **AI/ML roles have profile quality issues (SEVERITY: HIGH)**

**Impact:**

- `AI_ML_ENGINEER_INT` profile: 6 skills, 4 of which are networking skills (not AI/ML)
- `ML_RESEARCH_SCIENTIST` is the only strong AI/ML profile (238 skills) but it's a research role, not a general ML engineer
- `JR_ML_ENGINEER` and `ML_ENGINEER` (the natural interns/mid-level) are in the ladder but have NO profile data
- AI-specific skills (tensorflow, pytorch, keras, langchain, etc.) are in the 1,147-skill set but NOT in the 300-dim enhanced features

Result: Even when a user selects all AI/ML skills + AI_ML domain, the system has very poor role profiles to match against.

### Root Cause 7: **Game Development is completely dead (SEVERITY: HIGH)**

**Impact:** Zero game dev roles in profiles, zero game dev skills in enhanced features, all 8 ladder roles missing from data. A user selecting Unity, Unreal Engine, game design → gets zero relevant recommendations.

### Root Cause 8: **Career ladder gaps create unrealistic next-steps (SEVERITY: MEDIUM)**

**Impact:** When a role's next-step in the ladder doesn't have profile data, `get_next_role()` returns a role_id that has no skill profile. The frontend can display a "Next Step" badge with a role that can't actually be matched or analyzed.

### Root Cause 9: **Readiness is based on importance threshold 0.02 (very low) (SEVERITY: MEDIUM)**

**Impact:** With threshold=0.02, nearly ALL skills for a role are considered "required." This inflates the number of "missing skills" and deflates readiness scores. A more realistic threshold (e.g., 0.1 or 0.15) would focus on truly important skills.

### Root Cause 10: **Match score conflates skill similarity with profile scoring (SEVERITY: MEDIUM)**

**Impact:** The `match_score` displayed to users is `final_match_score` which blends skill_match (40%) with domain, experience, goal, and education scores. A user could see "75% match" when their actual skill overlap is only 25% — the rest is domain and experience fit. This is misleading.

---

## PHASE 4 — SUMMARY & IMPLEMENTATION PLAN

### Root Causes Ranked by Severity

| #   | Root Cause                                        | Severity     | Affected Areas                                                                                |
| --- | ------------------------------------------------- | ------------ | --------------------------------------------------------------------------------------------- |
| 1   | 111/173 ladder roles have no profile data         | **CRITICAL** | 6 entire domains dead, most domains partially broken                                          |
| 2   | Enhanced vectors use 300/1,147 skills             | **CRITICAL** | AI/ML, Game Dev, Security, Cloud, DevOps, Blockchain, Embedded all invisible in enhanced mode |
| 3   | No core-skill gate on recommendations             | HIGH         | Wrong roles recommended for skill-poor users                                                  |
| 4   | Entry-level roles have tiny/bad profiles          | HIGH         | Students/interns get poor recommendations                                                     |
| 5   | Domain values mismatch (7 vs 20)                  | HIGH         | 13 domains get no enhanced vector signal                                                      |
| 6   | AI/ML profile quality issues                      | HIGH         | AI/ML recommendations unreliable                                                              |
| 7   | Game Dev completely dead                          | HIGH         | No game dev recommendations possible                                                          |
| 8   | Career ladder next-step points to missing roles   | MEDIUM       | Misleading UI                                                                                 |
| 9   | Readiness threshold too low (0.02)                | MEDIUM       | Deflated readiness scores                                                                     |
| 10  | Match score blends skill fit with profile scoring | MEDIUM       | Misleading match percentages                                                                  |

### Live Data Files Being Used

1. `career-ml/data/expanded/skills_v2.csv` — 1,147 skills ✅
2. `career-ml/data/processed/job_skill_vectors_v2_fixed.csv` — 15,230 jobs × 1,147 skills × 62 roles ✅
3. `career-ml/data/processed/role_skill_profiles_v2_fixed.csv` — 62 roles ✅
4. `career-ml/data/processed/career_ladders_v2.json` — 20 domains, 173 roles ⚠️ (111 hollow)
5. `career-ml/data/processed/role_metadata.json` — 175 role titles ✅
6. `career-ml/models/role_classifier_v2.pkl` — Decision tree (1,147 features, 62 classes) ✅
7. `career-ml/models/skill_columns_v2.pkl` — 1,147 column names ✅
8. `career-ml/data/processed/role_enhanced_profiles.csv` — 62 roles × 330 dims ⚠️ (only 300 skills)
9. `career-ml/data/processed/enhanced_feature_columns.json` — 300 skills + 30 onehot ⚠️ (stale)
10. `career-ml/data/processed/jobs_enhanced_features.csv` — 5,470 jobs ✅
11. `career-ml/career_path/career_ladders_enhanced.json` — Enhanced ladder detail (for ladder endpoints)

### Exact Files to Inspect/Change

**Data Generation (must regenerate):**

- `career-ml/scripts/build_enhanced_features.py` — Needs to use 1,147 skills and 20 domains
- `career-ml/scripts/expand_career_ladders_v2.py` — May need to synthesize profiles for missing roles
- New script needed: Generate synthetic role profiles for 111 missing ladder roles

**Pipeline Code (needs changes):**

- `career-service/services/recommender.py` — Add core-skill gate, fix enhanced/legacy path
- `career-service/services/scoring.py` — Adjust match_score transparency, readiness threshold
- `career-service/services/user_vectorizer.py` — Update to handle 1,147 skills and 20 domains
- `career-service/services/career_service.py` — Handle missing-profile roles gracefully
- `career-service/data_loader.py` — Validate enhanced profile dimensions match current skills
- `career-service/config.py` — May need new config for tuning parameters

**Frontend (minor changes):**

- `frontend/src/components/career/CareerRecommendationCard.jsx` — Display skill_match_score separately
- `frontend/src/components/career/CareerDetailModal.jsx` — Show score breakdown more transparently

### Proposed Phased Implementation Plan

#### Phase 1: Rebuild Enhanced Features (Data Layer Fix)

**Goal:** Align enhanced vectors with current 1,147-skill set and 20 domains

1. Rewrite `build_enhanced_features.py` to use all 1,147 skill columns + 20 domain values
2. Regenerate `enhanced_feature_columns.json` (1,147 skills + expanded onehot)
3. Regenerate `role_enhanced_profiles.csv` with new dimensions
4. Update `UserVectorizer` to match new dimensions
5. Test: Enhanced recommendations should now see all skills

#### Phase 2: Generate Missing Role Profiles (Data Gap Fix)

**Goal:** Provide skill profiles for the 111 missing ladder roles

1. Create script to generate synthetic role profiles by:
   - Inheriting skills from adjacent roles in same ladder (e.g., JR_ML_ENGINEER inherits from AI_ML_ENGINEER_INT + ML_RESEARCH_SCIENTIST)
   - Adding domain-defining skills from skill categories
   - Calibrating importance weights based on seniority level
2. Merge synthetic profiles into `role_skill_profiles_v2_fixed.csv`
3. Rebuild `role_enhanced_profiles.csv` with all 173 roles
4. Retrain classifier (optional — synthetic data may reduce accuracy)

#### Phase 3: Core-Skill Gate & Scoring Fixes (Pipeline Fix)

**Goal:** Prevent skill-poor matches and improve entry-level routing

1. Add minimum skill overlap check in `recommender.py` — roles with < 5% core skill match get filtered out or heavily penalized
2. Raise importance threshold from 0.02 to 0.10 for readiness calculation
3. Add separate `skill_match_display` score (pure skill overlap) vs `final_match_score` (weighted)
4. Improve entry-level routing: when experience="student" or career_goal="first_job", add stronger seniority filtering
5. Fix `AI_ML_ENGINEER_INT` profile (remove networking skills, add core AI skills)

#### Phase 4: Domain & Ladder Integrity (Consistency Fix)

**Goal:** Fix domain mismatches and ladder gaps

1. Update enhanced feature domain values from 7 to match the 20 ladder domains
2. Add ladder validation: `get_next_role()` should check if next role has a profile
3. Update career_ladders_enhanced.json to include all roles with profile data
4. Ensure all frontend domain options map to real data

#### Phase 5: Frontend Transparency (Display Fix)

**Goal:** Show users honest scores

1. Display `skill_match_score` alongside `match_score` on cards
2. Add tooltip explaining what match_score includes
3. Show warning when a domain has limited data
4. Handle "no recommendations found" gracefully for dead domains
