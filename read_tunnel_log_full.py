import paramiko

def read():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)

    # 1. Read the file
    stdin, stdout, stderr = ssh.exec_command("cat /home/nishan/tunnel.log")
    content = stdout.read().decode('utf-8')
    print("--- /home/nishan/tunnel.log Full ---")
    print(content)

    print("--- monitor_tunnels.py parser fix ---")

    ssh.close()

if __name__ == "__main__":
    read()
