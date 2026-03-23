import paramiko

def trigger():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)

    print("Running monitor_tunnels.py...")
    # Trigger the full monitor update which usually announces to bot and prints URLs
    stdin, stdout, stderr = ssh.exec_command("python3 /home/nishan/monitor_tunnels.py")
    out = stdout.read().decode('utf-8')
    err = stderr.read().decode('utf-8')
    
    print("--- Monitor Output ---")
    print(out)
    print("--- Monitor Errors ---")
    print(err)

    ssh.close()

if __name__ == "__main__":
    trigger()
