import paramiko
import sys

def remote_curl():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    cmd = "curl http://127.0.0.1:5000"
    print(f"Executing: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    print("\n--- CURL OUT ---")
    print(stdout.read().decode('utf-8'))
    print("\n--- CURL ERR ---")
    print(stderr.read().decode('utf-8'))

    ssh.close()

if __name__ == "__main__":
    remote_curl()
