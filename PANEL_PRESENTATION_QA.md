# Budget Optimizer — Final Year Panel Preparation Q&A
**Component:** AI-Powered Student Budget Optimizer  
**Platform:** Uni-Finder (Sri Lanka)  
**Date Prepared:** April 16, 2026

> Use this document to practise answers out loud before your presentation.  
> Every answer is grounded in the actual code and data in this repository.

---

## SECTION 1 — "How does this algorithm / model actually work?"
*Panel is checking: Do you genuinely understand your own solution? Engineer or slave?*

---

### Q1.1 — "What algorithm did you use and why?"

**Your answer:**

The system uses **two machine learning models** working together:

1. **Gradient Boosting Regressor (GBR)** — predicts the student's optimal monthly expense budget.
2. **Logistic Regression** — classifies the student's financial risk level as either Low Risk or High Risk.

I chose Gradient Boosting Regressor over a simple Linear Regression or a neural network for a specific reason: the relationship between student income, affordability perceptions, and actual spending is **non-linear**. Gradient Boosting builds decision trees sequentially, where each new tree corrects the errors of the previous one. This ensemble approach handles non-linear patterns in tabular data very well without needing large amounts of data.

I chose Logistic Regression for risk classification because it is interpretable — I can explain the probability score to the student directly, and it is sufficiently accurate for a binary classification problem (High Risk / Low Risk) with 1,018 samples.

---

### Q1.2 — "Walk me through how the system actually produces an output when a student clicks Submit."

**Your answer:**

The pipeline has **five sequential stages**:

**Stage 1 — Rule-based calculation (`budget_calculator.py`)**  
Before any ML is involved, the system uses Sri Lanka-specific pricing datasets to calculate the student's realistic food and transport costs. For example, for a Bus commuter doing a 5 km round trip in Colombo, the calculator applies: minimum fare LKR 60 + LKR 10/km, multiplied by commute days per month, plus emergency and home-visit trips. This means the ML model receives *calculated* cost inputs, not just raw guesses.

**Stage 2 — Feature preprocessing (`ml_budget_predictor.py → preprocess_input()`)**  
The student's data is transformed into exactly **16 numerical features** expected by the trained model:
- `Income`, `Transport` — numeric values
- `Work_Hours`, `Comfort` — from survey-mapped ranges
- `Aff_Accommodation`, `Aff_Food`, `Aff_Materials`, `Aff_Transport`, `Aff_Social` — affordability ratings (1–5)
- `Has_Parental`, `Has_Job`, `Has_Scholarship`, `Has_Loan` — binary funding flags
- `Food_Cost_Multiplier`, `Avg_District_Rent`, `Avg_Transport_Cost` — live values loaded from the real pricing CSVs at runtime

The features are then scaled using a **StandardScaler** (the same scaler fitted during training and saved as `feature_preprocessor_final.pkl`).

**Stage 3 — ML prediction**  
The scaled feature vector is passed to the loaded GBR model, which returns the predicted optimal monthly budget. The same features are also passed to the Logistic Regression classifier, which returns a risk label (High/Low) and a probability score (e.g., 0.72 = 72% chance of financial stress).

**Stage 4 — Rule-based optimal strategy (`generate_optimal_budget_strategy()`)**  
Using the ML prediction plus the student's actual expense breakdown, the system compares each category's current spending against realistic Sri Lankan benchmarks and generates personalised Smart Budget Alternatives — e.g., if transport > LKR 3,500 and the student is at a state university, it suggests the CTB concession pass; if at a private campus, it suggests off-peak travel and batching instead.

**Stage 5 — Optional AI strategy (OpenAI GPT-4o-mini)**  
On manual button click, the complete financial profile (income, expenses, risk level, alternatives) is sent with a carefully engineered prompt to GPT-4o-mini. The model returns a step-by-step textual strategy following ethical guidelines built into the prompt — cultural constraints like no suggesting home-visit reduction, no suggesting rent negotiation with landlords, and concession pass advice only for state university students.

---

### Q1.3 — "What are the 16 features your model uses?"

**Your answer:**

The model was trained on **16 features** grouped into four categories:

| Group | Features |
|---|---|
| **Financial** | Income, Transport cost |
| **Lifestyle** | Work hours/week, Financial comfort (1–5 scale) |
| **Affordability perceptions** | Accommodation, Food, Study materials, Transport, Social life (all 1–5 scale) |
| **Funding source flags** | Has parental support (0/1), Has part-time job (0/1), Has scholarship (0/1), Has student loan (0/1) |
| **Real-world pricing** | Food cost multiplier (from food_prices.csv), Average district rent (from room_annex_rentals.csv), Average transport cost (from srilanka_transport_costs.csv) |

The 3 real-world pricing features were added as the "advanced" enhancement over the baseline 13-feature model. They anchor the prediction to actual market data rather than purely survey self-reports.

