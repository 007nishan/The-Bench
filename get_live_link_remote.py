import paramiko

def get_link():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)

    # Check for active cloudflared processes and their metrics or logs to find the URL
    # Safer: read the output file if monitor_tunnels saves it, or just find cloudflared processes log.
    # In earlier turns, creating a script and searching for .trycloudflare.com was used.
    
    stdin, stdout, stderr = ssh.exec_command("cat /home/nishan/flask_replica/app_log.txt")
    app_log = stdout.read().decode('utf-8')
    
    # Try reading the monitor script logs if they exist
    stdin, stdout, stderr = ssh.exec_command("grep -o 'https://[a-zA-Z0-9.-]*\\.trycloudflare\\.com' /home/nishan/flask_replica/app_log.txt || true")
    links_fallback = stdout.read().decode('utf-8')

    # Another approach: inspect cloudflared output
    stdin, stdout, stderr = ssh.exec_command("cat /home/nishan/monitor_tunnels.py")
    monitor_content = stdout.read().decode('utf-8')
    # Let's see where monitor script stores its outputs!
    
    ssh.close()
    print("--- App Log ---")
    print(app_log[:1000]) # Print first 1000 chars
    print("--- Fallback links ---")
    print(links_fallback)

if __name__ == "__main__":
    get_link()
