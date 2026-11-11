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

The app keeps one workspace folder per browser session (uploads, generated output, logs, config copies)
under `CST_DATA_DIR`. Uploads come from the user's browser, so no input data needs to be mounted.

- Mount one volume at `/data` (the image default for `CST_DATA_DIR`).
- Sessions are removed after `CST_SESSION_TTL_HOURS` of inactivity.

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
# Mount path: /data
```

### Environment variables

| Variable | Default | Meaning |
|---|---|---|
| `CST_DATA_DIR` | `<tmp>/cst-web` | Root for all session workspaces |
| `CST_SESSION_TTL_HOURS` | `24` | Idle time before a session workspace is deleted |
| `CST_MAX_SESSIONS` | `200` | Maximum number of live sessions |
| `CST_MAX_UPLOAD_MB` | `500` | Size limit of one upload |
| `CST_LOCK_TIMEOUT_SECONDS` | `900` | How long a request waits for the previous operation / the engine |
| `CST_CORS_ORIGINS` | – | Extra comma separated origins (only needed if the UI is served from another host) |

---

## Scaling Configuration

Sessions are held in memory and the processing engine uses process-wide state, so run **one replica
with one worker** until sessions move to shared storage (or sticky routing is set up). Only one
heavy operation (diagram generation, parsing) runs at a time per instance; other requests wait for
it. Long operations can exceed proxy timeouts (about 230 s on Azure): raise the ingress timeout or
move generation to a background job queue.

### Container Apps
- Min replicas: 1
- Max replicas: 1

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
