import paramiko
import shutil
import os
import time
import sys

def deploy():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"
    
    local_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(local_dir)
    zip_name = "flask_replica.zip"
    zip_path = os.path.join(parent_dir, zip_name)
    
    print(f"Creating ZIP archive of {local_dir}...")
    # Exclude zip itself and temp files if any
    if os.path.exists(zip_path):
        os.remove(zip_path)
    shutil.make_archive(zip_path.replace(".zip", ""), 'zip', local_dir)
    print(f"ZIP created: {zip_path}")

    print(f"Connecting to {user}@{host} via SSH...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=20)
    print("SSH Connected.")

    # SFTP upload
    print("Uploading ZIP archive...")
    sftp = ssh.open_sftp()
    remote_zip = f"/home/{user}/{zip_name}"
    sftp.put(zip_path, remote_zip)
    
    # Upload cloudflared
    print("Uploading cloudflared binary...")
    local_cloudflared = os.path.join(local_dir, "cloudflared_linux")
    remote_cloudflared = f"/home/{user}/cloudflared"
    try:
        sftp.remove(remote_cloudflared)
    except IOError:
        pass
    sftp.put(local_cloudflared, remote_cloudflared)
    
    sftp.close()
    print("Uploads complete!")

    # Commands to execute
    remote_dest = f"/home/{user}/flask_replica"
    commands = [
        f"echo '{password}' | sudo -S apt-get install -y unzip", # Install unzip
        f"mkdir -p {remote_dest}",
        f"unzip -o {remote_zip} -d {remote_dest}",
        f"sed -i 's/\\r$//' {remote_dest}/start_app.sh", # Fix CRLF line endings
        f"chmod +x {remote_dest}/start_app.sh",
        f"cd {remote_dest} && rm -f the_bench.db && rm -rf instance && mkdir -p instance && python3 init_db.py",
        f"bash {remote_dest}/start_app.sh",
        "chmod +x /home/nishan/cloudflared",
        # Start tunnel in background
        "nohup /home/nishan/cloudflared tunnel --url http://127.0.0.1:5000 > /home/nishan/tunnel.log 2>&1 &"
    ]

    print("Executing remote commands...")
    for cmd in commands:
        print(f"Executing: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        # We don't block too long on background commands
        time.sleep(2)

    # Wait for tunnel log to populate
    print("Polling for Tunnel URL...")
    time.sleep(10) # Wait for url generation
    
    stdin, stdout, stderr = ssh.exec_command("cat /home/nishan/tunnel.log")
    log_content = stdout.read().decode('utf-8')
    print("\n--- REMOTE TUNNEL LOG ---")
    print(log_content)
    print("-------------------------\n")

    ssh.close()
    
    if "trycloudflare.com" in log_content:
         print("SUCCESS: Deployment and Tunnel active on your server!")
         return True
    else:
         print("FAIL: Could not verify tunnel URL from log.")
         return False

if __name__ == "__main__":
    success = deploy()
    sys.exit(0 if success else 1)
