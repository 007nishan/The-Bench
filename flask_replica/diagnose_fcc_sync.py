import paramiko
import sys

def diagnose_fcc():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    commands = [
        "crontab -l",
        "ls -la /home/nishan",
        "cat /home/nishan/.bash_history | grep -i -E 'fcc|sync|portfolio' | tail -n 20"
    ]

    for cmd in commands:
        print(f"\n--- Output of: {cmd} ---")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode('utf-8'))
        print(stderr.read().decode('utf-8'))

    ssh.close()

if __name__ == "__main__":
    diagnose_fcc()
