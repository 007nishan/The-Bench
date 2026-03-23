import paramiko

def read_remote():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)

    commands = [
        "cat /home/nishan/portfolio/.env",
        "echo '--- Flask Replica Env ---'",
        "cat /home/nishan/flask_replica/.env"
    ]

    for cmd in commands:
        print(f"\nRunning: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode('utf-8'))

    ssh.close()

if __name__ == "__main__":
    read_remote()
