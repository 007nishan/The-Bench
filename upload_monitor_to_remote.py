import paramiko

def upload_and_run():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)

    # 1. SFTP Upload
    print("Uploading monitor_tunnels.py via SFTP...")
    sftp = ssh.open_sftp()
    sftp.put("monitor_tunnels_local.py", "/home/nishan/monitor_tunnels.py")
    sftp.close()
    print("Upload complete.")

    # 2. Run script via SSH to verify 
    print("Running monitor_tunnels.py on remote server...")
    stdin, stdout, stderr = ssh.exec_command("/home/nishan/flask_replica/venv/bin/python3 /home/nishan/monitor_tunnels.py")
    
    print("STDOUT:")
    print(stdout.read().decode('utf-8', errors='replace'))
    print("STDERR:")
    print(stderr.read().decode('utf-8', errors='replace'))

    # 3. Schedule Cron (Make sure it's present)
    print("Ensuring Cron scheduling is active (Hourly)...")
    cron_cmd = '(crontab -l 2>/dev/null | grep -v "monitor_tunnels.py"; echo "0 * * * * /home/nishan/flask_replica/venv/bin/python3 /home/nishan/monitor_tunnels.py") | crontab -'
    ssh.exec_command(cron_cmd)

    ssh.close()
    print("Done.")

if __name__ == "__main__":
    upload_and_run()
