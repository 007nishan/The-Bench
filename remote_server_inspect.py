import paramiko
import sys

def inspect_remote():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    print(f"Connecting to remote server {host}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, username=user, password=password, timeout=10)
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    commands = [
        "echo '--- Home Files ---'",
        "ls -la /home/nishan",
        "echo '--- Checking for existing Python/Flask processes ---'",
        "ps aux | grep -v grep | grep -E 'python|flask'",
        "echo '--- Checking for .env or configs in possible app folders ---'",
        "find /home/nishan -maxdepth 3 -name '.env' -o -name 'config.*' 2>/dev/null",
        "echo '--- Checking cron jobs ---'",
        "crontab -l 2>/dev/null || echo 'No crontab'"
    ]

    for cmd in commands:
        print(f"\nRunning command: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read().decode('utf-8')
        err = stderr.read().decode('utf-8')
        if out: print("Output:\n" + out.strip())
        if err: print("Error:\n" + err.strip())

    ssh.close()

if __name__ == "__main__":
    inspect_remote()
