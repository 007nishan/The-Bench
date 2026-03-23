import paramiko
import time

def fix():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)

    # 1. Kill old
    ssh.exec_command("pkill -9 -f 'python3 app.py'")
    ssh.exec_command("pkill -9 -f 'python app.py'")
    time.sleep(1)

    # 2. Restart with VENV
    print("Starting Flask with venv...")
    command = "cd /home/nishan/flask_replica && nohup ./venv/bin/python3 app.py > app_log.txt 2>&1 &"
    ssh.exec_command(command)
    time.sleep(2) # wait for start

    # 3. Read log to confirm start
    stdin, stdout, stderr = ssh.exec_command("cat /home/nishan/flask_replica/app_log.txt")
    log = stdout.read().decode('utf-8')
    print("--- App Log ---")
    print(log[-300:]) # last 300 chars

    # 4. Read monitor log to find Cloudflare links
    # Monitor runs as a cron or service, but it might save links to a file in /home/nishan/
    stdin, stdout, stderr = ssh.exec_command("cat /home/nishan/monitor_tunnels.py")
    # Let's inspect where monitor creates its content!
    # If the user's bot already gets the links hourly, we can just fetch links from active running cloudflared processes!
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep cloudflared")
    out = stdout.read().decode('utf-8')
    print("--- Cloudflared Processes ---")
    print(out)

    ssh.close()

if __name__ == "__main__":
    fix()