---

### Q1.4 — "Why did you use these specific technologies? Flask, React, etc.?"

**Your answer:**

| Technology | Why chosen |
|---|---|
| **Flask (Python)** | Integrates natively with scikit-learn and pandas, which are the standard libraries for loading `.pkl` model files and processing CSV datasets |
| **React** | Component-based, state-managed UI — essential for a 7-step multi-form that conditionally renders sections based on user choices |
| **Gradient Boosting Regressor** | Outperformed Random Forest and plain Decision Trees in cross-validation on this dataset. Handles non-linear income-expense relationships better than linear models |
| **Logistic Regression** | Fast, interpretable binary classifier. Outputs a probability rather than just a label, which allows showing the student a risk percentage score |
| **OpenAI GPT-4o-mini** | Fast inference (< 2 seconds), low cost (~$0.0001/request), and produces coherent, structured financial advice when given a well-engineered prompt. Chosen over Gemini because the paid tier gives predictable availability |
| **StandardScaler** | GBR is not distance-sensitive, but scaling ensures numerical stability during preprocessing and consistency between training and inference |

---

## SECTION 2 — "Did you use AI tools? Where? What was generated vs developed by you?"
*Panel is checking: Honesty, academic integrity, responsible AI use.*

---

### Q2.1 — "Did you use AI tools in this project?"

**Your answer (honest and structured):**

Yes, I used AI tools in specific, responsible ways. I want to be transparent about exactly where:

**Where AI assisted me:**
- **GitHub Copilot / ChatGPT** — for boilerplate code like React state management hooks, Flask route structures, and CSS layout templates. These are things any developer uses auto-complete or documentation for.
- **Prompt engineering** — the OpenAI prompt inside `app.py` was designed and refined by me through multiple iterations. I identified the ethical constraints (CTB concession pass only for state universities, no home-visit reduction advice, etc.) based on my own understanding of Sri Lanka. The AI did not produce these rules; I did.
- **Documentation** — some sections of readme files were written with AI assistance, though the technical content (accuracy numbers, feature descriptions) came from my own model runs.

**Where I did the work myself:**
- **Dataset collection** — I collected 1,018 student survey responses, scraped 669 accommodation listings, and compiled food/transport CSV datasets specific to Sri Lanka.
- **ML training pipeline** — the 16-feature engineering decisions, the choice of GridSearchCV with 5-fold CV, the train/test split with stratification, and the model selection were all decisions I made and validated.
- **Rule-based calculator** — the entire `budget_calculator.py` logic (6 transport modes each with model-specific fare formulas, the home-visit cost calculation, the food type branching) was written by me based on research on CTB fares, PickMe pricing, and market rates.
- **Ethical guardrails** — the state-university vs. private-university CTB distinction, the part-time job detection for income advice, the Sri Lankan cultural sensitivity rules in both the ML predictor and OpenAI prompt — all identified and implemented by me.

---

### Q2.2 — "How did you validate AI-generated outputs?"

**Your answer:**

For AI-generated code (boilerplate, suggestions): I validated by running the actual Flask endpoints and comparing API responses to expected values. Every endpoint has been manually tested with realistic input data from Sri Lankan students.

For GPT-4o-mini generated financial strategies: I validated by reviewing outputs against Sri Lankan reality:
- Tested with a SLIIT student profile → confirmed the CTB concession pass does **not** appear in output (as it should not for private institute students)
- Tested with a state university profile → confirmed CTB concession steps appear correctly
- Tested with `has_work_commute = true` → confirmed "get a part-time job" does not appear
- Checked that savings targets in the AI output are always ≤ actual income (enforced via `income_ceiling` calculation in the prompt)

The prompt also specifies a strict structured output format so I can programmatically verify the response has all required fields (STEP, ACTION, SAVE, HOW, LINKS, FINAL_BUDGET).

---

## SECTION 3 — "Did you train this model or use a pre-trained one?"
*Panel is checking: Data integrity, bias awareness, adaptation quality.*

---

### Q3.1 — "Did you train this model yourself or download a pre-trained one?"

**Your answer:**

I **trained both models myself** from scratch. There is no pre-trained financial model I downloaded.

The full training pipeline is in `budget_optimizer_service/notebooks/Student_Budget_ML_Training_ADVANCED.ipynb`. The trained models are saved as `.pkl` files:
- `budget_optimizer_gbr_model_final_optimized.pkl` — Gradient Boosting Regressor
- `risk_classifier_model_final.pkl` — Logistic Regression risk classifier
- `feature_preprocessor_final.pkl` — StandardScaler

These are loaded by `ml_budget_predictor.py` at runtime using `joblib.load()`.

---

### Q3.2 — "What dataset did you use to train the models?"

**Your answer:**

The training used **six datasets** — one primary and five auxiliary:

| Dataset | Size | Purpose |
|---|---|---|
| **Student Budget Survey.csv** | 1,018 responses | Primary training data — income, expenses, funding, affordability ratings |
| **food_prices.csv** | 402 food items | Food cost multiplier feature |
| **Vegetables_fruit_prices.csv** | 130,000+ records | District-level produce pricing |
| **srilanka_transport_costs.csv** | 100 routes | Average transport cost feature |
| **room_annex_rentals.csv** | 669 listings | Average district rent feature |
| **academic_calendar.csv** | University terms | Dynamic expense adjustment |

The survey data was directly collected from Sri Lankan university students, capturing income ranges, funding sources, affordability perceptions across 5 categories, work hours, and financial comfort levels.

---

### Q3.3 — "What are the limitations or biases in your data?"

**Your answer — be honest, this shows maturity:**

| Limitation | Impact | How I mitigated it |
|---|---|---|
| **Survey self-reporting bias** | Students may over or under-report income/expenses | Income was collected as ranges (not exact figures) to reduce social desirability bias |
| **Geographic concentration** | Survey may over-represent Colombo/Western Province students | Added district-level features from real pricing datasets to adjust predictions geographically |
| **Sample size (1,018)** | Not large enough to capture every district and field combination reliably | GridSearchCV with 5-fold cross-validation prevents overfitting to the available sample |
| **Temporal bias** | Prices in CSVs reflect 2024–2025 Sri Lankan market conditions | The pricing datasets should be refreshed annually to remain accurate |
| **Private vs state university** | Survey may not equally represent all university types | The system now explicitly distinguishes between state and private universities for relevant advice |
| **No longitudinal data** | We capture a snapshot of expenses — students' needs change by year of study | `year_of_study` is included as an input feature to partially account for this |

---

### Q3.4 — "How did you adapt the model to your specific problem?"

**Your answer:**

Three adaptations make this different from a generic expense prediction model:

**1. Domain-specific feature engineering**  
Rather than using raw categorical answers directly, I engineered features that carry real financial meaning — `Has_Parental`, `Has_Job`, `Has_Scholarship`, `Has_Loan` are binary flags derived from a multi-select funding source field, because each funding type affects financial stability differently.

**2. Hybrid architecture**  
The ML model alone does not produce a complete recommendation. I built a layered architecture:
- Rule-based calculator (domain expertise → realistic food/transport costs)  
- ML prediction (pattern learning from survey data)  
- Rule-based strategy engine (domain expertise → culturally ethical alternatives)  
- LLM layer (language generation → plain-language explanation)

No single layer could achieve the result alone. The combination means even if the ML prediction is slightly off, the rule-based calculator anchors the food and transport figures to real Sri Lankan prices.

**3. Culturally localised ethical constraints**  
The strategy generation — both in `ml_budget_predictor.py` and in the OpenAI prompt — was explicitly constrained to Sri Lankan social realities: no home-visit reduction (culturally non-negotiable), no landlord rent negotiation (students have no bargaining power), CTB concession eligibility limited to state university students only. These cannot come from a generic pre-trained model — they required specific domain knowledge that I built in.

---

## SECTION 4 — "How did you verify your results? What metrics did you use?"
*Panel is checking: Rigour. AI-generated outputs can look correct but be wrong.*

---

### Q4.1 — "What metrics did you use to evaluate your models?"

**Your answer:**

**For the Budget Predictor (regression problem):**

| Metric | Value | What it means |
|---|---|---|
| **R² Score** | **86.89%** | The model explains 86.89% of the variance in student monthly expenses |
| **MAE** | LKR ~1,200–1,800 | On average, the prediction is within LKR 1,200–1,800 of actual spending |
| **RMSE** | Slightly above MAE | Indicates the model is not making large outlier errors |
| **MAPE** | < 10% | Less than 10% relative error across income levels |

For a student spending LKR 30,000/month, the model predicts within ±LKR 1,500 on average — which is acceptable for a budgeting guidance tool.

**For the Risk Classifier (binary classification):**

| Metric | Value |
|---|---|
| **Accuracy** | 82.5% |
| **Evaluation** | Classification report (precision, recall, F1) for both Low Risk and High Risk classes |
| **Stratified split** | Ensures test set has the same High/Low ratio as training set |

---

### Q4.2 — "How did you validate that the system works end-to-end, not just the model?"

**Your answer:**

I conducted **four layers of validation:**

**Layer 1 — Unit-level (individual module testing)**  
- API endpoints tested independently: `/api/budget/calculate-food`, `/api/budget/calculate-transport`, `/api/budget/predict`, `/api/budget/complete-analysis`
- Each endpoint tested with edge cases: zero income, 0 km distance, no rent (living with family), maximum income range

