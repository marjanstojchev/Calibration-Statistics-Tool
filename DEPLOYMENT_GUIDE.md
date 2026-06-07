# Frontend + Backend Integration Guide

## Architecture

```
┌─────────────────────────────────────────────┐
│         Production (Docker/Azure)           │
│                                             │
│  ┌────────────────────────────────────┐   │
│  │   FastAPI Server (Port 8000)       │   │
│  │                                     │   │
│  │  ├─ /api/*      → API endpoints    │   │
│  │  ├─ /logs/*     → Logs endpoints   │   │
│  │  └─ /*          → React SPA        │   │
│  │     (from dist/)                    │   │
│  └────────────────────────────────────┘   │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│         Development (Local)                 │
│                                             │
│  ┌──────────────────┐  ┌─────────────────┐│
│  │ Vite Dev Server  │  │ FastAPI Server  ││
│  │   (Port 5173)    │──▶  (Port 8000)    ││
│  │                  │  │                 ││
│  │ Hot Reload       │  │ API Endpoints   ││
│  │ Proxy /api → :8000│ │ /api/*, /logs/* ││
│  └──────────────────┘  └─────────────────┘│
└─────────────────────────────────────────────┘
```

## Why This Setup?

### FastAPI Serves React (Production)
✅ **Single deployment** - One container, one service
✅ **No CORS issues** - Same origin for frontend and API
✅ **Simpler routing** - One domain, one SSL cert
✅ **Azure-friendly** - Works with App Service, Container Apps, AKS
✅ **Cost-effective** - Single compute instance

### Vite Proxy (Development)
✅ **Hot Module Replacement** - Fast refresh on code changes
✅ **Development tools** - React DevTools, source maps
✅ **API proxying** - Seamless API calls to localhost:8000

## Local Development

### Terminal 1: Start Backend
```bash
cd api
python main.py
# Runs on http://localhost:8000
```

### Terminal 2: Start Frontend
```bash
cd cst-frontend
npm run dev
# Runs on http://localhost:5173
```

Visit http://localhost:5173 - API calls automatically proxy to :8000

## Docker Builds

### Development (docker-compose)
```bash
# Start full stack
docker-compose up

# Start with frontend dev server
docker-compose --profile dev up
```

### Production Build
```bash
# Build image
docker build -t cst-app .

# Run container
docker run -p 8000:8000 cst-app

# Visit http://localhost:8000
```

## CI/CD Pipeline (.gitlab-ci.yml)

### Stages
1. **test** - Run pytest for Python backend
2. **build-frontend** - Build React with Vite → `dist/`
3. **build** - Build Python package + Docker image
4. **deploy** - Deploy to PyPI and/or Azure

### Artifacts
- `dist/` - Python wheel/sdist
- `cst-frontend/dist/` - Built React app
- Docker image - Pushed to GitLab Container Registry

## Azure Deployment

### Option 1: Azure Container Apps (Recommended)
```bash
az containerapp create \
  --name cst-app \
  --resource-group cst-rg \
  --environment cst-env \
  --image registry.gitlab.com/yourproject/calibration-statistics-tool:latest \
  --target-port 8000 \
  --ingress external
```

### Option 2: Azure App Service
1. Create Web App for Containers
2. Point to GitLab Container Registry
3. Set startup command: `uvicorn api.main:app --host 0.0.0.0 --port 8000`

See [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md) for details.

## Environment Variables

### Development
- `QT_QPA_PLATFORM=offscreen` (for headless Qt)
- `PYTHONUNBUFFERED=1` (for logging)

### Production (Azure)
Set in Azure Portal → Configuration → Application Settings

## File Structure

```
cst-frontend/
├── src/              # React source code
├── dist/             # Built static files (generated)
├── package.json      # Node dependencies
└── vite.config.js    # Vite configuration

api/
├── main.py           # FastAPI app (serves React + API)
└── routers/          # API endpoint modules

Dockerfile            # Multi-stage build (Node.js + Python)
docker-compose.yml    # Local development setup
.gitlab-ci.yml        # CI/CD pipeline
```

## Testing API Integration

### Frontend calls API
```javascript
// Development: Proxied by Vite to localhost:8000
// Production: Same origin (served by FastAPI)
fetch('/api/protocols')
  .then(res => res.json())
  .then(data => console.log(data));
```

### Health Check
- http://localhost:8000/api/health (returns `{"status":"ok"}`)
- Used by Docker healthcheck and Azure monitoring

## Troubleshooting

### Issue: API calls fail in development
- Ensure FastAPI is running on port 8000
- Check Vite proxy config in `vite.config.js`

### Issue: React app doesn't load in production
- Verify `cst-frontend/dist/` exists after build
- Check Docker logs: `docker logs <container>`
- Ensure FastAPI mounts static files correctly

### Issue: CORS errors
- Should not happen with this setup (same origin)
- If testing separately, add CORS middleware to FastAPI

## Next Steps

1. ✅ Infrastructure set up
2. ⏭️ Build React components to call API endpoints
3. ⏭️ Add authentication (JWT, Azure AD)
4. ⏭️ Set up Azure resources and configure GitLab CI variables
