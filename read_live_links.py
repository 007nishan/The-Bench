import paramiko

def read_live_links():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)

    commands = [
        "echo '--- Bench Tunnel Log (Last 10 Lines with trycloudflare) ---'",
        "cat /home/nishan/tunnel.log | grep trycloudflare.com | tail -n 5",
        "echo '--- Portfolio Tunnel Log (Last 10 Lines with trycloudflare) ---'",
        "cat /home/nishan/tunnel_portfolio.log | grep trycloudflare.com | tail -n 5"
    ]

    for cmd in commands:
        print(f"\nRunning: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode('utf-8'))

    ssh.close()

if __name__ == "__main__":
    read_live_links()
