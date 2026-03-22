import paramiko
import sys

def run_test():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    cmd = "cd /home/nishan/portfolio && source venv/bin/activate && python3 test_sync.py"
    print(f"Executing: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    print("\n--- TEST STDOUT ---")
    print(stdout.read().decode('utf-8'))
    print("\n--- TEST STDERR ---")
    print(stderr.read().decode('utf-8'))

    ssh.close()

if __name__ == "__main__":
    run_test()
