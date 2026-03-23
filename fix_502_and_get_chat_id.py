import paramiko

def fix_and_get_id():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)

    # 1. Get Admin/Chat ID
    stdin, stdout, stderr = ssh.exec_command("cat /home/nishan/portfolio/admin_id.txt")
    chat_id = stdout.read().decode('utf-8').strip()
    print(f"Chat ID Found: {chat_id}")

    # 2. Reinitialize / Create DB on remote just in case
    print("Re-initializing database on remote server...")
    ssh.exec_command("cd /home/nishan/flask_replica && python3 init_db.py")

    # 3. Start The Bench App in background
    print("Starting Flask App (The Bench) on remote server...")
    # Kill existing if any (just using kill on app.py script)
    ssh.exec_command("pkill -f app.py") 
    # Start fresh
    ssh.exec_command("cd /home/nishan/flask_replica && nohup python3 app.py > app.log 2>&1 &")

    # 4. Verify process started
    import time
    time.sleep(3)
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep [a]pp.py")
    print("Remote Process Status:\n", stdout.read().decode('utf-8'))

    ssh.close()

if __name__ == "__main__":
    fix_and_get_id()
