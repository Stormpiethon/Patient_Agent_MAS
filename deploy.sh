#!/bin/bash

# Simple deployment script for Patient Agent MAS
# Usage: OPENAI_API_KEY="sk-..." ./deploy.sh [VM_IP] [VM_USER] [SSH_KEY_PATH]

set -e

VM_IP=${1:-"172.191.149.139"}
VM_USER=${2:-"azureuser"}
SSH_KEY=${3:-"Patient2Key.pem"}

if [ -z "$OPENAI_API_KEY" ]; then
  echo "ERROR: OPENAI_API_KEY environment variable not set"
  echo "Usage: OPENAI_API_KEY=sk-... ./deploy.sh [IP] [USER] [SSH_KEY]"
  exit 1
fi

echo "🚀 Deploying to $VM_USER@$VM_IP"

# Create a temporary script with the API key embedded
TEMP_SCRIPT=$(mktemp)
cat > "$TEMP_SCRIPT" << 'SCRIPT_EOF'
set -e

# API key passed as argument
OPENAI_KEY="$1"

# Navigate to project directory
if [ ! -d /home/azureuser/Patient_Agent_MAS ]; then
  cd /home/azureuser
  git clone https://github.com/Stormpiethon/Patient_Agent_MAS.git
fi

cd /home/azureuser/Patient_Agent_MAS

echo "📦 Pulling latest changes..."
git pull origin main

# Create .env file with API key
echo "OPENAI_API_KEY=$OPENAI_KEY" > .env

echo "🔧 Setting up Python environment..."
sudo -n apt-get update > /dev/null 2>&1 && sudo -n apt-get install -y python3.12-venv > /dev/null 2>&1 || true

VENV_PATH="/home/azureuser/Patient_Agent_MAS/venv"

if [ ! -d "$VENV_PATH/bin" ]; then
  echo "Creating virtual environment..."
  python3 -m venv "$VENV_PATH"
fi

echo "Installing dependencies..."
"$VENV_PATH/bin/python" -m ensurepip --upgrade > /dev/null 2>&1 || true
"$VENV_PATH/bin/python" -m pip install --upgrade pip setuptools > /dev/null 2>&1 || true
"$VENV_PATH/bin/python" -m pip install -q -r requirements.txt

echo "🛑 Stopping existing services..."
pkill -f "uvicorn api.server" || true
sleep 2

echo "🚀 Starting API server..."
nohup "$VENV_PATH/bin/uvicorn" api.server:app --host 0.0.0.0 --port 8000 > api.log 2>&1 &
sleep 3

echo "📦 Installing and building frontend..."
cd frontend
npm install -q 2>/dev/null || true
npm run build -q 2>/dev/null || true

echo "✅ Deployment complete!"
echo "API: http://172.191.149.139:8000/api/health"
SCRIPT_EOF

# Copy and execute the script on remote server
scp -o StrictHostKeyChecking=no -i "$SSH_KEY" "$TEMP_SCRIPT" "${VM_USER}@${VM_IP}:/tmp/deploy.sh" > /dev/null 2>&1
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" "${VM_USER}@${VM_IP}" bash /tmp/deploy.sh "$OPENAI_API_KEY"

rm "$TEMP_SCRIPT"

echo "✅ Deployment successful!"
