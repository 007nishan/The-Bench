import paramiko
import sys

def read():
    # Reconfigure stdout to support emojis on windows terminal
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)

    stdin, stdout, stderr = ssh.exec_command("cat /home/nishan/monitor_tunnels.py")
    content = stdout.read().decode('utf-8')
    print("--- monitor_tunnels.py Content ---")
    print(content)

    ssh.close()

if __name__ == "__main__":
    read()
