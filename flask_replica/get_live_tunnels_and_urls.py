import paramiko
import sys
import time

def check_and_restart():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    # 1. Check processes
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep [c]loudflared")
    out = stdout.read().decode('utf-8')
    print("--- Active Tunnels ---")
    print(out.strip() if out else "None")

    processes = out.strip().split("\n") if out else []
    # Count lines with cloudflared
    running_count = len([p for p in processes if "cloudflared" in p])

    # 2. If less than 2, kill and restart both to get fresh sync
    if running_count < 2:
        print("\nTunnels seem dead or missing. Restarting both...")
        ssh.exec_command("pkill -f cloudflared")
        time.sleep(2)

        # Clear logs
        ssh.exec_command("rm -f /home/nishan/tunnel.log /home/nishan/tunnel_portfolio.log")
        
        # Start Bench
        ssh.exec_command("nohup /home/nishan/cloudflared tunnel --url http://127.0.0.1:5000 > /home/nishan/tunnel.log 2>&1 &")
        # Start Portfolio
        ssh.exec_command("nohup /home/nishan/cloudflared tunnel --url http://127.0.0.1:80 > /home/nishan/tunnel_portfolio.log 2>&1 &")
        
        print("Waiting for new URLs...")
        time.sleep(15)

    # 3. Read current URLs
    print("\n--- Current URLs ---")
    
    stdin, stdout, stderr = ssh.exec_command("cat /home/nishan/tunnel.log | grep -a trycloudflare.com")
    print("Bench URL Line:", stdout.read().decode('utf-8').strip())

    stdin, stdout, stderr = ssh.exec_command("cat /home/nishan/tunnel_portfolio.log | grep -a trycloudflare.com")
    print("Portfolio URL Line:", stdout.read().decode('utf-8').strip())

    ssh.close()

if __name__ == "__main__":
    check_and_restart()
