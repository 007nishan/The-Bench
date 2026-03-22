import paramiko
import sys
import time

def start_robust():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    print("Killing existing cloudflared processes...")
    ssh.exec_command("pkill -9 -f cloudflared")
    time.sleep(2)

    print("Cleaning up old logs...")
    # Use && to ensure order
    ssh.exec_command("rm -f /home/nishan/tunnel.log /home/nishan/tunnel_portfolio.log && sleep 1")
    time.sleep(2)

    # Use setsid to fully detach from the SSH session session
    cmd1 = "setsid /home/nishan/cloudflared tunnel --url http://127.0.0.1:5000 > /home/nishan/tunnel.log 2>&1"
    cmd2 = "setsid /home/nishan/cloudflared tunnel --url http://127.0.0.1:80 > /home/nishan/tunnel_portfolio.log 2>&1"

    print("Starting Bench Tunnel...")
    ssh.exec_command(cmd1)
    time.sleep(2)

    print("Starting Portfolio Tunnel...")
    ssh.exec_command(cmd2)
    
    print("Waiting for new URLs to populate...")
    time.sleep(15)

    print("\n--- NEW TUNNEL URLs ---")
    
    stdin, stdout, stderr = ssh.exec_command("cat /home/nishan/tunnel.log | grep -a trycloudflare.com")
    print("Bench URL:", stdout.read().decode('utf-8').strip())

    stdin, stdout, stderr = ssh.exec_command("cat /home/nishan/tunnel_portfolio.log | grep -a trycloudflare.com")
    print("Portfolio URL:", stdout.read().decode('utf-8').strip())

    # Double check running count
    print("\n--- Verification ---")
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep [c]loudflared")
    print(stdout.read().decode('utf-8').strip())

    ssh.close()

if __name__ == "__main__":
    start_robust()
