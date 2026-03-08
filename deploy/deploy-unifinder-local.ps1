param(
    [switch]$ValidateOnly
)

$ErrorActionPreference = "Stop"

$SubscriptionId = "54b722b3-0027-43ff-b8b1-08ef553e0c67"
$ResourceGroup = "unifinder-rg"
$EnvironmentResourceId = "/subscriptions/54b722b3-0027-43ff-b8b1-08ef553e0c67/resourceGroups/ctse-microservices-rg/providers/Microsoft.App/managedEnvironments/ctse-env"
$AcrName = "unifinderacr2026main01"

$Images = @{
    backend     = "$AcrName.azurecr.io/unifinder-backend:latest"
    degree      = "$AcrName.azurecr.io/unifinder-degree-service:latest"
    budget      = "$AcrName.azurecr.io/unifinder-budget-service:latest"
    career      = "$AcrName.azurecr.io/unifinder-career-service:latest"
    scholarship = "$AcrName.azurecr.io/unifinder-scholarship-service:latest"
    frontend    = "$AcrName.azurecr.io/unifinder-frontend:latest"
}

Write-Host "Verifying Azure context..."
az account set --subscription $SubscriptionId | Out-Null
$rgLocation = az group show --name $ResourceGroup --query location -o tsv 2>$null
if (-not $rgLocation) {
    az group create --name $ResourceGroup --location southeastasia | Out-Null
}

Write-Host "Reading ACR credentials..."
$AcrServer = az acr show --name $AcrName --resource-group $ResourceGroup --query loginServer -o tsv
$AcrUser = az acr credential show --name $AcrName --query username -o tsv
$AcrPass = az acr credential show --name $AcrName --query passwords[0].value -o tsv

Write-Host "Validating image availability in ACR..."
$repos = az acr repository list --name $AcrName -o tsv
$requiredRepos = @(
    "unifinder-backend",
    "unifinder-degree-service",
    "unifinder-budget-service",
    "unifinder-career-service",
    "unifinder-scholarship-service",
    "unifinder-frontend"
)

$missing = @()
foreach ($repo in $requiredRepos) {
    if ($repos -notcontains $repo) {
        $missing += $repo
    }
}

if ($missing.Count -gt 0) {
    throw "Missing images in ACR: $($missing -join ', '). Run the build workflow first."
}

if ($ValidateOnly) {
    Write-Host "Validation passed. All required images exist."
    exit 0
}

function Publish-ContainerApp {
    param(
        [string]$Name,
        [string]$Image,
        [int]$Port,
        [string]$Ingress,
        [string]$Cpu,
        [string]$Memory,
        [string[]]$EnvVars
    )

    Write-Host "Deploying $Name ..."
    $createArgs = @(
        "containerapp", "create",
        "--name", $Name,
        "--resource-group", $ResourceGroup,
        "--environment", $EnvironmentResourceId,
        "--image", $Image,
        "--target-port", "$Port",
        "--ingress", $Ingress,
        "--registry-server", $AcrServer,
        "--registry-username", $AcrUser,
        "--registry-password", $AcrPass,
        "--cpu", $Cpu,
        "--memory", $Memory,
        "--min-replicas", "1",
        "--max-replicas", "3"
    )

    if ($EnvVars.Count -gt 0) {
        $createArgs += "--env-vars"
        $createArgs += $EnvVars
    }

    try {
        az @createArgs | Out-Null
    }
    catch {
        $updateArgs = @(
            "containerapp", "update",
            "--name", $Name,
            "--resource-group", $ResourceGroup,
            "--image", $Image
        )
        if ($EnvVars.Count -gt 0) {
            $updateArgs += "--set-env-vars"
            $updateArgs += $EnvVars
        }
        az @updateArgs | Out-Null
    }
}

$mongo = "mongodb+srv://shehan:Shehan99@cluster0.t3v3psz.mongodb.net/Hotel_Management?retryWrites=true&w=majority&appName=Cluster0"
$jwt = "shehan"

Publish-ContainerApp -Name "unifinder-backend" -Image $Images.backend -Port 5000 -Ingress "external" -Cpu "0.5" -Memory "1Gi" -EnvVars @(
    "PORT=5000",
    "MONGO=$mongo",
    "JWT_SECRET=$jwt",
    "CORS_ORIGINS=*"
)

Publish-ContainerApp -Name "unifinder-degree-service" -Image $Images.degree -Port 5001 -Ingress "external" -Cpu "0.5" -Memory "1Gi" -EnvVars @(
    "PORT=5001"
)

Publish-ContainerApp -Name "unifinder-budget-service" -Image $Images.budget -Port 5002 -Ingress "external" -Cpu "0.5" -Memory "1Gi" -EnvVars @(
    "PORT=5002"
)

Publish-ContainerApp -Name "unifinder-career-service" -Image $Images.career -Port 5004 -Ingress "external" -Cpu "0.5" -Memory "1Gi" -EnvVars @(
    "PORT=5004",
    "CORS_ORIGINS=*"
)

Publish-ContainerApp -Name "unifinder-scholarship-service" -Image $Images.scholarship -Port 5005 -Ingress "external" -Cpu "0.5" -Memory "1Gi" -EnvVars @(
    "PORT=5005"
)

Publish-ContainerApp -Name "unifinder-frontend" -Image $Images.frontend -Port 80 -Ingress "external" -Cpu "0.25" -Memory "0.5Gi" -EnvVars @()

$frontendFqdn = az containerapp show --name unifinder-frontend --resource-group $ResourceGroup --query properties.configuration.ingress.fqdn -o tsv
$frontendUrl = "https://$frontendFqdn"

Write-Host "Updating API CORS with frontend URL: $frontendUrl"
$apiApps = @("unifinder-backend", "unifinder-degree-service", "unifinder-budget-service", "unifinder-career-service", "unifinder-scholarship-service")
foreach ($app in $apiApps) {
    az containerapp update --name $app --resource-group $ResourceGroup --set-env-vars "CORS_ORIGINS=$frontendUrl" | Out-Null
}

Write-Host "Deployment complete. Service URLs:"
$apps = @("unifinder-frontend", "unifinder-backend", "unifinder-degree-service", "unifinder-budget-service", "unifinder-career-service", "unifinder-scholarship-service")
foreach ($app in $apps) {
    $fqdn = az containerapp show --name $app --resource-group $ResourceGroup --query properties.configuration.ingress.fqdn -o tsv
    Write-Host "$app => https://$fqdn"
}
