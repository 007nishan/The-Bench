import paramiko
import time

def cleanup():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)

    print("Killing ALL cloudflared processes to clear duplicates...")
    ssh.exec_command("pkill -9 -f 'cloudflared'")
    time.sleep(2) # wait for processes to die

    # Clear old logs so monitor_tunnels is forced to record fresh single links
    ssh.exec_command("rm -f /home/nishan/tunnel.log /home/nishan/tunnel_portfolio.log")
    time.sleep(1)

    print("Triggering monitor_tunnels.py to start fresh tunnels and alert Telegram...")
    # This restarts them with nohup and appends to fresh logs
    ssh.exec_command("python3 /home/nishan/monitor_tunnels.py")
    
    print("Done. Clean monitor reboot complete.")
    ssh.close()

if __name__ == "__main__":
    cleanup()
