import paramiko

def update_monitor():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"
    
    bot_token = "8571904781:AAEhaViQiEihWOHShd0a0ywJ0BMufSh13p8"
    chat_id = "8687680759"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)

    monitor_script_content = f"""import subprocess
import time
import requests
import os

TOKEN = "{bot_token}"
CHAT_ID = "{chat_id}"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{{TOKEN}}/sendMessage"
    try:
        requests.get(url, params={{"chat_id": CHAT_ID, "text": msg}}, timeout=10)
    except Exception as e:
        pass

def check_process(name, restart_cmd):
    res = subprocess.run("ps aux | grep [" + name[0] + "]" + name[1:], shell=True, capture_output=True, text=True)
    if name not in res.stdout:
        subprocess.run(restart_cmd, shell=True)
        return False
    return True

# 1. Check Flask App (The Bench)
flask_restart = "cd /home/nishan/flask_replica && source venv/bin/activate && nohup python app.py > app.log 2>&1 &"
app_was_running = check_process("app.py", flask_restart)

# 2. Check Tunnel for Bench
tunnel_restart = "nohup /home/nishan/cloudflared tunnel --url http://127.0.0.1:5000 > /home/nishan/tunnel.log 2>&1 &"
tunnel_was_running = check_process("cloudflared tunnel --url http://127.0.0.1:5000", tunnel_restart)

# 3. Check Tunnel for Portfolio (Co-hosting)
portfolio_tunnel_restart = "nohup /home/nishan/cloudflared tunnel --url http://127.0.0.1:80 > /home/nishan/tunnel_portfolio.log 2>&1 &"
portfolio_was_running = check_process("cloudflared tunnel --url http://127.0.0.1:80", portfolio_tunnel_restart)

# Wait for potential restart to gather links
if not app_was_running or not tunnel_was_running or not portfolio_was_running:
    time.sleep(10)

# 4. Read current URLs and notify
try:
    with open('/home/nishan/tunnel.log', 'r') as f:
        log = f.read()
    if "https://" in log:
        for line in log.splitlines():
            if "trycloudflare.com" in line:
                sub = line[line.find("https://"):].split()[0]
                send_telegram(f"🚀 **The Bench URL:**\\n{{sub}}")
                break
except: pass

try:
    with open('/home/nishan/tunnel_portfolio.log', 'r') as f:
        log_p = f.read()
    if "https://" in log_p:
        for line in log_p.splitlines():
            if "trycloudflare.com" in line:
                sub = line[line.find("https://"):].split()[0]
                send_telegram(f"🎨 **Portfolio URL:**\\n{{sub}}")
                break
except: pass
"""

    print("Overwriting monitor script to include Portfolio tunnel checks...")
    write_cmd = f'cat > /home/nishan/monitor_tunnels.py << "EOF"\n{monitor_script_content}\nEOF'
    ssh.exec_command(write_cmd)

    print("Triggering check for both tunnels...")
    ssh.exec_command("/home/nishan/flask_replica/venv/bin/python3 /home/nishan/monitor_tunnels.py")

    ssh.close()
    print("Updates complete.")

if __name__ == "__main__":
    update_monitor()
