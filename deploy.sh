#!/bin/bash

# Simple deployment script for Patient Agent MAS
# Usage: ./deploy.sh <VM_IP> <VM_USER> <SSH_KEY_PATH>

set -e

VM_IP=${1:-"172.191.149.139"}
VM_USER=${2:-"azureuser"}
SSH_KEY=${3:-"Patient2Key.pem"}

echo "🚀 Deploying to $VM_USER@$VM_IP"

# Deploy to server
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" "${VM_USER}@${VM_IP}" << 'EOF'
  set -e

  # Navigate to project directory (create if doesn't exist)
  if [ ! -d /home/azureuser/Patient_Agent_MAS ]; then
    cd /home/azureuser
    git clone https://github.com/Stormpiethon/Patient_Agent_MAS.git
  fi

  cd /home/azureuser/Patient_Agent_MAS

  echo "📦 Pulling latest changes..."
  git pull origin main

  echo "🔧 Setting up Python environment..."
  python3 -m venv venv || true
  source venv/bin/activate
  pip install -r requirements.txt -q

  echo "🛑 Stopping existing services..."
  pkill -f "uvicorn api.server" || true
  pkill -f "vite" || true
  sleep 2

  echo "🚀 Starting API server..."
  nohup uvicorn api.server:app --host 0.0.0.0 --port 8000 > api.log 2>&1 &

  echo "📦 Installing and building frontend..."
  cd frontend
  npm install -q 2>/dev/null || true
  npm run build -q

  echo "✅ Deployment complete!"
  echo "API running on http://$HOSTNAME:8000"
  echo "Frontend build ready in frontend/dist"
EOF

echo "✅ Deployment successful!"
