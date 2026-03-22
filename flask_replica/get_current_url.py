import paramiko
import sys

def get_url():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    cmd = "cat /home/nishan/tunnel.log | grep -a trycloudflare.com"
    print(f"Executing: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    print("\n--- URL OUT ---")
    print(stdout.read().decode('utf-8'))

    ssh.close()

if __name__ == "__main__":
    get_url()
