import paramiko

def read_remote_full():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)

    # Cat the whole file and save locally
    stdin, stdout, stderr = ssh.exec_command("cat /home/nishan/portfolio/telegram_bridge.py")
    content = stdout.read().decode('utf-8', errors='replace')

    with open("telegram_bridge_remote.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("File saved to telegram_bridge_remote.py")
    ssh.close()

if __name__ == "__main__":
    read_remote_full()
