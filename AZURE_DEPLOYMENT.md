# Azure App Service / Container Apps Configuration
# This file documents Azure deployment options for the Calibration Statistics Tool

## Option 1: Azure Container Apps (Recommended for cloud-native apps)

### Prerequisites
- Azure Container Registry (ACR) or use GitLab Container Registry
- Azure Container Apps environment

### Deployment via Azure CLI
```bash
# Login to Azure
az login

# Create resource group (if not exists)
az group create --name cst-rg --location eastus

# Create Container Apps environment
az containerapp env create \
  --name cst-env \
  --resource-group cst-rg \
  --location eastus

# Deploy from registry
az containerapp create \
  --name cst-app \
  --resource-group cst-rg \
  --environment cst-env \
  --image <your-registry>/calibration-statistics-tool:latest \
  --target-port 8000 \
  --ingress external \
  --registry-server <your-registry> \
  --registry-username <username> \
  --registry-password <password> \
  --cpu 1 --memory 2Gi \
  --min-replicas 1 --max-replicas 3
```

### Environment Variables (configure in Azure Portal or CLI)
- `PYTHONUNBUFFERED=1`
- `QT_QPA_PLATFORM=offscreen`

---

## Option 2: Azure App Service (Web App for Containers)

### Deployment via Azure Portal
1. Create App Service Plan (Linux, B1 or higher)
2. Create Web App → Select "Docker Container"
3. Configure container:
   - Image Source: GitLab Container Registry or ACR
   - Image: `<registry>/calibration-statistics-tool:latest`
   - Port: 8000
4. Add Application Settings (Environment Variables)
5. Enable Continuous Deployment webhook

### Startup Command
```
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

---

## Option 3: Azure Kubernetes Service (AKS)

See `kubernetes/` directory for manifests (create separately if needed)

---

## Storage Configuration (Important!)

The app needs persistent storage for:
- `measurement_data/` (input files)
- `output*/` (generated results)

### Azure Files Mount
```bash
# Create storage account
az storage account create \
  --name cststorage \
  --resource-group cst-rg \
  --sku Standard_LRS

# Create file share
az storage share create \
  --name cst-data \
  --account-name cststorage

# Mount in Container Apps (configure via Portal or CLI)
# Mount path: /app/measurement_data
# Mount path: /app/output
```

---

## Scaling Configuration

### Horizontal Scaling Rules (Container Apps)
- CPU: Scale out at >70% usage
- Memory: Scale out at >80% usage
- Min replicas: 1
- Max replicas: 5

### Vertical Scaling
- Development: 0.5 CPU, 1 GB RAM
- Production: 2 CPU, 4 GB RAM

---

## Cost Optimization

1. Use Azure Container Apps (consumption-based pricing)
2. Enable scale-to-zero for dev/test environments
3. Use Azure Files Standard tier for storage
4. Consider Azure Functions for event-driven processing

---

## Monitoring

Enable Azure Monitor / Application Insights:
```bash
az monitor app-insights component create \
  --app cst-insights \
  --location eastus \
  --resource-group cst-rg
```

Add instrumentation key to environment variables.
