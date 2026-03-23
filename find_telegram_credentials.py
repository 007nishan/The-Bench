import paramiko

def search_remote():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)

    commands = [
        "echo '--- Searching for Bot Token in telegram_bridge.py ---'",
        "cat /home/nishan/portfolio/telegram_bridge.py | grep -E 'token|TOKEN|chat|CHAT'",
        "echo '--- Searching for Bot Token in other py files ---'",
        "grep -rnw '/home/nishan/portfolio/' -e 'bot' -e 'token' -e 'API_KEY' --exclude-dir=venv 2>/dev/null | head -n 20"
    ]

    for cmd in commands:
        print(f"\nRunning: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode('utf-8'))

    ssh.close()

if __name__ == "__main__":
    search_remote()
