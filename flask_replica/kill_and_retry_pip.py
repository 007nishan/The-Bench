import paramiko
import sys

def retry_pip():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    # 1. Kill previous hanging tests
    ssh.exec_command("pkill -9 -f pip3")
    
    # 2. Run with --no-input and --verbose
    cmd = "cd /home/nishan/flask_replica && source venv/bin/activate && pip3 install -r requirements.txt --no-input"
    print(f"Executing: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    print("\n--- PIP STDOUT ---")
    print(stdout.read().decode('utf-8'))
    print("\n--- PIP STDERR ---")
    print(stderr.read().decode('utf-8'))

    ssh.close()

if __name__ == "__main__":
    retry_pip()
