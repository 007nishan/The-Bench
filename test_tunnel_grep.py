import paramiko

def test():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)

    # Grep in tunnel.log for trycloudflare.com
    stdin, stdout, stderr = ssh.exec_command("grep -o 'https://[a-zA-Z0-9.-]*\\.trycloudflare\\.com' /home/nishan/tunnel.log || echo 'NOT FOUND'")
    out = stdout.read().decode('utf-8')
    print("--- /home/nishan/tunnel.log URL count ---")
    print(out)

    stdin, stdout, stderr = ssh.exec_command("grep -o 'https://[a-zA-Z0-9.-]*\\.trycloudflare\\.com' /home/nishan/tunnel_portfolio.log || echo 'NOT FOUND'")
    out_p = stdout.read().decode('utf-8')
    print("--- /home/nishan/tunnel_portfolio.log URL count ---")
    print(out_p)

    ssh.close()

if __name__ == "__main__":
    test()
