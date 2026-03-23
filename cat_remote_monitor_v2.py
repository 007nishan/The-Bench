import paramiko

def read_remote():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)

    with open("remote_run_results.txt", "w", encoding="utf-8") as f:
        f.write("--- Reading /home/nishan/monitor_tunnels.py ---\n")
        stdin, stdout, stderr = ssh.exec_command("cat /home/nishan/monitor_tunnels.py")
        f.write(stdout.read().decode('utf-8', errors='replace'))
        
        f.write("\n\n--- Testing execution and reading stderr ---\n")
        # Run script
        stdin, stdout, stderr = ssh.exec_command("/home/nishan/flask_replica/venv/bin/python3 /home/nishan/monitor_tunnels.py")
        f.write("STDOUT:\n")
        f.write(stdout.read().decode('utf-8', errors='replace'))
        f.write("\nSTDERR:\n")
        f.write(stderr.read().decode('utf-8', errors='replace'))

    print("Results saved to remote_run_results.txt")
    ssh.close()

if __name__ == "__main__":
    read_remote()
