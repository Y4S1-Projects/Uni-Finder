# Uni-Finder Deployment Guide

This guide covers deploying the Uni-Finder application to Azure Container Apps using Docker containers and GitHub Actions.

## 🏗️ Architecture

The application consists of 6 microservices:

1. **Backend** (Node/Express) - Port 5000
   - Authentication & authorization
   - MongoDB data persistence
   - Budget and scholarship CRUD operations

2. **Degree Recommendation Service** (FastAPI) - Port 5001
   - ML-based degree recommendations
   - Eligibility checking
   - Semantic similarity matching

3. **Budget Optimizer Service** (Flask) - Port 5002
   - ML budget predictions
   - Financial analysis
   - OpenAI-powered insights

4. **Career Service** (FastAPI) - Port 5004
   - Career recommendations
   - Skill gap analysis
   - AI explanations (Gemini)

5. **Scholarship Service** (FastAPI) - Port 5005
   - Scholarship/loan matching
   - ML-based recommendations

6. **Frontend** (React + Nginx) - Port 80
   - User interface
   - Built with React, served by Nginx

## 📋 Prerequisites

### Local Development
- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose
- Node.js 18+ (for local development without Docker)
- Python 3.11+ (for local development without Docker)

### Azure Deployment
- Azure account with active subscription
- Azure CLI installed locally
- GitHub repository with secrets configured

## 🚀 Quick Start - Local Development

### 1. Clone the repository

```bash
git clone https://github.com/Y4S1-Projects/Uni-Finder.git
cd Uni-Finder
```

### 2. Configure environment variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your values
# Required:
# - MONGO_URI: Your MongoDB connection string
# - JWT_SECRET: Secret key for JWT tokens
# - OPENAI_API_KEY: OpenAI API key for budget insights
# - GEMINI_API_KEY: Google Gemini API key for explanations
```

### 3. Build and run with Docker Compose

```bash
docker-compose up --build
```

### 4. Access the application

- 🌐 Frontend: http://localhost:3000
- 🔧 Backend API: http://localhost:5000
- 🎓 Degree Service: http://localhost:5001
- 💰 Budget Service: http://localhost:5002
- 💼 Career Service: http://localhost:5004
- 🎓 Scholarship Service: http://localhost:5005

## ☁️ Azure Deployment

### Step 1: Create Azure Service Principal

```bash
# Login to Azure
az login

# Set your subscription (if you have multiple)
az account set --subscription "your-subscription-id"

# Create resource group
az group create --name unifinder-rg --location eastus

# Create service principal with contributor role
az ad sp create-for-rbac \
  --name "unifinder-github-actions" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/unifinder-rg \
  --sdk-auth
```

Copy the entire JSON output - you'll need it for GitHub secrets.

### Step 2: Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add the following secrets:

1. **AZURE_CREDENTIALS**
   - Paste the entire JSON from the service principal creation

2. **MONGO_URI**
   - Your MongoDB connection string (e.g., from MongoDB Atlas)
   - Format: `mongodb+srv://<user>:<password>@<cluster>/<db>?retryWrites=true&w=majority`

3. **JWT_SECRET**
   - A secure random string for JWT token signing
   - Generate with: `openssl rand -base64 32`

4. **OPENAI_API_KEY**
   - Your OpenAI API key from https://platform.openai.com/

5. **GEMINI_API_KEY**
   - Your Google Gemini API key from https://ai.google.dev/

### Step 3: Update ACR Name

Edit `.github/workflows/deploy-azure.yml` and change the ACR_NAME:

```yaml
env:
  ACR_NAME: unifinderacr  # Change this to a globally unique name!
```

The ACR name must be:
- Globally unique across all Azure
- Lowercase letters and numbers only
- 5-50 characters

### Step 4: Deploy

#### Option A: Automatic deployment on push

Push to the `main` or `yasiru` branch:

```bash
git add .
git commit -m "Configure Azure deployment"
git push origin yasiru
```

The GitHub Actions workflow will automatically:
1. ✅ Create Azure infrastructure (ACR, Log Analytics, Container Apps Environment)
2. ✅ Build all 6 Docker images
3. ✅ Push images to Azure Container Registry
4. ✅ Deploy all services as Container Apps
5. ✅ Configure networking and CORS
6. ✅ Output all service URLs

#### Option B: Manual deployment trigger

Go to: GitHub → Actions → "Deploy Uni-Finder to Azure Container Apps" → Run workflow

### Step 5: Access your deployed application

After deployment completes (10-15 minutes), check the workflow output for URLs:

```
🌐 Frontend: https://unifinder-frontend.{random}.eastus.azurecontainerapps.io
🔧 Backend: https://unifinder-backend.{random}.eastus.azurecontainerapps.io
```

Open the frontend URL in your browser!

## 🔧 Configuration Details

### Environment Variables

