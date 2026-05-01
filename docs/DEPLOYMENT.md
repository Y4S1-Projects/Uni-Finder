# Uni-Finder Deployment Guide

This document covers the current Uni-Finder deployment and local development workflow.

## Current deployment strategy

- Frontend: Vercel
- Backend: Hugging Face Spaces
- Local development: Docker Compose
- Primary docs:
  - `docs/DEPLOYMENT.md` — this guide
  - `docs/docker/DOCKER_README.md` — local Docker quick start
  - `docs/hf/README.spaces.md` — Hugging Face Space manifest and route summary

> Legacy Azure deployment content has been archived and is no longer part of the active documentation.

## 1. Local development with Docker Compose

### Prerequisites

- Docker Desktop or Docker Engine
- Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local Python service development)

### Quick start

```powershell
cd d:\My GitHub\Uni-Finder
copy .env.example .env
# Edit .env with your local values
# e.g. MONGO=mongodb://localhost:27017/unifinder
#      JWT_SECRET=your_secret
#      CORS_ORIGINS=http://localhost:3000

docker-compose up --build
```

### Local service URLs

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:5000`
- Degree Service: `http://localhost:5001`
- Budget Service: `http://localhost:5002`
- Career Service: `http://localhost:5004`
- Scholarship Service: `http://localhost:5005`

### Notes

- Use `docs/docker/DOCKER_README.md` for detailed Docker commands, individual service builds, and health checks.
- If ports are already in use, stop the running containers and retry.

## 2. Cloud deployment — Vercel + Hugging Face Spaces

The recommended cloud deployment path for Uni-Finder is:

- Frontend deployed to Vercel
- Backend services deployed to Hugging Face Spaces

The backend can run in a single HF Space (recommended), or optionally as separate Spaces for each service.

### 2.1 Required GitHub secrets

For a single Space deployment:

- `HF_TOKEN`
- `HF_SPACE_MONO`

For optional per-service deployment:

- `HF_SPACE_BACKEND`
- `HF_SPACE_DEGREE`
- `HF_SPACE_BUDGET`
- `HF_SPACE_CAREER`
- `HF_SPACE_SCHOLARSHIP`

### 2.2 HF Space configuration

Use the following environment variables in your Hugging Face Space(s):

- `PORT=7860`
- `CORS_ORIGINS=https://<your-vercel-domain>`
- `MONGO=<your-mongodb-connection-string>`
- `JWT_SECRET=<your-jwt-secret>`
- `OPENAI_API_KEY=<your-openai-api-key>`
- `GEMINI_API_KEY=<your-gemini-api-key>`

If you use a single backend Space, the proxy routes should map:

- `/api` → Node backend
- `/degree` → Degree service
- `/budget` → Budget service
- `/career` → Career service
- `/scholarship` → Scholarship service

### 2.3 Vercel configuration

Create a Vercel project for `frontend/` and set these variables:

- `REACT_APP_BACKEND_URL=https://<your-space>.hf.space`
- `REACT_APP_DEGREE_SERVICE_URL=https://<your-space>.hf.space/degree`
- `REACT_APP_BUDGET_SERVICE_URL=https://<your-space>.hf.space/budget`
- `REACT_APP_CAREER_SERVICE_URL=https://<your-space>.hf.space/career`
- `REACT_APP_SCHOLARSHIP_MATCHER_URL=https://<your-space>.hf.space/scholarship`

Optional compatibility alias:

- `REACT_APP_SCHOLARSHIP_SERVICE_URL=https://<your-space>.hf.space/scholarship`

### 2.4 Health check endpoints

- Backend: `https://<your-space>.hf.space/health`
- Degree: `https://<your-space>.hf.space/degree/health`
- Budget: `https://<your-space>.hf.space/budget/health`
- Career: `https://<your-space>.hf.space/career/health`
- Scholarship: `https://<your-space>.hf.space/scholarship/health`

### 2.5 Deployment workflow

The Hugging Face deployment workflow is defined in:

- `.github/workflows/deploy-hf-spaces.yml`

Use the workflow on push or manual dispatch to deploy the backend services.

## 3. Recommended documentation links

- Local Docker quick start: `docs/docker/DOCKER_README.md`
- Hugging Face Space manifest: `docs/hf/README.spaces.md`
- Primary project docs index: `docs/README.md`

## 4. Archived legacy deployment

Legacy Azure deployment artifacts remain in the repository only for historical reference.
They are not part of the current recommended deployment path.
