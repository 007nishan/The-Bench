import paramiko
import os

def sync():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {host}...")
    ssh.connect(host, username=user, password=password)

    sftp = ssh.open_sftp()
    
    local_base = "c:\\Users\\NISHAN\\Desktop\\Test Folder\\The Bench\\flask_replica"
    remote_base = "/home/nishan/flask_replica"

    files_to_sync = [
        "app.py",
        "models.py",
        "templates/index.html",
        "templates/dashboard.html"
    ]

    for f in files_to_sync:
        l_path = os.path.join(local_base, f.replace('/', '\\'))
        r_path = remote_base + '/' + f
        print(f"Uploading {l_path} -> {r_path}")
        sftp.put(l_path, r_path)

    sftp.close()

    # Restart app: assumption is it runs via screen or nohup, we find and kill old, and standard trigger restarts it,
    # or we just trigger the restart here!
    print("Killing existing Flask threads on remote...")
    ssh.exec_command("pkill -9 -f 'python app.py'")
    ssh.exec_command("pkill -9 -f 'python3 app.py'")
    
    print("Starting app on remote...")
    # Run in background via nohup or screen
    stdin, stdout, stderr = ssh.exec_command("cd /home/nishan/flask_replica && nohup python3 app.py > app_log.txt 2>&1 &")
    
    ssh.close()
    print("Sync and restart complete.")

if __name__ == "__main__":
    sync()
