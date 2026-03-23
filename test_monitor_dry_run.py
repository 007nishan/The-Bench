import paramiko

def dry_run():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)

    # We can fetch the parsing block from monitor_tunnels.py and run it with print statements
    script = """
import requests

def debug_print(msg):
    print(f"DEBUG_MSG: {msg}")

# Bench
try:
    with open('/home/nishan/tunnel.log', 'r') as f:
        log = f.read()
    if 'https://' in log:
        found = False
        for line in reversed(log.splitlines()):
            if 'trycloudflare.com' in line:
                idx = line.find('https://')
                sub = line[idx:].split()[0]
                debug_print(f"Found Bench Link: {sub}")
                found = True
                break
        if not found:
            debug_print("No trycloudflare.com found in Bench log lines")
    else:
        debug_print("No https:// found in Bench log")
except Exception as e:
    debug_print(f"Bench exception: {e}")

# Portfolio
try:
    with open('/home/nishan/tunnel_portfolio.log', 'r') as f:
        log_p = f.read()
    if 'https://' in log_p:
        found_p = False
        for line in reversed(log_p.splitlines()):
            if 'trycloudflare.com' in line:
                idx = line.find('https://')
                sub = line[idx:].split()[0]
                debug_print(f"Found Portfolio Link: {sub}")
                found_p = True
                break
        if not found_p:
            debug_print("No trycloudflare.com found in Portfolio log lines")
    else:
        debug_print("No https:// found in Portfolio log")
except Exception as e:
    debug_print(f"Portfolio exception: {e}")
"""
    sftp = ssh.open_sftp()
    with sftp.open("/home/nishan/dry_run_monitor.py", "w") as f:
        f.write(script)
    sftp.close()

    stdin, stdout, stderr = ssh.exec_command("python3 /home/nishan/dry_run_monitor.py")
    out = stdout.read().decode('utf-8')
    print("--- Dry Run Output ---")
    print(out)

    ssh.close()

if __name__ == "__main__":
    dry_run()
