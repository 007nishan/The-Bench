import paramiko

def check_log():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)

    # Cat the end of app_log.txt to find 500 tracebacks
    stdin, stdout, stderr = ssh.exec_command("cat /home/nishan/flask_replica/app_log.txt")
    out = stdout.read().decode('utf-8')
    print("--- Remote App Log ---")
    print(out[-1500:]) # Last 1500 chars

    ssh.close()

if __name__ == "__main__":
    check_log()