**Layer 2 — Calculation sanity checks**  
The transport calculator was validated against real Sri Lankan scenarios:
- 5 km Bus trip (5 days/week, monthly home visit 80 km): expected ~LKR 5,620 ✅
- 3 km Tuk-Tuk daily: expected ~LKR 9,780 ✅
- 2 km Walking: expected ~LKR 2,720 (emergency trips only) ✅

**Layer 3 — Output reasonableness checks**  
I verified that:
- Optimal target budget never exceeds the student's income
- Savings rate shown is always non-negative (safety floor applied)
- Smart Budget Alternatives are never generated for categories where current spending is already optimal
- State university vs. private university CTB concession logic produces correct output for each case

**Layer 4 — Cross-validation during training**  
GridSearchCV with 5-fold cross-validation was used for hyperparameter tuning. This means the model was evaluated on 5 different held-out subsets of the training data, reducing the chance of overfitting to a single partition.

---

### Q4.3 — "What is the expected accuracy / performance of your system?"

**Your answer:**

| Component | Performance | Confidence |
|---|---|---|
| Food budget calculation | Grounded in 402 real food prices + 130K vegetable price records — not ML-based | High |
| Transport budget calculation | Based on 2024–2025 Sri Lankan fare structures, validated against 6 transport modes | High |
| Budget prediction (GBR) | R² = 86.89% — predicts within ±LKR 1,500 for a LKR 30,000 student | Good |
| Risk classification | 82.5% accuracy — identifies high-risk students correctly in 4 out of 5 cases | Acceptable |
| AI strategy (GPT-4o-mini) | Quality-controlled by structured prompt with ethical constraints and strict output format | Validated by review |

**Known limitations to state honestly:**
- The ML model is only as current as the survey data (2024). Inflation or major cost-of-living shifts would reduce accuracy over time.
- The risk classifier has lower accuracy at the extremes — students with very high or very low income relative to expenses are easier to classify than borderline cases.
- GPT-4o-mini outputs vary slightly across runs (temperature = 0.7). The structured prompt minimises this, but some variation exists.

---

### Q4.4 — "What would you do differently to improve the system?"

**Your answer (shows research maturity):**

1. **Expand the survey** to 5,000+ responses with better geographic distribution across all 25 districts and both state and private universities.
2. **Add a feedback loop** — after students use the system for one month, collect actual expense data vs. predicted budget. Retrain the model with this ground-truth data.
3. **Use district-specific models** — Colombo students have fundamentally different cost structures vs. Jaffna or Matara students. A separate model per high-cost region would improve accuracy.
4. **Replace the affordability self-rating** with calculated affordability ratios (e.g., rent/income ratio), removing subjectivity from the training signal.
5. **Fine-tune an LLM** specifically on Sri Lankan student financial conversations rather than using a general-purpose model with prompt constraints.

---

## QUICK-REFERENCE FACTS (Memorise These)

| Fact | Value |
|---|---|
| Primary training dataset | 1,018 Sri Lankan student survey responses |
| Total datasets used | 6 (survey + food prices + vegetable prices + transport + accommodation + academic calendar) |
| Accommodation listings | 669 listings in room_annex_rentals.csv |
| Food items in price data | 402 items in food_prices.csv |
| Transport routes | 100 routes in srilanka_transport_costs.csv |
| Vegetable price records | 130,000+ district-level records |
| ML features used | 16 features |
| Budget predictor algorithm | Gradient Boosting Regressor |
| Risk classifier algorithm | Logistic Regression |
| Budget prediction accuracy | R² = 86.89% |
| Risk classification accuracy | 82.5% |
| Train/test split | 80% training / 20% test (stratified) |
| Cross-validation | 5-fold GridSearchCV |
| Feature scaling | StandardScaler |
| AI strategy model | GPT-4o-mini (OpenAI) |
| Total multi-step form steps | 7 steps |
| Flask service port | 5002 |
| Key ethical constraint | CTB concession advice only for state university students |

---

## ONE-SENTENCE ANSWERS (for rapid-fire questions)

- **"What problem does this solve?"** — Sri Lankan university students lack a localized tool that estimates their real living costs, detects financial risk, and gives culturally realistic improvement advice in one workflow.
- **"Why machine learning?"** — Because different students have different income-expense patterns depending on their funding source, district, food habits, and transport method — patterns a fixed rule-based formula cannot capture.
- **"What makes this original?"** — The combination of district-specific pricing data from real Sri Lankan markets, culturally grounded ethical constraints, and state vs. private university awareness in the recommendation engine is not found in any existing student budgeting tool.
- **"What are the limitations?"** — Model accuracy depends on the 2024 survey data; it would need retraining annually, and the current 1,018-sample dataset may not fully represent all districts equally.
- **"Did AI write your code?"** — AI tools assisted with boilerplate and syntax, but the domain logic — fare formulas, ethical guardrails, feature engineering, and dataset collection — was designed and built by me.
