@echo off
echo Starting The Bench Flask Replica...
cd /d "%~dp0"
pip install -r requirements.txt flask flask-cors pytz requests python-dotenv google-generativeai
python app.py
pause
