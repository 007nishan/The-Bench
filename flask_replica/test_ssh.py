import paramiko
import sys

def test_ssh():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    print(f"Connecting to {user}@{host}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, username=user, password=password, timeout=10)
        print("SUCCESS: SSH Connection Successful!")
        
        # Determine OS
        print("\n--- Testing OS Details ---")
        stdin, stdout, stderr = ssh.exec_command("uname -a")
        uname = stdout.read().decode('utf-8').strip()
        print(f"uname -a: {uname}")
        
        stdin, stdout, stderr = ssh.exec_command("ver")
        ver = stdout.read().decode('utf-8').strip()
        print(f"ver: {ver}")
        
        # Test directory listing to find workspace/home
        stdin, stdout, stderr = ssh.exec_command("ls -la")
        ls_out = stdout.read().decode('utf-8').strip()
        print("\n--- Home Directory Contents (ls) ---")
        print(ls_out if ls_out else "Empty or Windows")
        
        stdin, stdout, stderr = ssh.exec_command("dir")
        dir_out = stdout.read().decode('utf-8').strip()
        print("\n--- Home Directory Contents (dir) ---")
        print(dir_out if dir_out else "Empty or Linux")
        
        ssh.close()
        return True
    except Exception as e:
        print(f"FAIL: Connection Failed: {e}")
        return False

if __name__ == "__main__":
    success = test_ssh()
    sys.exit(0 if success else 1)
