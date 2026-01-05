# Uni-Finder Backend

This folder contains:

1. A **Node/Express API** (MongoDB-backed) used for authentication, admin routes, budgets, and scholarship/loan matcher routes.
2. A couple of **Python (Flask) microservices** used by the frontend (budget optimizer and recommendation API).

## 1) Node API (Express + MongoDB)

### Location

- Entry: `backend/index.js`

### Prerequisites

- Node.js 18+ recommended
- npm
- MongoDB (Atlas or local)

### Environment variables

Create `backend/.env` with (values shown are placeholders):

```env
PORT=5000
MONGO=mongodb+srv://<user>:<password>@<cluster>/<db>?retryWrites=true&w=majority
JWT_SECRET=<your-secret>
CORS_ORIGINS=http://localhost:3000
```

### Run

```bash
cd backend
npm install
npm run dev
```

Default URL:

- `http://localhost:5000` (unless `PORT` is set)

### Main route prefixes

- `/api/auth` — auth routes
- `/api/admin` — admin routes
- `/api/budget` — budget persistence routes (used by budget microservice save)
- `/api/scholarships` — scholarship/loan matcher routes

## 2) Budget Optimizer API (Flask)

### Location

- `backend/app_budget_enhanced.py`

### Port

- `http://127.0.0.1:5002`

### Environment variables

Optional:

- `MONGODB_API_URL` — where to POST saved budget predictions.
  - Default inside the service: `http://localhost:8080/api/budget/save`
  - Recommended: set it to your Node API base URL, e.g. `MONGODB_API_URL=http://localhost:5000/api/budget/save`

### Run

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app_budget_enhanced.py
```

Health:

- `GET http://127.0.0.1:5002/health`

## 3) Recommendation API (Flask)

### Location

- `backend/app.py`

### Port

- Default: `http://127.0.0.1:5003` (controlled by `PORT` env var)

### Environment variables

Optional (features degrade gracefully if missing):

- `OPENWEATHER_API_KEY`
- `GEMINI_API_KEY`
- `PLACES_DATASET_PATH` (defaults to a CSV next to the file)

### Run

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
