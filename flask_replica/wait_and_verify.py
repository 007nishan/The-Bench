import paramiko
import sys
import time

def verify():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    print("Waiting for pip3 to finish and app to start up (Max 3 mins)...")
    success = False
    
    for _ in range(36): # 36 * 5s = 180s
        stdin, stdout, stderr = ssh.exec_command("netstat -nlp | grep 5000")
        out = stdout.read().decode('utf-8')
        if out:
            print(f"Success! Port 5000 is listening: {out.strip()}")
            success = True
            break
        
        # Check if pip is still running
        stdin_p, stdout_p, stderr_p = ssh.exec_command("ps aux | grep pip3 | grep -v grep")
        pip_out = stdout_p.read().decode('utf-8')
        if not pip_out:
             # Pip finished! But is port up? Run app manually or check log
             print("Pip finished. Starting app if not running...")
             ssh.exec_command("cd /home/nishan/flask_replica && bash start_app.sh")
             time.sleep(5)
             
        time.sleep(5)

    if success:
        print("Ensuring Cloudflare Tunnel is running...")
        ssh.exec_command("nohup /home/nishan/cloudflared tunnel --url http://127.0.0.1:5000 > /home/nishan/tunnel.log 2>&1 &")
        time.sleep(3)

    ssh.close()
    return success

if __name__ == "__main__":
    if verify():
        print("ALIVE")
    else:
        print("FAILED")
