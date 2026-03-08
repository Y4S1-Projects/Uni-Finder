// Container App template for individual services
@description('Container App name')
param containerAppName string

@description('Location for resources')
param location string = resourceGroup().location

@description('Container Apps Environment ID')
param containerAppsEnvironmentId string

@description('Container image')
param containerImage string

@description('Container port')
param containerPort int = 80

@description('Is external ingress')
param isExternal bool = true

@description('Environment variables')
param environmentVariables array = []

@description('CPU cores')
param cpu string = '0.5'

@description('Memory')
param memory string = '1Gi'

resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: containerAppName
  location: location
  properties: {
    managedEnvironmentId: containerAppsEnvironmentId
    configuration: {
      ingress: {
        external: isExternal
        targetPort: containerPort
        transport: 'http'
        allowInsecure: false
      }
      registries: []
    }
    template: {
      containers: [
        {
          name: containerAppName
          image: containerImage
          resources: {
            cpu: json(cpu)
            memory: memory
          }
          env: environmentVariables
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
        rules: [
          {
            name: 'http-scaling'
            http: {
              metadata: {
                concurrentRequests: '50'
              }
            }
          }
        ]
      }
    }
  }
}

output fqdn string = containerApp.properties.configuration.ingress.fqdn
output containerAppId string = containerApp.id
