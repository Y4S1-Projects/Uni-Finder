# Vercel + Hugging Face Spaces Deployment

This guide deploys the frontend to Vercel and the backend services to Hugging Face (HF) Docker Spaces.

You now have two options:

- Option A: Single Space (recommended for simpler secrets)
- Option B: One Space per service (legacy)

## 1) Option A: Single Space (recommended)

Run all backend services in one Docker Space using an internal reverse proxy.
HF exposes only one port (7860), so routes are path-based:

- /api -> Node backend (5000)
- /degree -> Degree service (5001)
- /budget -> Budget service (5002)
- /career -> Career service (5004)
- /scholarship -> Scholarship service (5005)

### GitHub Actions (single Space)

Add these secrets:

- HF_TOKEN
- HF_SPACE_MONO

HF_SPACE_MONO must be the full Space ID, e.g. `YasiruKaveeshwara/UniFinder`.

### Space variables (single Space)

- PORT=7860
- CORS_ORIGINS=https://<your-vercel-domain>
- MONGO=<your-mongodb-connection-string>
- JWT_SECRET=<your-jwt-secret>
- OPENAI_API_KEY=<your-openai-api-key>
- GEMINI_API_KEY=<your-gemini-api-key>

Note: SCHOLARSHIP_SERVICE_URL is not required in single Space mode because the backend uses http://localhost:5005 by default.

### Vercel env (single Space)

- REACT_APP_BACKEND_URL=https://<your-space>.hf.space
- REACT_APP_DEGREE_SERVICE_URL=https://<your-space>.hf.space/degree
- REACT_APP_BUDGET_SERVICE_URL=https://<your-space>.hf.space/budget
- REACT_APP_CAREER_SERVICE_URL=https://<your-space>.hf.space/career
- REACT_APP_SCHOLARSHIP_MATCHER_URL=https://<your-space>.hf.space/scholarship

Optional (compat alias):

- REACT_APP_SCHOLARSHIP_SERVICE_URL=https://<your-space>.hf.space/scholarship

## 2) Option B: One Space per service (legacy)

Create one Docker Space per service:

- backend (Node/Express)
- degree-recommendation-service (FastAPI)
- budget_optimizer_service (Flask)
- career-service (FastAPI)
- scholarship_and_loan_recommendation_service (FastAPI)

Point each Space to the corresponding folder and push the code (HF UI or git).

### GitHub Actions (optional)

If you want GitHub Actions to deploy to your Spaces on push, add these secrets:

- HF_TOKEN
- HF_SPACE_BACKEND
- HF_SPACE_DEGREE
- HF_SPACE_BUDGET
- HF_SPACE_CAREER
- HF_SPACE_SCHOLARSHIP

Each HF_SPACE_* value must be the full Space ID, e.g. `YasiruKaveeshwara/UniFinder-Backend`.

### Common Space variables (all services)

- PORT=7860
- CORS_ORIGINS=https://<your-vercel-domain>

### Backend (Node/Express) Space variables

- PORT=7860
- MONGO=<your-mongodb-connection-string>
- JWT_SECRET=<your-jwt-secret>
- CORS_ORIGINS=https://<your-vercel-domain>
- SCHOLARSHIP_SERVICE_URL=https://<your-scholarship-space>.hf.space

### Degree service Space variables

- PORT=7860
- CORS_ORIGINS=https://<your-vercel-domain>
- EMBEDDING_MODEL_NAME=<optional>

### Budget service Space variables

- PORT=7860
- CORS_ORIGINS=https://<your-vercel-domain>
- OPENAI_API_KEY=<your-openai-api-key>

### Career service Space variables

- PORT=7860
- CORS_ORIGINS=https://<your-vercel-domain>
- GEMINI_API_KEY=<your-gemini-api-key>

### Scholarship service Space variables

- PORT=7860
- CORS_ORIGINS=https://<your-vercel-domain>

Notes:

- Use the HTTPS URL of your Vercel deployment in CORS_ORIGINS.
- If you also want local dev, append localhost origins separated by commas.

## 3) Deploy the frontend to Vercel

Create a Vercel project from frontend/ and set these environment variables:

Suggested Vercel project settings:

- Root Directory: frontend
- Build Command: npm run build
- Output Directory: build
- Install Command: npm install

- REACT_APP_BACKEND_URL=https://<your-backend-space>.hf.space
- REACT_APP_DEGREE_SERVICE_URL=https://<your-degree-space>.hf.space
- REACT_APP_BUDGET_SERVICE_URL=https://<your-budget-space>.hf.space
- REACT_APP_CAREER_SERVICE_URL=https://<your-career-space>.hf.space
- REACT_APP_SCHOLARSHIP_MATCHER_URL=https://<your-scholarship-space>.hf.space

Optional (compat alias):

- REACT_APP_SCHOLARSHIP_SERVICE_URL=https://<your-scholarship-space>.hf.space

If REACT_APP_SCHOLARSHIP_MATCHER_URL is not set, the frontend will call the Node backend proxy at /api/scholarships.

## 4) Inter-service communication checklist

- Backend -> Scholarship service: set SCHOLARSHIP_SERVICE_URL to the scholarship Space URL.
- Frontend -> all services: set REACT*APP*\* URLs to the HTTPS Space URLs.
- CORS_ORIGINS for every service must include the Vercel domain.
- Avoid CORS_ORIGINS=\* on services that use cookies (the backend uses credentials).

## 5) Quick verification

Single Space:

- Backend health: https://<your-space>.hf.space/health
- Degree health: https://<your-space>.hf.space/degree/health
- Budget health: https://<your-space>.hf.space/budget/health
- Career health: https://<your-space>.hf.space/career/health
- Scholarship health: https://<your-space>.hf.space/scholarship/health

Multi-Space:

- Backend health: https://<backend-space>.hf.space/health
- Degree health: https://<degree-space>.hf.space/health
- Budget health: https://<budget-space>.hf.space/health
- Career health: https://<career-space>.hf.space/health
- Scholarship health: https://<scholarship-space>.hf.space/health

