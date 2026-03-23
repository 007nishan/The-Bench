import paramiko

def debug_remote():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)

    commands = [
        "echo '--- Checking for Virtualenv ---'",
        "ls -la /home/nishan/flask_replica",
        "echo '--- Reading app.log ---'",
        "cat /home/nishan/flask_replica/app.log",
        "echo '--- Testing startup manually in shell ---'",
        "cd /home/nishan/flask_replica && python3 app.py 2>&1 | head -n 20"
    ]

    for cmd in commands:
        print(f"\nRunning: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode('utf-8', errors='replace'))

    ssh.close()

if __name__ == "__main__":
    debug_remote()
    
