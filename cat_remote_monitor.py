import paramiko

def read_remote():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)

    print("Reading /home/nishan/monitor_tunnels.py:")
    stdin, stdout, stderr = ssh.exec_command("cat /home/nishan/monitor_tunnels.py")
    print(stdout.read().decode('utf-8'))
    
    print("\n--- Testing execution and reading stderr ---")
    stdin, stdout, stderr = ssh.exec_command("/home/nishan/flask_replica/venv/bin/python3 /home/nishan/monitor_tunnels.py")
    print("STDOUT:", stdout.read().decode('utf-8'))
    print("STDERR:", stderr.read().decode('utf-8'))

    ssh.close()

if __name__ == "__main__":
    read_remote()
