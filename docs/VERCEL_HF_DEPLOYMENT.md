# Vercel + Hugging Face Spaces Deployment

This guide deploys the frontend to Vercel and each backend service to its own Hugging Face (HF) Docker Space.

Why multiple Spaces? HF Spaces expose only one HTTP port (7860). Hosting each service in a separate Space is the simplest, most reliable option.

## 1) Deploy backend services to Hugging Face Spaces

Create one Docker Space per service:

- backend (Node/Express)
- degree-recommendation-service (FastAPI)
- budget_optimizer_service (Flask)
- career-service (FastAPI)
- scholarship_and_loan_recommendation_service (FastAPI)

Point each Space to the corresponding folder and push the code (HF UI or git).

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

## 2) Deploy the frontend to Vercel

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

## 3) Inter-service communication checklist

- Backend -> Scholarship service: set SCHOLARSHIP_SERVICE_URL to the scholarship Space URL.
- Frontend -> all services: set REACT_APP_* URLs to the HTTPS Space URLs.
- CORS_ORIGINS for every service must include the Vercel domain.
- Avoid CORS_ORIGINS=* on services that use cookies (the backend uses credentials).

## 4) Quick verification

- Backend health: https://<backend-space>.hf.space/health
- Degree health: https://<degree-space>.hf.space/health
- Budget health: https://<budget-space>.hf.space/health
- Career health: https://<career-space>.hf.space/health
- Scholarship health: https://<scholarship-space>.hf.space/health

## 5) If you want a single Space for all services

A single Space would need an internal reverse proxy and all services running inside one container. If you want this setup, tell me and I will prepare the proxy config and a combined Dockerfile.