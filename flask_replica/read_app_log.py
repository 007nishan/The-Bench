import paramiko
import sys

def read_log():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    cmd = "cat /home/nishan/flask_replica/app_output.log"
    print(f"Reading log: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    print("\n--- APP LOG OUTPUT ---")
    print(stdout.read().decode('utf-8'))
    print("\n--- APP LOG ERRORS ---")
    print(stderr.read().decode('utf-8'))

    ssh.close()

if __name__ == "__main__":
    read_log()
