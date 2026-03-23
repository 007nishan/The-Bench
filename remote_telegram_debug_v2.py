import paramiko
import time

def debug_telegram():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"
    
    bot_token = "8571904781:AAEhaViQiEihWOHShd0a0ywJ0BMufSh13p8"
    chat_id = "8687680759"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)

    # Rewrite monitor_tunnels.py to log Telegram response
    monitor_script_content = f"""import subprocess
import time
import requests
import os

TOKEN = "{bot_token}"
CHAT_ID = "{chat_id}"

# Clear debug log
with open('/home/nishan/telegram_debug.log', 'w') as f: f.write("--- Start Telegram Debug --- \n")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{{TOKEN}}/sendMessage"
    try:
        r = requests.get(url, params={{"chat_id": CHAT_ID, "text": msg}}, timeout=10)
        with open('/home/nishan/telegram_debug.log', 'a') as f:
            f.write(f"Msg: {{msg}} \\nResponse: {{r.status_code}} - {{r.text}} \\n")
    except Exception as e:
        with open('/home/nishan/telegram_debug.log', 'a') as f:
            f.write(f"Exception: {{e}} \\n")

def check_process(name, restart_cmd):
    res = subprocess.run("ps aux | grep [" + name[0] + "]" + name[1:], shell=True, capture_output=True, text=True)
    if name not in res.stdout:
        subprocess.run(restart_cmd, shell=True)
        return False
    return True

# 1. Check Flask App
flask_restart = "cd /home/nishan/flask_replica && source venv/bin/activate && nohup python app.py > app.log 2>&1 &"
check_process("app.py", flask_restart)

# 2. Check Tunnel for Bench
tunnel_restart = "nohup /home/nishan/cloudflared tunnel --url http://127.0.0.1:5000 > /home/nishan/tunnel.log 2>&1 &"
check_process("cloudflared tunnel --url http://127.0.0.1:5000", tunnel_restart)

send_telegram("🚀 **The Bench Direct Debug Trigger**")
"""

    print("Writing debug monitor script to remote server...")
    write_cmd = f'cat > /home/nishan/monitor_tunnels.py << "EOF"\n{monitor_script_content}\nEOF'
    ssh.exec_command(write_cmd)
    time.sleep(2)

    # Run it
    print("Running debug monitor...")
    ssh.exec_command("/home/nishan/flask_replica/venv/bin/python3 /home/nishan/monitor_tunnels.py")
    time.sleep(3)

    # Read log
    print("Reading Debug Log:")
    stdin, stdout, stderr = ssh.exec_command("cat /home/nishan/telegram_debug.log")
    print(stdout.read().decode('utf-8'))

    ssh.close()

if __name__ == "__main__":
    debug_telegram()
