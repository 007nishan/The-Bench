import paramiko

def fix_telegram():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)

    commands = [
        "echo '--- 1. Installing requests in remote venv for Monitor script ---'",
        "cd /home/nishan/flask_replica && source venv/bin/activate && pip install requests",
        "echo '--- 2. Triggering Monitor Script ---'",
        "/home/nishan/flask_replica/venv/bin/python3 /home/nishan/monitor_tunnels.py",
        "echo '--- 3. Verifying output / Error messages ---'"
    ]

    for cmd in commands:
        print(f"\nRunning: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode('utf-8', errors='replace'))
        print(stderr.read().decode('utf-8', errors='replace'))

    ssh.close()

if __name__ == "__main__":
    fix_telegram()
