import paramiko

def read_live():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)

    commands = [
        "cat /home/nishan/tunnel.log | grep -a trycloudflare.com | tail -n 1",
        "cat /home/nishan/tunnel_portfolio.log | grep -a trycloudflare.com | tail -n 1"
    ]

    print("Fetching final URLs:")
    with open("final_links.txt", "w", encoding="utf-8") as f:
        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            f.write(stdout.read().decode('utf-8', errors='replace'))

    ssh.close()

if __name__ == "__main__":
    read_live()
