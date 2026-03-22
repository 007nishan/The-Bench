import paramiko
import sys
import time

def manual_start():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    print(f"Connecting to {user}@{host} to test Flask startup...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=15)
    
    # Run the app directly without nohup to see output
    cmd = "cd /home/nishan/flask_replica && source venv/bin/activate && python3 app.py"
    print(f"Executing: {cmd}")
    
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    # Read output with a timeout
    print("\n--- APP STARTUP OUTPUT ---")
    start_time = time.time()
    while (time.time() - start_time) < 15: # Wait up to 15s
        line = stdout.readline()
        if line:
            print(f"[OUT] {line.strip()}")
        else:
            if stdout.channel.exit_status_ready():
                break
            time.sleep(0.5)

    err = stderr.read().decode('utf-8')
    if err:
        print("\n--- APP ERRORS ---")
        print(err)

    ssh.close()

if __name__ == "__main__":
    manual_start()
