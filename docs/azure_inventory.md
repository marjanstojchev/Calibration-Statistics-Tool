# Azure Inventory (read-only snapshot, 2026-11-18)

Subscription: `Azure subscription 1` (`37e1f076-b00f-4a0c-9bde-439f99d878db`), the only one visible to the signed-in account.

## Resource groups

| Resource group | Looks like | Notes |
|---|---|---|
| `az400_100_rg` | AZ-400 course labs | Large: web apps, VMs, Cosmos, Key Vault, and ACR `az400104ContinerRegistry1`. Not ours. |
| `rgAZ400-ServiceConnPractice1` | AZ-400 lab | Managed identity practice. |
| `AZ400-arm-incr-rg` | AZ-400 lab | Storage `az400stgdemo01`. |
| `rg-lab`, `rg-marjan-demo` | Personal labs | `rg-marjan-demo` has storage `az400storagetf1`. |
| `rg-tfstate` | Terraform state | Storage `stmarjantfstate01`, container `tfstate`. Reused as the backend for `infra/terraform`. |
| `DefaultResourceGroup-WEU`, `NetworkWatcherRG`, `VisualStudioOnline-...` | Azure defaults | Leave alone. |

## Current project resources (new tenant)

Tenant `cbd5ed7e-f781-48b5-b92f-03ae767a0b17`, resource group `cst-rg`:

- ACR `CSTContainerReg` (`cstcontainerreg.azurecr.io`). `build:docker` pushes to it; admin user is disabled.
- Container App `calibration-tool-app` in environment `cae-cst`. Created by Terraform; `deploy:azure` updates its image.
- AKS `aks-cst`, created by Terraform. Stop or start it with the manual `aks:stop` / `aks:start` pipeline jobs.

The old `csttool.azurecr.io` ACR and `calibration-tool-app` belonged to a previous tenant and are gone.

## Decision for AKS

- AKS and the Container App use the existing `cst-rg`. State stays in `rg-tfstate` / `stmarjantfstate01` / `tfstate` under key `cst-aks.tfstate`.

## Re-run the inventory

```powershell
az group list -o table
az resource list --query "[].{name:name,type:type,rg:resourceGroup}" -o table
az acr list -o table
az containerapp list -o table
az role assignment list --all --query "[?principalType=='ServicePrincipal'].{who:principalName,role:roleDefinitionName,scope:scope}" -o table
```
