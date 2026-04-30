# Docker Deployment Quick Start

This document describes local container and Docker Compose setup for Uni-Finder.

## Services

| Service             | Port            | Description                    |
| ------------------- | --------------- | ------------------------------ |
| Frontend            | 80 (3000 local) | React UI served by Nginx       |
| Backend             | 5000            | Node/Express API               |
| Degree Service      | 5001            | FastAPI degree recommendations |
| Budget Service      | 5002            | Flask budget optimizer         |
| Career Service      | 5004            | FastAPI career recommendations |
| Scholarship Service | 5005            | FastAPI scholarship matching   |

## Quick Start

```powershell
copy .env.example .env
# Edit .env with your values
# Example values for local development
# MONGO=mongodb://localhost:27017/unifinder
# JWT_SECRET=your-secret
# CORS_ORIGINS=http://localhost:3000

docker-compose up --build
```

## Open the app

- Frontend: `http://localhost:3000`
- Backend health: `http://localhost:5000/health`

## Notes

- For complete deployment and cloud setup, see `docs/DEPLOYMENT.md`.
- This file is focused on local Docker development.
