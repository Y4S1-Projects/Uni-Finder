# ⚠️ IMPORTANT: AZURE DEPLOYMENT SETUP INSTRUCTIONS

## Step 1: Create Azure Service Principal

Run this command in PowerShell (requires Azure CLI):

```powershell
# First, login to Azure
az login

# List your subscriptions to get the ID
az account list --output table

# Set your subscription (if you have multiple)
$SUBSCRIPTION_ID = "your-subscription-id"
az account set --subscription $SUBSCRIPTION_ID

# Create the service principal
az ad sp create-for-rbac `
  --name "unifinder-github-actions" `
  --role contributor `
  --scopes "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/unifinder-rg" `
  --sdk-auth
```

**⚠️ IMPORTANT:** Copy the entire JSON output - you'll need it for GitHub Secrets!

---

## Step 2: Add GitHub Secrets

Go to: **GitHub Repository → Settings → Secrets and variables → Actions**

Click **New repository secret** and add these 5 secrets:

### Secret 1: AZURE_CREDENTIALS
- **Value**: Paste the entire JSON from Step 1

### Secret 2: MONGO_URI
- **Value**: `mongodb+srv://shehan:Shehan99@cluster0.t3v3psz.mongodb.net/Hotel_Management?retryWrites=true&w=majority&appName=Cluster0`

### Secret 3: JWT_SECRET
- **Value**: `shehan`

### Secret 4: OPENAI_API_KEY
- **Value**: Get from https://platform.openai.com/api-keys
- Or use placeholder: `sk-test-key-for-testing`

### Secret 5: GEMINI_API_KEY
- **Value**: Get from https://ai.google.dev/
- Or use placeholder: `test-key-for-testing`

---

## Step 3: Update ACR Name

Edit `.github/workflows/deploy-azure.yml` and change the ACR name to something globally unique:

```yaml
env:
  AZURE_RESOURCE_GROUP: unifinder-rg
  AZURE_LOCATION: eastus
  ENVIRONMENT: prod
  ACR_NAME: unifinderacr2026  # Change this! (lowercase, alphanumeric only)
```

The ACR name must be:
- ✅ Globally unique across all Azure
- ✅ Lowercase letters and numbers only
- ✅ 5-50 characters

**Bad names**:
- ❌ unifinder-acr (has dash)
- ❌ UniFindersACR (has uppercase)
- ❌ unifinderacr (might already exist)

**Good names**:
- ✅ unifinderacr2026
- ✅ unifindercontainers
- ✅ unifinderregistry01

---

## Step 4: Deploy to Azure

You have 3 options:

### Option A: Automatic (Recommended)
```powershell
cd d:\My GitHub\Uni-Finder
git add .
git commit -m "Setup Azure deployment with updated ACR name"
git push origin yasiru
```

GitHub Actions will automatically start!

### Option B: Manual Trigger
1. Go to GitHub → Actions tab
2. Select "Deploy Uni-Finder to Azure Container Apps"
3. Click "Run workflow" button

### Option C: Manual Azure CLI
```powershell
# Login to Azure
az login

# Create resource group
az group create --name unifinder-rg --location eastus

# Deploy with Bicep
az deployment group create `
  --resource-group unifinder-rg `
  --template-file deploy/azure/main.bicep `
  --parameters environmentName=prod acrName=unifinderacr2026 location=eastus
```

---

## What The Deployment Does

When you push/trigger the workflow, it will:

✅ **Authenticate** to Azure
✅ **Create infrastructure**:
  - Azure Container Registry (ACR)
  - Log Analytics Workspace
  - Container Apps Environment

✅ **Build Docker images** for all 6 services
✅ **Push images** to ACR
✅ **Deploy services** to Container Apps:
  - Backend (port 5000)
  - Degree Service (port 5001)
  - Budget Service (port 5002)
  - Career Service (port 5004)
  - Scholarship Service (port 5005)
  - Frontend (port 80)

✅ **Configure networking** (CORS, URLs)
✅ **Output all service URLs**

---

## Deployment Timeline

- Build & Push: ~5-10 minutes
- Infrastructure Provisioning: ~2-3 minutes
- Service Deployments: ~5-10 minutes
- **Total: 15-25 minutes**

---

## After Deployment

Once complete, you'll see in the workflow output:

```
🚀 Frontend: https://unifinder-frontend.xxxxxxx.eastus.azurecontainerapps.io
🔧 Backend: https://unifinder-backend.xxxxxxx.eastus.azurecontainerapps.io
🎓 Degree Service: https://unifinder-degree-service.xxxxxxx.eastus.azurecontainerapps.io
💰 Budget Service: https://unifinder-budget-service.xxxxxxx.eastus.azurecontainerapps.io
💼 Career Service: https://unifinder-career-service.xxxxxxx.eastus.azurecontainerapps.io
🎓 Scholarship Service: https://unifinder-scholarship-service.xxxxxxx.eastus.azurecontainerapps.io
```

Open the frontend URL in your browser to test!

---

## Troubleshooting

### Workflow Fails at "Azure Login"
- Check AZURE_CREDENTIALS secret is correct JSON
- Verify the JSON includes proper subscription ID

### Workflow Fails at "Create Resource Group"
- Check Azure subscription has capacity
- Verify service principal has contributor role

### Workflow Fails at "Build Docker Images"
- Check GitHub Actions logs for error details
- Verify all Dockerfiles are valid

### Container Apps Won't Start
- Check Azure Container Apps logs:
```powershell
az containerapp logs show \
  --name unifinder-backend \
  --resource-group unifinder-rg \
  --follow
```

### CORS Errors in Frontend
- The workflow will auto-configure CORS
- Wait for workflow to fully complete
- Check that CORS_ORIGINS includes frontend URL

---

## Cost Estimate

Monthly costs for running all 6 services on Azure:

| Resource | Cost |
|----------|------|
| Container Apps (6 services) | $50-80 |
| Container Registry | $5 |
| Log Analytics (30 days retention) | $10-20 |
| **Total** | **$65-105/month** |

This is for minimal traffic. Costs scale with usage.

---

## Next: Monitor Your Deployment

Watch the GitHub Actions workflow:
1. Go to **GitHub → Actions**
2. Select **"Deploy Uni-Finder to Azure Container Apps"**
3. Click the latest workflow run
4. Watch the steps complete
5. Check the final output for your service URLs

---

## Questions?

✅ Check `docs/DEPLOYMENT.md` for complete guide
✅ Check `CONTAINERIZATION_SUMMARY.md` for implementation details
✅ Review GitHub Actions logs for specific errors

Good luck with your Azure deployment! 🚀
