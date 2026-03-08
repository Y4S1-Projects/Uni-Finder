param(
    [switch]$ValidateOnly,
    [string]$ImageTag = "latest",
    [switch]$DisableDigestPinning
)

$ErrorActionPreference = "Stop"

$SubscriptionId = "54b722b3-0027-43ff-b8b1-08ef553e0c67"
$ResourceGroup = "unifinder-rg"
$EnvironmentResourceId = "/subscriptions/54b722b3-0027-43ff-b8b1-08ef553e0c67/resourceGroups/ctse-microservices-rg/providers/Microsoft.App/managedEnvironments/ctse-env"
$AcrName = "unifinderacr2026main01"

$Images = @{
    backend     = "$AcrName.azurecr.io/unifinder-backend:$ImageTag"
    degree      = "$AcrName.azurecr.io/unifinder-degree-service:$ImageTag"
    budget      = "$AcrName.azurecr.io/unifinder-budget-service:$ImageTag"
    career      = "$AcrName.azurecr.io/unifinder-career-service:$ImageTag"
    scholarship = "$AcrName.azurecr.io/unifinder-scholarship-service:$ImageTag"
    frontend    = "$AcrName.azurecr.io/unifinder-frontend:$ImageTag"
}

$ImageRepos = @{
    backend     = "unifinder-backend"
    degree      = "unifinder-degree-service"
    budget      = "unifinder-budget-service"
    career      = "unifinder-career-service"
    scholarship = "unifinder-scholarship-service"
    frontend    = "unifinder-frontend"
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

function Resolve-ImageReference {
    param(
        [string]$Repository,
        [string]$Tag
    )

    if ($DisableDigestPinning) {
        return "$AcrServer/$Repository:$Tag"
    }

    try {
        $digest = az acr repository show-tags --name $AcrName --repository $Repository --detail --orderby time_desc --query "[?name=='$Tag'] | [0].digest" -o tsv
        if ($digest) {
            return "$AcrServer/$Repository@$digest"
        }
    }
    catch {
        Write-Warning "Could not resolve digest for $Repository`:$Tag. Falling back to tag."
    }

    return "$AcrServer/$Repository:$Tag"
}

Write-Host "Resolving image references (digest pinning: $([string](-not $DisableDigestPinning))) ..."
foreach ($key in $Images.Keys) {
    $repo = $ImageRepos[$key]
    $resolved = Resolve-ImageReference -Repository $repo -Tag $ImageTag
    $Images[$key] = $resolved
    Write-Host " - $key => $resolved"
}

$deployStamp = [DateTime]::UtcNow.ToString("yyyyMMddHHmmss")

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
    "CORS_ORIGINS=*",
    "DEPLOYMENT_VERSION=$deployStamp"
)

Publish-ContainerApp -Name "unifinder-degree-service" -Image $Images.degree -Port 5001 -Ingress "external" -Cpu "0.5" -Memory "1Gi" -EnvVars @(
    "PORT=5001",
    "DEPLOYMENT_VERSION=$deployStamp"
)

Publish-ContainerApp -Name "unifinder-budget-service" -Image $Images.budget -Port 5002 -Ingress "external" -Cpu "0.5" -Memory "1Gi" -EnvVars @(
    "PORT=5002",
    "DEPLOYMENT_VERSION=$deployStamp"
)

Publish-ContainerApp -Name "unifinder-career-service" -Image $Images.career -Port 5004 -Ingress "external" -Cpu "0.5" -Memory "1Gi" -EnvVars @(
    "PORT=5004",
    "CORS_ORIGINS=*",
    "DEPLOYMENT_VERSION=$deployStamp"
)

Publish-ContainerApp -Name "unifinder-scholarship-service" -Image $Images.scholarship -Port 5005 -Ingress "external" -Cpu "0.5" -Memory "1Gi" -EnvVars @(
    "PORT=5005",
    "DEPLOYMENT_VERSION=$deployStamp"
)

Publish-ContainerApp -Name "unifinder-frontend" -Image $Images.frontend -Port 80 -Ingress "external" -Cpu "0.25" -Memory "0.5Gi" -EnvVars @(
    "DEPLOYMENT_VERSION=$deployStamp"
)

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
    $image = az containerapp show --name $app --resource-group $ResourceGroup --query "properties.template.containers[0].image" -o tsv
    Write-Host "$app => https://$fqdn"
    Write-Host "    image: $image"
}
