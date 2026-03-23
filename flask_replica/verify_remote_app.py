import paramiko

def verify():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)

    stdin, stdout, stderr = ssh.exec_command("cat /home/nishan/flask_replica/pip_output.log")
    print("\n--- REMOTE PIP LOG ---")
    print(stdout.read().decode('utf-8'))
    print("----------------------\n")

    stdin, stdout, stderr = ssh.exec_command("cat /home/nishan/flask_replica/app_output.log")
    print("\n--- REMOTE APP LOG ---")
    print(stdout.read().decode('utf-8'))
    print("----------------------\n")

    stdin, stdout, stderr = ssh.exec_command("ps aux | grep app.py")
    print("--- PS AUX ---")
    print(stdout.read().decode('utf-8'))
    print("--------------\n")

    ssh.close()

if __name__ == "__main__":
    verify()

