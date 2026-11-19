# Kubernetes Intro for the Calibration Statistics Tool

## What Kubernetes does

You describe the state you want in YAML (for example "one copy of this image, reachable on port 80"). Kubernetes keeps the cluster in that state: it starts the container, restarts it if it fails, and routes traffic to it.

## Concepts mapped to this app

| Concept | What it is | In this repo |
|---|---|---|
| Image | The built container | `calibration-tool` from the `Dockerfile` (in ACR) |
| Pod | One running copy of the container | One pod running uvicorn on port 8000 |
| Deployment | Keeps N pods running and handles updates | `deploy/k8s/deployment.yaml`, `replicas: 1` |
| Service | Stable address in front of the pods | `deploy/k8s/service.yaml`, port 80 → 8000 |
| Probes | Health checks | Both use `/api/health` |
| Env vars | Config | `CST_DATA_DIR`, `CST_SESSION_TTL_HOURS` (see `api/settings.py`) |
| Node / cluster | The machines that run pods | AKS node pool, created by Terraform |

**Why one replica:** sessions are in memory, and the Dockerfile runs one uvicorn worker. A second pod would not see the first pod's sessions, so users would randomly lose their data. Do not scale up.

## How the pieces fit

```
GitLab pipeline ──build:docker──▶ ACR (image)
                                    │
Terraform ──creates──▶ AKS cluster ─┘ (AcrPull role lets the cluster pull)
                         ▲
GitLab deploy:aks ──kubectl apply / set image──┘
```

- **Terraform** builds the infrastructure (resource group, cluster, pull permission).
- **kubectl / the pipeline** deploys the app onto that infrastructure.

## Try it locally first

1. Docker Desktop → Settings → Kubernetes → Enable Kubernetes. Wait until it is running.
2. Build the image: `docker build -t calibration-tool:local .`
3. Apply the manifests with the local image:
   ```powershell
   kubectl apply -f deploy/k8s/
   kubectl set image deployment/calibration-tool calibration-tool=calibration-tool:local
   kubectl rollout status deployment/calibration-tool
   ```
4. Open it: `kubectl port-forward svc/calibration-tool 8000:80`, then browse `http://localhost:8000/api/health`.
5. Useful commands: `kubectl get pods`, `kubectl describe pod <name>`, `kubectl logs deploy/calibration-tool`.
6. Clean up: `kubectl delete -f deploy/k8s/`.

## Then AKS

```powershell
cd infra/terraform
copy terraform.tfvars.example terraform.tfvars   # defaults already point at cst-rg / CSTContainerReg
terraform init
terraform plan
terraform apply
az aks get-credentials -g cst-rg -n aks-cst
kubectl apply -f ../../deploy/k8s/
```

Cost control: AKS nodes bill while the cluster runs. Stop it when idle with `az aks stop -g cst-rg -n aks-cst` (or the manual `aks:stop` pipeline job) and start it again with `az aks start` (or `aks:start`). The Container App scales to zero when `container_app_min_replicas = 0`, which is the default. To remove everything, run `terraform destroy`.
