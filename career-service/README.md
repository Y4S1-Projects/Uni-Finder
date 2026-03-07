# Career Service (FastAPI)

This service provides career recommendations and AI-powered explainability.

## Location

- Entry: `career-service/app.py`

## Port (local dev)

The frontend is configured to call this service at:

- `http://127.0.0.1:5004`

Health:

- `GET http://127.0.0.1:5004/health`

## Prerequisites

- Python 3.10+ recommended

## Setup

```bash
cd career-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
cd career-service
.venv\Scripts\activate
python -m uvicorn app:app --reload --host 127.0.0.1 --port 5004
```

## Data/model dependencies

This service includes the `career-ml/` folder containing all ML artifacts (CSV/JSON/PKL). The folder structure is:

```
career-service/
├── career-ml/           # ML data, models, and scripts
│   ├── data/
│   │   ├── expanded/    # skills_v2.csv
│   │   ├── processed/   # role profiles, job vectors, career ladders
│   │   └── reports/     # analytics reports
│   ├── models/          # trained classifiers (.pkl)
│   └── scripts/         # training & data processing scripts
├── services/            # recommender, explainer, vectorizer
├── app.py               # FastAPI entry point
├── config.py            # path configuration
├── data_loader.py       # startup data loading
└── requirements.txt
```

Paths are configured in `config.py`. Use `DATA_VERSION=v2` (default) or `DATA_VERSION=v1` to toggle between V2 and V1 datasets.

## Environment & configuration

- CORS origins are configured in `career-service/config.py`.
- Explainability uses Gemini when configured.

Recommended approach:

- Set `GEMINI_API_KEY` as an environment variable rather than hard-coding it.
