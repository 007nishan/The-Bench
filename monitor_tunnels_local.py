import subprocess
import time
import requests
import os

TOKEN = "8571904781:AAEhaViQiEihWOHShd0a0ywJ0BMufSh13p8"
CHAT_ID = "8687680759"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        r = requests.get(url, params={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except Exception:
        pass

def check_process(name, restart_cmd):
    res = subprocess.run("ps aux | grep [" + name[0] + "]" + name[1:], shell=True, capture_output=True, text=True)
    if name not in res.stdout:
        subprocess.run(restart_cmd, shell=True)
        return False
    return True

# 1. Check Flask App
flask_restart = "cd /home/nishan/flask_replica && source venv/bin/activate && nohup python app.py > app.log 2>&1 &"
app_was_running = check_process("app.py", flask_restart)

# 2. Check Tunnel for Bench
tunnel_restart = "nohup /home/nishan/cloudflared tunnel --url http://127.0.0.1:5000 > /home/nishan/tunnel.log 2>&1 &"
tunnel_was_running = check_process("cloudflared tunnel --url http://127.0.0.1:5000", tunnel_restart)

# 3. Check Tunnel for Portfolio 
portfolio_tunnel_restart = "nohup /home/nishan/cloudflared tunnel --url http://127.0.0.1:80 > /home/nishan/tunnel_portfolio.log 2>&1 &"
portfolio_was_running = check_process("tunnel_portfolio.log", portfolio_tunnel_restart)

if not app_was_running or not tunnel_was_running or not portfolio_was_running:
    time.sleep(15)

# 4. Read current URLs and notify
# REVERSED iteration to get the latest line!

# Bench
try:
    with open('/home/nishan/tunnel.log', 'r') as f:
        log = f.read()
    if "https://" in log:
        for line in reversed(log.splitlines()): # FIXED
            if "trycloudflare.com" in line:
                idx = line.find("https://")
                sub = line[idx:].split()[0]
                send_telegram(f"🚀 **The Bench URL:**\n{sub}")
                break
except Exception: pass

# Portfolio
try:
    with open('/home/nishan/tunnel_portfolio.log', 'r') as f:
        log_p = f.read()
    if "https://" in log_p:
        for line in reversed(log_p.splitlines()): # FIXED
            if "trycloudflare.com" in line:
                idx = line.find("https://")
                sub = line[idx:].split()[0]
                send_telegram(f"🎨 **Portfolio URL:**\n{sub}")
                break
except Exception: pass

send_telegram("✅ **Hourly Automation Triggered**")
print("Executed monitor scripts safely with reversed logs reader.")
f_check = open('/home/nishan/telegram_debug.log', 'w')
f_check.write("Sync completed successfully.")
f_check.close()
