#!/bin/bash
echo "--- Starting The Bench (Flask Replica) ---"
cd "$(dirname "$0")"

# Create virtual environment if missing
if [ ! -d "venv" ]; then
    echo "Creating venv..."
    python3 -m venv venv
fi

# Activate venv
pkill -f "app.py" || true
echo "Killing existing app.py process to free port 5000..."

source venv/bin/activate

# Install dependencies
echo "Installing dependencies inside venv..."
./venv/bin/pip install -r requirements.txt > pip_output.log 2>&1

# Run in background
nohup ./venv/bin/python3 app.py > app_output.log 2>&1 &
echo "App started in background with Venv."
