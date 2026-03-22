import paramiko
import sys

def list_venv():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    commands = [
        "ls -la /home/nishan/flask_replica/venv",
        "ls -la /home/nishan/flask_replica/venv/bin",
        "ls -la /home/nishan/flask_replica/venv/Scripts" # Just in case
    ]

    for cmd in commands:
        print(f"\n--- Output of: {cmd} ---")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode('utf-8'))
        print(stderr.read().decode('utf-8'))

    ssh.close()

if __name__ == "__main__":
    list_venv()
