# 🐳 Docker Deployment Quick Start

This directory contains Docker configurations for all Uni-Finder services.

## 📦 Services

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 80 (3000 local) | React UI served by Nginx |
| Backend | 5000 | Node/Express API |
| Degree Service | 5001 | FastAPI degree recommendations |
| Budget Service | 5002 | Flask budget optimizer |
| Career Service | 5004 | FastAPI career recommendations |
| Scholarship Service | 5005 | FastAPI scholarship matching |

## 🚀 Quick Start

### 1. Local Testing with Docker Compose

```bash
# Copy environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor

# Start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:5000/health
```

### 2. Azure Cloud Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for complete Azure deployment guide.

**Quick setup:**

1. Configure GitHub Secrets (see DEPLOYMENT.md)
2. Update ACR_NAME in `.github/workflows/deploy-azure.yml`
3. Push to `main` or `yasiru` branch
4. GitHub Actions will automatically deploy!

## 📁 File Structure

```
.
├── .github/workflows/
│   └── deploy-azure.yml          # GitHub Actions deployment pipeline
├── backend/
│   ├── Dockerfile                # Backend container
│   └── .dockerignore
├── degree-recommendation-service/
│   ├── Dockerfile                # Degree service container
│   └── .dockerignore
├── budget_optimizer_service/
│   ├── Dockerfile                # Budget service container
│   └── .dockerignore
├── career-service/
│   ├── Dockerfile                # Career service container
│   └── .dockerignore
├── scholarship_and_loan_recommendation_service/
│   ├── Dockerfile                # Scholarship service container
│   └── .dockerignore
├── frontend/
│   ├── Dockerfile                # Frontend multi-stage build
│   ├── deploy/nginx/
│   │   └── default.conf          # Nginx configuration
│   └── .dockerignore
├── deploy/azure/
│   ├── main.bicep                # Azure infrastructure template
│   ├── container-app.bicep       # Container app template
│   └── env.example               # Azure environment variables
├── docker-compose.yml            # Local orchestration
├── .env.example                  # Environment variables template
└── docs/
    └── DEPLOYMENT.md             # Full deployment guide
```

## 🔧 Individual Service Docker Commands

### Backend
```bash
cd backend
docker build -t unifinder-backend .
docker run -p 5000:5000 --env-file .env unifinder-backend
```

### Degree Service
```bash
cd degree-recommendation-service
docker build -t unifinder-degree .
docker run -p 5001:5001 unifinder-degree
```

### Budget Service
```bash
cd budget_optimizer_service
docker build -t unifinder-budget .
docker run -p 5002:5002 --env-file .env unifinder-budget
```

### Career Service
```bash
cd career-service
docker build -t unifinder-career .
docker run -p 5004:5004 --env-file .env unifinder-career
```

### Scholarship Service
```bash
cd scholarship_and_loan_recommendation_service
docker build -t unifinder-scholarship .
docker run -p 5005:5005 unifinder-scholarship
```

### Frontend
```bash
cd frontend
docker build \
  --build-arg REACT_APP_BACKEND_URL=http://localhost:5000 \
  --build-arg REACT_APP_DEGREE_SERVICE_URL=http://localhost:5001 \
  --build-arg REACT_APP_BUDGET_SERVICE_URL=http://localhost:5002 \
  --build-arg REACT_APP_CAREER_SERVICE_URL=http://localhost:5004 \
  --build-arg REACT_APP_SCHOLARSHIP_SERVICE_URL=http://localhost:5005 \
  -t unifinder-frontend .
docker run -p 3000:80 unifinder-frontend
```

## 🔍 Health Checks

All services include health check endpoints:

- Backend: http://localhost:5000/health
- Degree: http://localhost:5001/health
- Budget: http://localhost:5002/health
- Career: http://localhost:5004/health
- Scholarship: http://localhost:5005/health
- Frontend: http://localhost:3000/ (Nginx status)

## 📊 Docker Image Sizes (Approximate)

| Service | Base Image | Approx Size |
|---------|-----------|-------------|
| Backend | node:20-alpine | ~200MB |
| Degree Service | python:3.11-slim | ~800MB |
| Budget Service | python:3.11-slim | ~700MB |
| Career Service | python:3.11-slim | ~900MB |
| Scholarship Service | python:3.11-slim | ~600MB |
| Frontend | nginx:1.27-alpine | ~50MB |

## 🛠️ Troubleshooting

**Issue**: Container fails to start
```bash
# View logs
docker-compose logs <service-name>

# Example
docker-compose logs backend
```

**Issue**: Port already in use
```bash
# Find what's using the port
netstat -ano | findstr :5000  # Windows
lsof -i :5000                  # Linux/Mac

# Stop all containers
docker-compose down
```

**Issue**: Services can't communicate
- Make sure all services are on the same Docker network
- Use service names (not localhost) for inter-service communication

## 📚 Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Full Deployment Guide](docs/DEPLOYMENT.md)

## 🔐 Security

- Never commit `.env` files
- Use Docker secrets for sensitive data in production
- Keep Docker images updated
- Use multi-stage builds to reduce image size
- Run containers as non-root users (implemented in all Dockerfiles)

## 📝 Notes

- Frontend uses multi-stage build (Node build → Nginx serve)
- All Python services use slim images to reduce size
- Health checks ensure container readiness
- Auto-restart policies configured for reliability
