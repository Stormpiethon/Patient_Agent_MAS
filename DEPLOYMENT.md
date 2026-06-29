# Patient Agent MAS - Deployment Guide

## Local Development

### Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with OpenAI API key
echo "OPENAI_API_KEY=sk-..." > .env
```

### Running Locally

**Terminal 1 - Backend API:**
```bash
source venv/bin/activate
uvicorn api.server:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev  # http://localhost:5173
```

**Test:**
```bash
curl http://localhost:8000/api/health
```

---

## Azure VM Deployment

### Prerequisites
- Azure VM: `172.191.149.139`
- User: `azureuser`
- SSH Key: `Patient2Key.pem`

### Automated Deployment

```bash
chmod +x deploy.sh
./deploy.sh 172.191.149.139 azureuser Patient2Key.pem
```

### Manual Deployment

```bash
ssh -i Patient2Key.pem azureuser@172.191.149.139

# On the VM:
cd /home/azureuser/Patient_Agent_MAS
git clone https://github.com/Stormpiethon/Patient_Agent_MAS.git .
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start API
nohup uvicorn api.server:app --host 0.0.0.0 --port 8000 > api.log 2>&1 &

# Build frontend
cd frontend
npm install
npm run build
```

### CI/CD

GitHub Actions automatically deploys when pushing to `main`:
- Runs tests
- Deploys to Azure VM if tests pass
- Requires secrets in GitHub:
  - `PATIENT_SSH_KEY` - SSH private key content
  - `VM_USER` - azureuser
  - `VM_IP` - 172.191.149.139

---

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/generate` - Generate clinical summary

### Example Request

```bash
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

## Environment Variables

```
OPENAI_API_KEY=sk-...   # Required for LLM operations
```

---

## Troubleshooting

### API won't start
```bash
# Check if port 8000 is in use
lsof -i :8000
# Kill existing process
pkill -f "uvicorn"
```

### Frontend build fails
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Missing patient data
Ensure `data/` folder contains JSON files for test patients.

