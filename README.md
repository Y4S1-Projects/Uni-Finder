# Uni-Finder

Uni-Finder is a multi-service educational guidance platform for Sri Lankan students. It combines a React frontend with multiple backend services that provide:

- Degree recommendations
- Career guidance (recommendations + explainability)
- Scholarship/loan matching (via the Node API)
- Student budget optimization

## Repository layout

- `frontend/` — React app (UI)
- `backend/` — Node/Express API + some Python microservices
- `degree-recommendation-service/` — FastAPI degree recommendation engine
- `career-service/` — FastAPI career guidance service (includes `career-ml/` with trained models)

## Services (local dev)

| Service              | Folder                           | Tech              | Default URL                              |
| -------------------- | -------------------------------- | ----------------- | ---------------------------------------- |
| Frontend UI          | `frontend/`                      | React (CRA)       | `http://localhost:3000`                  |
| Node API             | `backend/`                       | Express + MongoDB | `http://localhost:5000` _(configurable)_ |
| Budget Optimizer API | `backend/`                       | Flask             | `http://127.0.0.1:5002`                  |
| Recommendation API   | `backend/`                       | Flask             | `http://127.0.0.1:5003`                  |
| Career Service       | `career-service/`                | FastAPI           | `http://127.0.0.1:5004`                  |
| Degree Service       | `degree-recommendation-service/` | FastAPI           | `http://127.0.0.1:5001`                  |

## Quick start (Windows)

### 1) Frontend

```bash
cd frontend
npm install
copy .env.example .env
npm start
```

### 2) Node API (Express)

```bash
cd backend
npm install
npm run dev
```

### 3) Python services

Degree Service:

```bash
cd degree-recommendation-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Career Service:

```bash
cd career-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app:app --reload --host 127.0.0.1 --port 5004
```

Budget Optimizer API:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app_budget_enhanced.py
```

Recommendation API:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Service documentation

- Frontend: [frontend/README.md](frontend/README.md)
- Node API + Python microservices: [backend/README.md](backend/README.md)
- Career Service: [career-service/README.md](career-service/README.md)
- Degree Service: [degree-recommendation-service/README.md](degree-recommendation-service/README.md)

## Cloud deployment

- Recommended: Vercel frontend + Hugging Face Spaces backend
- Detailed deployment guide: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- Local container setup: [docs/docker/DOCKER_README.md](docs/docker/DOCKER_README.md)

## Environment variables

The frontend expects service base URLs via CRA env vars. See [frontend/.env.example](frontend/.env.example).

Security note: do not commit real secrets (DB passwords, API keys) into `.env` files.
