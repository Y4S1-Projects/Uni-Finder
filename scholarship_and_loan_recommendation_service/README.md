## Scholarship & Loan Recommendation Service

This folder contains the standalone **Scholarship & Loan Matcher** ML service, exposed as a **FastAPI** app.
It powers the scholarship/loan matcher UI in the frontend and can be deployed independently of the Node backend.

---

### 1. Architecture overview

- **Service type**: Python FastAPI microservice
- **Default port**: `5005`
- **Package / module**: `scholarship_loan_matcher_ml`
- **Entry point**: `scholarship_loan_matcher_ml/api_service.py`
- **Core engine**: `scholarship_loan_matcher_ml.matcher.match_engine.match_profile`
- **Data**:
  - Cleaned datasets in `scholarship_loan_matcher_ml/processed_data/`
  - Raw data + training scripts in `scholarship_loan_matcher_ml/raw_data/` and `scholarship_loan_matcher_ml/training/`

The service exposes a simple HTTP API (`/match`) which wraps the existing ML pipeline and is designed to be called directly
from the React frontend (or any other client).

---

### 2. Prerequisites

- **Python**: 3.10+ recommended (3.11/3.12/3.13 are fine)
- **pip**: latest version
- **OS**: Windows, macOS, or Linux

You should run this service in a **virtual environment** to keep dependencies isolated from your system Python.

---

### 3. Install & set up

From the project root, switch into the service folder:

```bash
cd scholarship_and_loan_recommendation_service
```

#### 3.1 Create and activate a virtual environment

On **Windows (PowerShell)**:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

On **macOS / Linux**:

```bash
python -m venv .venv
source .venv/bin/activate
```

#### 3.2 Install dependencies

With the virtual environment activated:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

`requirements.txt` includes:

- `fastapi`, `uvicorn[standard]`
- `numpy`, `pandas`, `scikit-learn`, `joblib`
- `python-dotenv`

---

### 4. Running the FastAPI service

There are two supported ways to start the service.

#### Option A (recommended): run as a module

From `scholarship_and_loan_recommendation_service` with the venv active:

```bash
python -m scholarship_loan_matcher_ml.api_service
```

Output should look similar to:

```text
Uvicorn running on http://0.0.0.0:5005 (Press CTRL+C to quit)
Application startup complete.
```

#### Option B: run the script directly

```bash
cd scholarship_and_loan_recommendation_service
.\.venv\Scripts\activate   # or `source .venv/bin/activate` on macOS/Linux
cd scholarship_loan_matcher_ml
python api_service.py
```

The service will still bind to port **5005** by default.

#### 4.1 Health check

Once running, verify the service with:

- `GET http://127.0.0.1:5005/health`

You should receive:

```json
{ "status": "ok", "service": "scholarship-loan-matcher" }
```

---

### 5. API specification

#### 5.1 `POST /match`

Runs the scholarship & loan matcher for a given student profile.

- **URL**: `http://127.0.0.1:5005/match`
- **Method**: `POST`
- **Request body (JSON)**:

```json
{
  "profile": {
    "education_level": "Undergraduate",
    "field_of_study": "Computer Science",
    "family_income": "Low",
    "district": "Colombo",
    "age": 21,
    "study_interests": "AI, data science",
    "career_goals": "Machine learning engineer",
    "extracurriculars": "hackathons, coding clubs",
    "desired_program_type": "scholarship",
    "skills": ["python", "machine learning"]
  },
  "top_n": 5,
  "match_type": "scholarship"
}
```

- `profile`: free-form student profile; more detail → better matching.
- `top_n`: number of results to return (default: 5).
- `match_type`:
  - `"scholarship"` – only scholarship results
  - `"loan"` – only loan results
  - `null` / omitted – combined results.

**Response (200 OK)**:

```json
{
  "matches": [
    {
      "name": "Example Scholarship",
      "record_type": "scholarship",
      "final_score": 0.91,
      "similarity_score": 0.88,
      "rule_score": 0.96,
      "eligibility_status": "eligible",
      "eligibility_reasons": {
        "passed": ["Field of study matches", "..."],
        "failed": []
      },
      "...": "other fields from the dataset"
    }
  ],
  "count": 1
}
```

**Error responses**:

- `400 Bad Request` – invalid or empty profile (e.g. missing text fields).
- `500 Internal Server Error` – unexpected failure inside the ML pipeline.

The error payload will include a `detail` field with a human-readable message.

---

### 6. Frontend integration

The React frontend talks directly to this FastAPI service via the `scholarship_loan_matcher/api.js` helper.

In `frontend/.env`:

```env
REACT_APP_SCHOLARSHIP_MATCHER_URL=http://127.0.0.1:5005
REACT_APP_BACKEND_URL=http://localhost:5000
```

Key points:

- `REACT_APP_SCHOLARSHIP_MATCHER_URL` points **directly** to this FastAPI service.
- If this variable is missing, the frontend falls back to calling the Node backend route (`/api/scholarships/match`).
- After changing `.env`, restart the React dev server so env vars are applied.

On the frontend, `requestMatches(profile, { topN, matchType })` will:

- Send `POST /match` to `REACT_APP_SCHOLARSHIP_MATCHER_URL`.
- Pass through the `profile` and `matchType` fields expected by this service.
- Return the `matches` array back to the UI.

---

### 7. Dataset update pipeline (optional)

The ML engine relies on cleaned CSVs stored under `scholarship_loan_matcher_ml/processed_data/`.
There is a separate **update pipeline** (scraping, cleaning, merging) implemented in:

- `scholarship_loan_matcher_ml/pipeline/update_pipeline.py`
- `scholarship_loan_matcher_ml/pipeline/get_stats.py`

These scripts are typically triggered by the Node backend via `updateDatasetController.js`, but they can also be run
manually from this folder if needed (for example, to refresh data before deployment).

Example (manual run, from `scholarship_and_loan_recommendation_service`):

```bash
.\.venv\Scripts\activate
python -m scholarship_loan_matcher_ml.pipeline.update_pipeline
```

Refer to code comments in those pipeline modules for more detail on the end-to-end data refresh process.

---

### 8. Deployment notes

- **Separate service**: this FastAPI app can be deployed as an independent container or process.
- **Port configuration**:
  - Default: `PORT=5005`
  - Override by setting the `PORT` environment variable before starting the service.
- **CORS**:
  - Allowed origins are controlled by the `CORS_ORIGINS` environment variable.
  - If unset, it defaults to common local dev URLs (`http://localhost:3000`, etc.).

In production, point your frontend environment variable `REACT_APP_SCHOLARSHIP_MATCHER_URL`
to the public URL of this service (for example, `https://ml.your-domain.com`), and keep the API contract
described above stable so the UI continues to work without changes.

