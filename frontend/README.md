# Uni-Finder Frontend (React)

This is the React UI for Uni-Finder.

## Prerequisites

- Node.js 18+ recommended
- npm

## Setup

```bash
cd frontend
npm install
```

Create your environment file:

```bash
copy .env.example .env
```

Then start the dev server:

```bash
npm start
```

- App: `http://localhost:3000`

## Environment variables

This app uses Create React App env vars (must be prefixed with `REACT_APP_`).

See [frontend/.env.example](.env.example) for the full list. The important ones:

- `REACT_APP_BACKEND_URL` (Node API)
- `REACT_APP_DEGREE_SERVICE_URL` (Degree service)
- `REACT_APP_CAREER_SERVICE_URL` (Career service)
- `REACT_APP_BUDGET_SERVICE_URL` (Budget service)
- `REACT_APP_RECOMMENDATION_SERVICE_URL` (Recommendation service)

## Common issues

- **"Missing REACT*APP*\* in frontend .env"**

  - Ensure you created `frontend/.env` from `.env.example` and restarted `npm start`.

- **"Cannot find module 'react-router-dom'"**
  - Run `npm install` in `frontend/`.
