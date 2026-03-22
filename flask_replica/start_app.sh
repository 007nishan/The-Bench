#!/bin/bash
echo "--- Starting The Bench (Flask Replica) ---"
cd "$(dirname "$0")"

# Create virtual environment if missing
if [ ! -d "venv" ]; then
    echo "Creating venv..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies inside venv..."
pip3 install flask flask-cors pytz requests python-dotenv google-generativeai

# Run in background
nohup python3 app.py > app_output.log 2>&1 &
echo "App started in background with Venv."
