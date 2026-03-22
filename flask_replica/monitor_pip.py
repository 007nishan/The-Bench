import paramiko
import sys
import time

def monitor():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    # Run multiple times to see if values change
    print("Monitoring 'pip3' processes on remote...")
    for i in range(5):
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep pip3 | grep -v grep")
        print(f"\n--- Check {i+1} ---")
        out = stdout.read().decode('utf-8')
        if out:
            print(out.strip())
        else:
            print("No pip3 processes found.")
        time.sleep(3)

    ssh.close()

if __name__ == "__main__":
    monitor()