#### Backend Service
- `PORT`: Server port (default: 5000)
- `MONGO`: MongoDB connection string
- `JWT_SECRET`: Secret for JWT signing
- `CORS_ORIGINS`: Allowed CORS origins (comma-separated)

#### Degree Service
- `PORT`: Server port (default: 5001)
- `CORS_ORIGINS`: Allowed CORS origins
- `DATA_DIR`: Path to data files (default: data)
- `EMBEDDING_MODEL_NAME`: Sentence transformer model

#### Budget Service
- `PORT`: Server port (default: 5002)
- `OPENAI_API_KEY`: OpenAI API key for AI insights
- `CORS_ORIGINS`: Allowed CORS origins

#### Career Service
- `PORT`: Server port (default: 5004)
- `GEMINI_API_KEY`: Google Gemini API key
- `CORS_ORIGINS`: Allowed CORS origins
- `DATA_VERSION`: Dataset version (default: v2)

#### Scholarship Service
- `PORT`: Server port (default: 5005)
- `CORS_ORIGINS`: Allowed CORS origins

#### Frontend
Build-time variables (baked into the build):
- `REACT_APP_BACKEND_URL`: Backend API URL
- `REACT_APP_DEGREE_SERVICE_URL`: Degree service URL
- `REACT_APP_BUDGET_SERVICE_URL`: Budget service URL
- `REACT_APP_CAREER_SERVICE_URL`: Career service URL
- `REACT_APP_SCHOLARSHIP_SERVICE_URL`: Scholarship service URL

## 🐛 Troubleshooting

### Docker Compose Issues

**Issue**: Services can't connect to each other
**Solution**: Use service names as hostnames (e.g., `http://backend:5000` instead of `localhost`)

**Issue**: Port already in use
**Solution**: Change ports in docker-compose.yml or stop conflicting services

### Azure Deployment Issues

**Issue**: "ACR name already exists"
**Solution**: Change ACR_NAME in `.github/workflows/deploy-azure.yml` to a unique value

**Issue**: "Authorization failed"
**Solution**: Verify AZURE_CREDENTIALS secret is correct and service principal has contributor role

**Issue**: Container app failing to start
**Solution**: Check logs with:
```bash
az containerapp logs show \
  --name unifinder-backend \
  --resource-group unifinder-rg \
  --follow
```

**Issue**: CORS errors in browser
**Solution**: Check that CORS_ORIGINS includes the frontend URL

### Local Development Issues

**Issue**: "Missing REACT_APP_* in frontend .env"
**Solution**: Copy `frontend/.env.example` to `frontend/.env` and fill in values

**Issue**: MongoDB connection failed
**Solution**: Check MONGO_URI is correct and network allows connections

## 📊 Monitoring

### View Container App Logs

```bash
# Backend logs
az containerapp logs show \
  --name unifinder-backend \
  --resource-group unifinder-rg \
  --follow

# Degree service logs
az containerapp logs show \
  --name unifinder-degree-service \
  --resource-group unifinder-rg \
  --follow
```

### View Metrics

Go to Azure Portal → Resource Groups → unifinder-rg → Container Apps → Select service → Metrics

## 🔄 Updates and Redeployment

To deploy changes:

1. Make your code changes
2. Commit and push to `main` or `yasiru` branch
3. GitHub Actions will automatically rebuild and redeploy changed services

Or manually trigger the workflow from GitHub Actions.

## 🧹 Cleanup

To delete all Azure resources:

```bash
az group delete --name unifinder-rg --yes --no-wait
```

To stop local Docker containers:

```bash
docker-compose down
```

To remove local Docker images:

```bash
docker-compose down --rmi all
```

## 📝 Cost Estimation

Azure Container Apps pricing (approximate):

- Container Apps Environment: ~$30/month (shared across all apps)
- Each Container App: ~$0.000012/vCPU-second + $0.0000014/GB-second
- For 6 services with minimal traffic: ~$50-100/month
- Azure Container Registry (Basic): ~$5/month

Total estimated cost: **$85-135/month** for low-traffic usage

You can reduce costs by:
- Using smaller CPU/memory allocations
- Setting min replicas to 0 (scale to zero)
- Using consumption-only plan

## 🔐 Security Notes

1. **Secrets**: Never commit secrets to Git. Use GitHub Secrets and Azure Key Vault
2. **CORS**: Configure CORS_ORIGINS restrictively in production
3. **API Keys**: Rotate API keys regularly
4. **Network**: Consider using Azure Private Link for internal service communication
5. **SSL**: Container Apps automatically provide HTTPS certificates

## 📚 Additional Resources

- [Azure Container Apps Documentation](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [MongoDB Atlas Documentation](https://www.mongodb.com/docs/atlas/)

## 🆘 Support

For issues:
1. Check the troubleshooting section above
2. Review GitHub Actions workflow logs
3. Check Azure Container App logs
4. Open an issue on GitHub

## 📄 License

See LICENSE file in the repository root.
