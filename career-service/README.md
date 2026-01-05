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

This service reads its artifacts from the `career-ml/` folder (CSV/JSON/PKL). If you move folders around, update the paths in `career-service/config.py`.

## Environment & configuration

- CORS origins are configured in `career-service/config.py`.
- Explainability uses Gemini when configured.

Recommended approach:

- Set `GEMINI_API_KEY` as an environment variable rather than hard-coding it.
