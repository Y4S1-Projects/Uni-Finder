// Azure Container Apps Infrastructure for Uni-Finder
// This template deploys all necessary Azure resources

@description('Location for all resources')
param location string = resourceGroup().location

@description('Environment name (dev, staging, prod)')
param environmentName string = 'prod'

@description('Container Apps Environment name')
param containerAppsEnvName string = 'unifinder-${environmentName}-env'

@description('Log Analytics Workspace name')
param logAnalyticsName string = 'unifinder-${environmentName}-logs'

@description('Azure Container Registry name (must be globally unique)')
param acrName string

// Log Analytics Workspace
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: logAnalyticsName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// Azure Container Registry
resource acr 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: acrName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
  }
}

// Container Apps Environment
resource containerAppsEnv 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: containerAppsEnvName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}

output containerAppsEnvironmentId string = containerAppsEnv.id
output acrLoginServer string = acr.properties.loginServer
output logAnalyticsWorkspaceId string = logAnalytics.id
