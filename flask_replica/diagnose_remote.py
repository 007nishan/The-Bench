import paramiko
import sys

def diagnose():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    print(f"Connecting to {user}@{host} for diagnosis...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    commands = [
        "ls -l cloudflared",
        "file cloudflared",
        "ls -l /home/nishan/tunnel.log",
        "cat /home/nishan/tunnel.log",
        "ps aux | grep -E '(cloudflared|app.py)'"
    ]

    for cmd in commands:
        print(f"\n--- Output of: {cmd} ---")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode('utf-8'))
        print(stderr.read().decode('utf-8'))

    ssh.close()

if __name__ == "__main__":
    diagnose()
