# Uni-Finder Deployment Report

**Project:** Uni-Finder (Multi-Service Educational Guidance Platform)  
**Repository:** Uni-Finder  
**Branch Assessed:** `main`  
**Report Date:** 2026-03-12  
**Deployment Platform:** Microsoft Azure (Container Apps + ACR)

---

## 1. Executive Summary

Uni-Finder is deployed as a containerized microservices platform on Azure. The deployment architecture uses:

- **GitHub Actions** for CI image build and push
- **Azure Container Registry (ACR)** as container image repository
- **Azure Container Apps** for runtime hosting and autoscaling
- **PowerShell deployment automation** for create/update orchestration

The deployment process supports six services (frontend + backend + 4 AI/API services), includes image validation, digest-based image pinning, revision forcing, and post-deploy URL verification.

---

## 2. Deployment Scope

### 2.1 Services Included

1. `unifinder-frontend` (React UI)
2. `unifinder-backend` (Node/Express API)
3. `unifinder-degree-service` (FastAPI)
4. `unifinder-budget-service` (Flask/FastAPI microservice runtime in platform)
5. `unifinder-career-service` (FastAPI)
6. `unifinder-scholarship-service` (Scholarship/loan recommendation service)

### 2.2 Environments

- **Current production-style resource group:** `unifinder-rg`
- **Container Apps managed environment:** `ctse-env`
- **Registry:** `unifinderacr2026main01.azurecr.io`

---

## 3. Target Architecture

### 3.1 High-Level Architecture

1. Developer pushes changes to `main`.
2. GitHub Actions detects changed service directories.
3. Updated service images are built and pushed to ACR with:
   - `latest` tag
   - immutable commit SHA tag
4. Deployment script validates ACR repositories and resolves image references.
5. Azure Container Apps are created/updated per service.
6. Frontend URL is discovered and propagated to API services as `CORS_ORIGINS`.
7. Endpoints are output for verification.

### 3.2 Infrastructure as Code Assets

- `deploy/azure/main.bicep` provisions core shared Azure resources:
  - Log Analytics Workspace
  - Azure Container Registry
  - Managed Container Apps Environment
- `deploy/azure/container-app.bicep` provides reusable container app template with:
  - external ingress
  - TLS (`allowInsecure: false`)
  - scaling (min 1, max 3 replicas)
  - HTTP scale rule (50 concurrent requests)

---

## 4. CI/CD Implementation

### 4.1 Workflow File

- `.github/workflows/build-push-acr.yml`

### 4.2 Trigger Conditions

- Automatic on push to `main`
- Manual through `workflow_dispatch`

### 4.3 Pipeline Stages

1. **Change Detection** (paths filter) for service-specific builds
2. **ACR Secret Validation** (`ACR_LOGIN_SERVER`, `ACR_USERNAME`, `ACR_PASSWORD`)
3. **ACR Authentication** via Docker login action
4. **Buildx Setup** for multi-layer cache support
5. **Build & Push per service**
   - Tags: `latest` and `${{ github.sha }}`
   - Build cache: `:buildcache`
6. **Frontend Runtime URL Injection** using build args

### 4.4 Build Optimization

- Registry cache pull/push is configured for all images.
- Only changed services are rebuilt on push events.
- Manual runs can force full build as needed.

---

## 5. Release Deployment Process (Azure)

### 5.1 Deployment Script

- `deploy/deploy-unifinder-local.ps1`

### 5.2 Script Capabilities

- Azure subscription/context validation
- Resource group existence check and creation fallback
- ACR credential retrieval
- Required image repository validation
- Optional validation-only mode (`-ValidateOnly`)
- Create-or-update logic for each Container App
- Post-deployment CORS synchronization using actual frontend URL
- URL and deployed image output for verification

### 5.3 Version Freshness Controls (Critical)

To prevent stale frontend/backend revisions in Azure Container Apps:

1. **Digest pinning** resolves `repo:tag` -> `repo@sha256:digest` by default
2. **Deployment stamp variable** (`DEPLOYMENT_VERSION=UTC timestamp`) forces a template change and revision rollout
3. **Optional override** with `-DisableDigestPinning` if tag-only behavior is required

These controls improve deployment determinism and reduce “build succeeded but old UI still visible” incidents.

---

## 6. Runtime Configuration

### 6.1 Container Resources

| Service                       | Port |  CPU | Memory | Replicas |
| ----------------------------- | ---: | ---: | -----: | -------- |
| unifinder-frontend            |   80 | 0.25 |  0.5Gi | 1–3      |
| unifinder-backend             | 5000 |  0.5 |    1Gi | 1–3      |
| unifinder-degree-service      | 5001 |  0.5 |    1Gi | 1–3      |
| unifinder-budget-service      | 5002 |  0.5 |    1Gi | 1–3      |
| unifinder-career-service      | 5004 |  0.5 |    1Gi | 1–3      |
| unifinder-scholarship-service | 5005 |  0.5 |    1Gi | 1–3      |

