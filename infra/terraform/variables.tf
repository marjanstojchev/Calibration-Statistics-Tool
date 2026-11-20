variable "subscription_id" {
  type        = string
  description = "Azure subscription that hosts the AKS cluster and the ACR"
}

variable "resource_group_name" {
  type        = string
  default     = "cst-rg"
  description = "Existing resource group for the project (AKS, Container App, ACR)"
}

variable "cluster_name" {
  type    = string
  default = "aks-cst"
}

variable "container_app_name" {
  type    = string
  default = "calibration-tool-app"
}

variable "container_app_environment_name" {
  type    = string
  default = "cae-cst"
}

variable "container_app_min_replicas" {
  type        = number
  default     = 0
  description = "0 = scale to zero when idle (no cost), 1 = always on"
}

variable "node_count" {
  type    = number
  default = 1
}

variable "node_vm_size" {
  type        = string
  default     = "Standard_D2s_v6"
  description = "Small and cheap; the app runs a single replica"
}

variable "acr_name" {
  type        = string
  description = "Name of the existing Azure Container Registry (without .azurecr.io)"
}

variable "acr_resource_group" {
  type        = string
  description = "Resource group of the existing Azure Container Registry"
}
