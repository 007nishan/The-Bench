import paramiko
import sys

def setup_cron():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    # 1. Create the cron helper script on the server
    helper_script = """import datetime
from fcc_sync import fetch_challenge, upsert_challenge
from app import app

with app.app_context():
    today = datetime.date.today().strftime('%Y-%m-%d')
    print(f"--- {datetime.datetime.now()} ---")
    print(f"Syncing FCC for date: {today}")
    data = fetch_challenge(today)
    if data:
        action, date_str = upsert_challenge(data)
        print(f"Action: {action}, Date: {date_str}")
    else:
        print("No challenge data found for today's date from FCC API.")
"""
    
    # Escape single quotes in helper_script for safe bash output
    escaped_script = helper_script.replace("'", "'\\''")
    
    write_cmd = f"cat > /home/nishan/portfolio/cron_fcc_sync.py << 'EOF'\n{helper_script}\nEOF"
    ssh.exec_command(write_cmd)
    
    # 2. Add to Crontab (Run daily at 1:00 AM)
    cron_job = "0 1 * * * cd /home/nishan/portfolio && /home/nishan/portfolio/venv/bin/python3 cron_fcc_sync.py >> /home/nishan/portfolio/fcc_sync.log 2>&1"
    
    install_cron = f'(crontab -l 2>/dev/null; echo "{cron_job}") | crontab -'
    stdin, stdout, stderr = ssh.exec_command(install_cron)
    
    print("\n--- Installation Log ---")
    print(stdout.read().decode('utf-8'))
    print(stderr.read().decode('utf-8'))

    # 3. Verify
    stdin, stdout, stderr = ssh.exec_command("crontab -l")
    print("\n--- Verification: Current Crontab ---")
    print(stdout.read().decode('utf-8'))

    # 4. Trigger it once right now to sync today!
    print("Triggering sync for today right now...")
    ssh.exec_command("cd /home/nishan/portfolio && /home/nishan/portfolio/venv/bin/python3 cron_fcc_sync.py >> /home/nishan/portfolio/fcc_sync.log 2>&1")

    ssh.close()

if __name__ == "__main__":
    setup_cron()
