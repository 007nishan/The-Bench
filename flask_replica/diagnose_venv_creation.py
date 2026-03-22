import paramiko
import sys

def diagnose_venv():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    cmd = "cd /home/nishan/flask_replica && rm -rf venv && python3 -m venv venv"
    print(f"Executing over SSH: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    print("\n--- VENV STDOUT ---")
    print(stdout.read().decode('utf-8'))
    print("\n--- VENV STDERR ---")
    print(stderr.read().decode('utf-8'))

    ssh.close()

if __name__ == "__main__":
    diagnose_venv()
