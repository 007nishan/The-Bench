import paramiko
import sys
import time

def fix_remote():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=15)
    
    # 1. Install python3-venv using sudo
    print("Installing python3-venv to remote...")
    cmd_install = f"echo '{password}' | sudo -S apt-get update && echo '{password}' | sudo -S apt-get install -y python3-venv"
    stdin, stdout, stderr = ssh.exec_command(cmd_install)
    print(stdout.read().decode('utf-8'))
    print(stderr.read().decode('utf-8'))

    # 2. Cleanup partial venv if any
    print("Cleaning up partial Venv...")
    commands = [
        "rm -rf /home/nishan/flask_replica/venv",
        "bash /home/nishan/flask_replica/start_app.sh"
    ]
    
    for cmd in commands:
        print(f"Executing: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode('utf-8'))
        time.sleep(2)

    # 3. Wait and verify
    print("Waiting for app to initialize Venv...")
    time.sleep(10) # Give it time to build venv

    print("Checking if port 5000 is listening...")
    stdin, stdout, stderr = ssh.exec_command("netstat -nlp | grep 5000")
    netstat_out = stdout.read().decode('utf-8')
    print(f"Netstat output: {netstat_out}")

    ssh.close()

if __name__ == "__main__":
    fix_remote()
