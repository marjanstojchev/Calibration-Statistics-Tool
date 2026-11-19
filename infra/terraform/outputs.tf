output "cluster_name" {
  value = azurerm_kubernetes_cluster.aks.name
}

output "resource_group" {
  value = data.azurerm_resource_group.app.name
}

output "container_app_fqdn" {
  value = azurerm_container_app.app.ingress[0].fqdn
}

output "acr_login_server" {
  value = data.azurerm_container_registry.acr.login_server
}
