import paramiko
import time

def finish_remote():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"
    
    bot_token = "8571904781:AAEhaViQiEihWOHShd0a0ywJ0BMufSh13p8"
    chat_id = "8687680759"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)

    # 1. Start Flask App in background using venv
    print("Starting Flask App (The Bench) with Virtualenv on remote server...")
    ssh.exec_command("pkill -f app.py") 
    time.sleep(2)
    # Commands: navigate, activate, install requirements, start in background
    cmd = (
        "cd /home/nishan/flask_replica && "
        "source venv/bin/activate && "
        "pip install -r requirements.txt flask-cors && "
        "nohup python app.py > app.log 2>&1 &"
    )
    ssh.exec_command(cmd)
    print("Startup sequence triggered. Waiting 10s for PIP / Start...")
    time.sleep(10)

    # 2. Verify process is running
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep [a]pp.py")
    out = stdout.read().decode('utf-8')
    if out:
        print("✅ SUCCESS: Flask App is running on remote server!")
        print(out.strip())
    else:
        print("❌ FAIL: Flask App did not start! Inspecting app.log:")
        stdin, stdout, stderr = ssh.exec_command("cat /home/nishan/flask_replica/app.log")
        print(stdout.read().decode('utf-8'))
        ssh.close()
        return

    # 3. Create monitor script on remote server
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
        send_telegram(f"⚠️ process {{name}} is down. Restarting...")
        subprocess.run(restart_cmd, shell=True)
        return False
    return True

# 1. Check Flask App
flask_restart = "cd /home/nishan/flask_replica && source venv/bin/activate && nohup python app.py > app.log 2>&1 &"
app_was_running = check_process("app.py", flask_restart)

# 2. Check Tunnel for Bench
tunnel_restart = "nohup /home/nishan/cloudflared tunnel --url http://127.0.0.1:5000 > /home/nishan/tunnel.log 2>&1 &"
tunnel_was_running = check_process("cloudflared tunnel --url http://127.0.0.1:5000", tunnel_restart)

# Wait for potential restart to gather links
if not app_was_running or not tunnel_was_running:
    time.sleep(10)

# 3. Read current URLs and notify
try:
    with open('/home/nishan/tunnel.log', 'r') as f:
        log = f.read()
    if "https://" in log:
        for line in log.splitlines():
            if "trycloudflare.com" in line:
                idx = line.find("https://")
                sub = line[idx:].split()[0]
                send_telegram(f"🚀 **The Bench Live URL:**\\n{{sub}}")
                break
except Exception as e:
    send_telegram(f"Error reading tunnel log: {{e}}")
"""

    print("Writing monitor script to remote server...")
    # Escape single quotes and double quotes for shell injection
    safe_content = monitor_script_content.replace('"', '\\"')
    write_cmd = f'cat > /home/nishan/monitor_tunnels.py << "EOF"\n{monitor_script_content}\nEOF'
    ssh.exec_command(write_cmd)

    # 4. Schedule Cron job to run every 3 hours
    print("Scheduling Cron job on remote server...")
    cron_cmd = '(crontab -l 2>/dev/null; echo "0 */3 * * * /home/nishan/flask_replica/venv/bin/python /home/nishan/monitor_tunnels.py") | crontab -'
    ssh.exec_command(cron_cmd)
    print("Cron scheduled.")

    # 5. Run the monitor script once immediately to trigger Telegram notification
    print("Triggering initial Telegram notification...")
    ssh.exec_command("/home/nishan/flask_replica/venv/bin/python /home/nishan/monitor_tunnels.py")

    ssh.close()
    print("All tasks completed on remote server.")

if __name__ == "__main__":
    finish_remote()
