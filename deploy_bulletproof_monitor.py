import paramiko
import time
import sys

def deploy():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)

    sftp = ssh.open_sftp()
    
    script = """
import subprocess
import time
import requests
import os

TOKEN = "8571904781:AAEhaViQiEihWOHShd0a0ywJ0BMufSh13p8"
CHAT_ID = "8687680759"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    # No try-except: let it crash and print traceback so we can fix it!
    r = requests.get(url, params={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    print(f"Telegram sent. Status: {r.status_code}, Response: {r.text}")

def check_process(name, restart_cmd):
    res = subprocess.run("ps aux | grep [" + name[0] + "]" + name[1:], shell=True, capture_output=True, text=True)
    if name not in res.stdout:
        subprocess.run(restart_cmd, shell=True)
        return False
    return True

# 1. Check Flask App
flask_restart = "cd /home/nishan/flask_replica && source venv/bin/activate && nohup python app.py > app_log.txt 2>&1 &"
app_was_running = check_process("app.py", flask_restart)

# 2. Check Tunnel for Bench
tunnel_restart = "nohup /home/nishan/cloudflared tunnel --url http://127.0.0.1:5000 > /home/nishan/tunnel.log 2>&1 &"
tunnel_was_running = check_process("cloudflared tunnel --url http://127.0.0.1:5000", tunnel_restart)

# 3. Check Tunnel for Portfolio 
portfolio_tunnel_restart = "nohup /home/nishan/cloudflared tunnel --url http://127.0.0.1:80 > /home/nishan/tunnel_portfolio.log 2>&1 &"
portfolio_was_running = check_process("cloudflared tunnel --url http://127.0.0.1:80", portfolio_tunnel_restart)

def get_url(log_path):
    print(f"Polling {log_path} for active URL...")
    for _ in range(25): # Polling 25 times * 3s = 75s grace period
        try:
            with open(log_path, 'r') as f:
                log = f.read()
            if "trycloudflare.com" in log:
                for line in reversed(log.splitlines()):
                    if "trycloudflare.com" in line:
                        idx = line.find("https://")
                        sub = line[idx:].split()[0]
                        print(f"Parsed FROM {log_path}: {sub}")
                        return sub
        except Exception: pass
        time.sleep(3)
    print(f"Timeout trying to read URL from {log_path}")
    return None

bench_url = get_url('/home/nishan/tunnel.log')
if bench_url:
    send_telegram(f"🚀 **The Bench URL:**\\n{bench_url}")

port_url = get_url('/home/nishan/tunnel_portfolio.log')
if port_url:
    send_telegram(f"🎨 **Portfolio URL:**\\n{port_url}")

send_telegram("✅ **Hourly Automation Triggered**")
print("Executed bulletproof monitor script with wait grace polling.")
"""
    with sftp.open("/home/nishan/monitor_tunnels_safe.py", "w") as f:
        f.write(script)
    sftp.close()

    # Overwrite the original
    ssh.exec_command("mv /home/nishan/monitor_tunnels_safe.py /home/nishan/monitor_tunnels.py")
    
    # Run a fresh trigger and cleanup sequence to execute it right now!
    print("Flushing older duplicate processes on remote server...")
    ssh.exec_command("pkill -9 -f 'cloudflared'")
    time.sleep(2)
    ssh.exec_command("rm -f /home/nishan/tunnel.log /home/nishan/tunnel_portfolio.log")
    
    print("Executing updated monitor_tunnels.py SYNCHRONOUSLY to capture live trace...")
    stdin, stdout, stderr = ssh.exec_command("python3 /home/nishan/monitor_tunnels.py")
    
    out = stdout.read().decode('utf-8')
    err = stderr.read().decode('utf-8')

    print("--- Remote Monitor Output ---")
    print(out)
    if err:
        print("--- Errors ---")
        print(err)

    print("Deployment triggered inside continuous task buffer.")
    ssh.close()

if __name__ == "__main__":
    deploy()
