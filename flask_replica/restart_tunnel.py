import paramiko
import sys
import time

def restart():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    # Kill old tunnel
    print("Killing existing cloudflared process...")
    ssh.exec_command("pkill -f cloudflared")
    time.sleep(2)

    # Start new tunnel
    cmd = "nohup /home/nishan/cloudflared tunnel --url http://127.0.0.1:5000 > /home/nishan/tunnel.log 2>&1 &"
    print(f"Executing: {cmd}")
    ssh.exec_command(cmd)
    
    print("Waiting for logs to populate...")
    time.sleep(10)

    stdin, stdout, stderr = ssh.exec_command("cat /home/nishan/tunnel.log")
    print("\n--- NEW TUNNEL LOG ---")
    print(stdout.read().decode('utf-8'))

    ssh.close()

if __name__ == "__main__":
    restart()
