# main.tf
provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "ai_agents" {
  name     = "ai-agents-rg"
  location = "eastus"
}

module "aks" {
  source              = "Azure/aks/azurerm"
  resource_group_name = azurerm_resource_group.ai_agents.name
  client_id           = var.client_id
  client_secret       = var.client_secret
  prefix              = "aiagents"
}

module "redis" {
  source              = "Azure/redis/azurerm"
  resource_group_name = azurerm_resource_group.ai_agents.name
  location            = azurerm_resource_group.ai_agents.location
  capacity            = 2
  family              = "C"
  sku_name            = "Standard"
  enable_non_ssl_port = false
  minimum_tls_version = "1.2"
}

module "storage" {
  source              = "Azure/storage/azurerm"
  resource_group_name = azurerm_resource_group.ai_agents.name
  storage_account_name = "aiagentsconfig"
  account_tier        = "Standard"
  account_replication_type = "LRS"
}

module "servicebus" {
  source              = "Azure/servicebus/azurerm"
  resource_group_name = azurerm_resource_group.ai_agents.name
  namespace_name      = "ai-agents-sb"
  sku                 = "Standard"
}

module "apim" {
  source              = "Azure/apim/azurerm"
  resource_group_name = azurerm_resource_group.ai_agents.name
  publisher_name      = "Contoso"
  publisher_email     = "admin@contoso.com"
  sku_name            = "Developer_1"
}