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
    print("--- /home/nishan/tunnel.log ---")
    print(content[-500:]) # last 500 chars

    stdin, stdout, stderr = ssh.exec_command("cat /home/nishan/tunnel_portfolio.log")
    content_p = stdout.read().decode('utf-8')
    print("--- /home/nishan/tunnel_portfolio.log ---")
    print(content_p[-500:])

    ssh.close()

if __name__ == "__main__":
    read()
