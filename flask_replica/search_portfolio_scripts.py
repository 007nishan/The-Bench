import paramiko
import sys

def search():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    commands = [
        "ls -la /home/nishan/portfolio",
        "find /home/nishan/portfolio -name '*.py' | grep -i -E 'fcc|sync|update|cron|app'",
        "cat /home/nishan/portfolio/app.py | grep -i -E 'fcc|sync'"
    ]

    for cmd in commands:
        print(f"\n--- Output of: {cmd} ---")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode('utf-8'))
        print(stderr.read().decode('utf-8'))

    ssh.close()

if __name__ == "__main__":
    search()