### 6.2 Ingress and Access

- All services are deployed with **external ingress**.
- Frontend is public-facing and consumes public API endpoints.
- TLS enforced at ingress level (`allowInsecure: false` in bicep template).

### 6.3 Environment Variables (Examples)

- Backend: `PORT`, `MONGO`, `JWT_SECRET`, `CORS_ORIGINS`, `DEPLOYMENT_VERSION`
- Degree service: `PORT`, `CORS_ORIGINS`, `DEPLOYMENT_VERSION`
- Career service: `PORT`, `CORS_ORIGINS`, `DEPLOYMENT_VERSION`
- Frontend build args include runtime API URLs

> For submission and security governance, all sensitive values must be redacted in screenshots/documents.

---

## 7. Deployment Verification and Validation

### 7.1 CI Validation Evidence

- Successful workflow run in GitHub Actions
- Confirm built image tags in ACR:
  - `latest`
  - commit SHA

### 7.2 Runtime Validation Evidence

After script execution:

1. Confirm each service FQDN is printed
2. Confirm deployed image reference includes expected digest
3. Test endpoint health checks:
   - `GET /health` for AI services
4. Validate frontend functionality end-to-end:
   - login/auth flow
   - degree recommendation flow
   - career/budget/scholarship feature calls

### 7.3 Browser and Cache Verification

- Hard refresh (`Ctrl+F5`) after deployment
- If stale UI appears, compare active container image digest with ACR digest

---

## 8. Security, Compliance, and Operational Controls

### 8.1 Current Strengths

- TLS enabled at ingress
- CI secret-based ACR login
- Containerized service isolation
- Revision-based rollout model

### 8.2 Improvement Recommendations

1. Move hardcoded secrets from scripts to Key Vault or secret references
2. Set strict CORS allowlist per environment (avoid wildcard in production)
3. Use managed identity for ACR pulls where feasible
4. Add vulnerability image scanning in CI
5. Implement environment separation (`dev`, `staging`, `prod`) with isolated resources

---

## 9. Risks and Mitigations

| Risk                                  | Impact                      | Mitigation in Place                | Further Action                       |
| ------------------------------------- | --------------------------- | ---------------------------------- | ------------------------------------ |
| Floating tags causing stale revisions | Old code in production      | Digest pinning + deployment stamp  | Keep digest pinning default          |
| Secrets exposure                      | Security breach             | Secrets in GitHub Actions          | Migrate runtime secrets to Key Vault |
| Service-specific build path drift     | Missed image updates        | Paths filter in workflow           | Periodic workflow-path audit         |
| External API/key dependency failures  | Partial feature degradation | Graceful fallback in some services | Add alerting + retry policies        |

---

## 10. Rollback Strategy

### 10.1 Image-based Rollback

1. Identify previous known-good commit SHA tag in ACR
2. Deploy using script parameter `-ImageTag <previous_sha>`
3. Verify active image and endpoint health

### 10.2 Revision-based Rollback

- Use Azure Container Apps revision controls to route traffic to previous stable revision (if configured with multiple active revisions strategy).

---

## 11. Deployment Checklist (Submission Appendix)

### Pre-Deployment

- [ ] Code merged to `main`
- [ ] GitHub Actions build passed
- [ ] New images exist in ACR (`latest` + SHA)
- [ ] Required Azure resources are available

### Deployment

- [ ] Run `deploy/deploy-unifinder-local.ps1`
- [ ] Confirm no missing ACR repositories
- [ ] Confirm all services created/updated successfully

### Post-Deployment

- [ ] Verify all service URLs
- [ ] Verify deployed image references
- [ ] Run health checks
- [ ] Validate UI and cross-service API calls
- [ ] Capture evidence screenshots/logs

---

## 12. Evidence to Attach in Assignment

1. GitHub Actions successful run screenshot
2. ACR repositories/tags screenshot
3. Deployment script terminal output screenshot
4. Azure Container Apps service list screenshot
5. Health endpoint responses screenshot
6. Frontend functional proof screenshot (updated UI)
7. (Optional) Bicep deployment/resource screenshot from Azure portal

---

## 13. Conclusion

The Uni-Finder deployment implementation demonstrates a robust cloud-native release process with CI-based image automation and scripted Azure rollout across multiple microservices. The addition of digest pinning and forced revision updates significantly improved release reliability, particularly for frontend update visibility. The system is operationally deployable and suitable for academic submission, with clear pathways to further enterprise hardening.

---

## 14. Quick Conversion to Word

To convert this report to a Word document (`.docx`):

1. Open this markdown file in VS Code.
2. Copy all content into Microsoft Word.
3. Apply Heading styles (Heading 1/2/3) and export as `.docx`.

(If needed, this can be generated into `.docx` directly in a follow-up step.)
