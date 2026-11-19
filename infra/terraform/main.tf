terraform {
  required_version = ">= 1.5"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }

  # Remote state in the existing storage account (rg-tfstate / stmarjantfstate01)
  backend "azurerm" {
    resource_group_name  = "rg-tfstate"
    storage_account_name = "stmarjantfstate01"
    container_name       = "tfstate"
    key                  = "cst-aks.tfstate"
    # Use the service principal's blob RBAC role instead of fetching the account key (needs listKeys permission)
    use_azuread_auth = true
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

# Existing resource group (created manually in the new tenant, not by Terraform)
data "azurerm_resource_group" "app" {
  name = var.resource_group_name
}

# Existing registry that build:docker pushes to
data "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = var.acr_resource_group
}

resource "azurerm_kubernetes_cluster" "aks" {
  name                = var.cluster_name
  location            = data.azurerm_resource_group.app.location
  resource_group_name = data.azurerm_resource_group.app.name
  dns_prefix          = var.cluster_name

  default_node_pool {
    name       = "default"
    node_count = var.node_count
    vm_size    = var.node_vm_size
  }

  identity {
    type = "SystemAssigned"
  }
}

# Lets the cluster nodes pull images from ACR without pull secrets
resource "azurerm_role_assignment" "aks_acr_pull" {
  scope                            = data.azurerm_container_registry.acr.id
  role_definition_name             = "AcrPull"
  principal_id                     = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
  skip_service_principal_aad_check = true
}

# Container Apps runtime (the existing app stays; deploy:azure updates its image)
resource "azurerm_container_app_environment" "cae" {
  name                = var.container_app_environment_name
  location            = data.azurerm_resource_group.app.location
  resource_group_name = data.azurerm_resource_group.app.name
}

resource "azurerm_container_app" "app" {
  name                         = var.container_app_name
  resource_group_name          = data.azurerm_resource_group.app.name
  container_app_environment_id = azurerm_container_app_environment.cae.id
  revision_mode                = "Single"

  identity {
    type = "SystemAssigned"
  }

  # Sessions are in memory, so the app must stay on one replica
  template {
    min_replicas = var.container_app_min_replicas
    max_replicas = 1

    container {
      name   = "calibration-tool"
      image  = "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"
      cpu    = 0.25
      memory = "0.5Gi"

      env {
        name  = "CST_DATA_DIR"
        value = "/data"
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = 8000
    transport        = "http"

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  # Image and registry are set by deploy:azure (az containerapp update / registry set)
  lifecycle {
    ignore_changes = [template[0].container[0].image, registry]
  }
}

# Lets the Container App pull from ACR with its managed identity
resource "azurerm_role_assignment" "app_acr_pull" {
  scope                            = data.azurerm_container_registry.acr.id
  role_definition_name             = "AcrPull"
  principal_id                     = azurerm_container_app.app.identity[0].principal_id
  skip_service_principal_aad_check = true
}
