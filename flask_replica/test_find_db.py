import paramiko
import os

def check():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect('192.168.1.150', username='nishan', password='6WKW5_3w2w5121')
        stdin, stdout, stderr = ssh.exec_command("find /home/nishan/flask_replica -name '*.db'")
        print("DB Files Found:")
        print(stdout.read().decode())
    except Exception as e:
        print("Error:", e)
    finally:
        ssh.close()

if __name__ == "__main__":
    check()
 Ath:
