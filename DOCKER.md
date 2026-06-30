# Docker Deployment Guide - Patient Agent MAS

## Overview

The Patient Agent MAS application is fully containerized with Docker. Both the frontend (React + Nginx) and backend (FastAPI) run in separate containers and communicate over a Docker network.

---

## Local Development with Docker

### Quick Start

```bash
# Build images
docker compose build

# Start services (requires OPENAI_API_KEY)
OPENAI_API_KEY=sk-... docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

### Access Points

- **Frontend**: http://localhost
- **API**: http://localhost:8000/api
- **Health Check**: http://localhost:8000/api/health

### Testing

```bash
# API health check
curl http://localhost:8000/api/health

# Test agent pipeline
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "jd-001",
    "chief_complaint": "Fatigue",
    "laboratory_review": true,
    "risk_assessment": true,
    "cost_estimate": true
  }'
```

---

## Docker Images

### Backend Image (`Dockerfile.backend`)

**Base**: `python:3.12-slim`

**Features**:
- FastAPI + Uvicorn server
- OpenAI API integration
- Health checks enabled
- Non-root user for security
- ~676MB final size

**Environment Variables**:
- `OPENAI_API_KEY` - Required for LLM operations

### Frontend Image (`Dockerfile.frontend`)

**Base**: `nginx:alpine`

**Features**:
- Multi-stage build (optimized)
- React + TypeScript compiled
- Nginx reverse proxy
- API proxy to backend
- Gzip compression enabled
- Health checks enabled
- ~92MB final size

---

## Production Deployment on Azure

### Prerequisites

1. Docker and Docker Compose installed on Azure VM
2. GitHub Personal Access Token for pulling images from GitHub Container Registry
3. Environment variables configured

### Setup Azure VM for Docker

```bash
# SSH into Azure VM
ssh -i Patient2Key.pem azureuser@172.191.149.139

# Install Docker
sudo apt update
sudo apt install -y docker.io docker-compose

# Add user to docker group
sudo usermod -aG docker azureuser

# Verify installation
docker --version
docker compose --version
```

### Manual Deployment

```bash
# Clone repository
cd /home/azureuser
git clone https://github.com/Stormpiethon/Patient_Agent_MAS.git
cd Patient_Agent_MAS

# Log in to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Create .env file
echo "OPENAI_API_KEY=sk-..." > .env

# Start services using production compose file
docker compose -f docker-compose.prod.yml up -d

# Verify
docker compose ps
curl http://localhost/api/health
```

### Automated Deployment (GitHub Actions)

The `.github/workflows/docker-deploy.yml` workflow:

1. **Triggers on**: Push to `main` branch
2. **Builds**: Both backend and frontend Docker images
3. **Pushes to**: GitHub Container Registry (`ghcr.io`)
4. **Deploys to**: Azure VM via SSH
5. **Pulls and runs**: Latest images with docker compose

**Required GitHub Secrets**:
- `PATIENT_SSH_KEY` - SSH private key for Azure VM
- `VM_USER` - Azure VM username (azureuser)
- `VM_IP` - Azure VM IP (172.191.149.139)
- `OPENAI_API_KEY` - OpenAI API key for runtime

---

## Docker Network Architecture

```
┌─────────────────────────────────────────┐
│        Docker Host (localhost)          │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  Frontend Container (Nginx)      │  │
│  │  Port 80                         │  │
│  │  ├─ Serves React SPA             │  │
│  │  └─ Proxies /api → backend:8000  │  │
│  └──────────────────────────────────┘  │
│           ↕ (patient-network)          │
│  ┌──────────────────────────────────┐  │
│  │  Backend Container (Uvicorn)     │  │
│  │  Port 8000                       │  │
│  │  ├─ FastAPI Server               │  │
│  │  └─ Multi-Agent System           │  │
│  └──────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
```

---

## Health Checks

Both containers have built-in health checks:

```bash
# Check container health
docker compose ps

# View health status
docker inspect patient-api | grep -A 10 Health
docker inspect patient-ui | grep -A 10 Health
```

---

## Troubleshooting

### Containers won't start

```bash
# View logs
docker compose logs -f

# Rebuild images
docker compose build --no-cache

# Restart services
docker compose restart
```

### API connection errors

```bash
# Verify network
docker network ls
docker network inspect patient_patient-network

# Test network connectivity
docker compose exec frontend wget http://backend:8000/api/health
```

### Port conflicts

```bash
# View port usage
docker compose ps

# Change ports in docker-compose.yml
# ports:
#   - "8001:8000"  # Use different host port
```

### Image pull failures

```bash
# Log in to registry
docker login ghcr.io -u USERNAME

# Pull images manually
docker pull ghcr.io/stormpiethon/patient_agent_mas-backend:latest
docker pull ghcr.io/stormpiethon/patient_agent_mas-frontend:latest
```

---

## Performance Optimization

### Image Sizes

- Backend: 676MB
- Frontend: 92MB
- **Total**: ~768MB

### Optimization Tips

1. **Multi-stage builds**: Frontend uses builder stage to reduce final size
2. **Slim base images**: Python slim and nginx alpine are minimal
3. **Layer caching**: Dependencies cached separately from source code
4. **Gzip compression**: Enabled in nginx for assets

### Resource Limits

Add to `docker-compose.yml` if needed:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
  frontend:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
```

---

## Updating Containers

```bash
# Pull latest images
docker compose pull

# Restart with new images
docker compose up -d

# View running versions
docker compose images
```

---

## Cleanup

```bash
# Stop containers
docker compose down

# Remove images
docker rmi patient-backend patient-frontend

# Remove volumes
docker volume rm patient_patient_data

# Remove dangling images
docker image prune -a
```

---

## CI/CD Workflow

1. **Developer pushes to main**
   ↓
2. **GitHub Actions triggers**
   ↓
3. **Build Docker images**
   ↓
4. **Push to GitHub Container Registry**
   ↓
5. **Deploy to Azure VM**
   ↓
6. **Pull and run latest images**
   ↓
7. **Application updated in production**

---

## References

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [GitHub Actions](https://docs.github.com/en/actions)
