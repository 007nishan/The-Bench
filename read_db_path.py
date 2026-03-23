import paramiko

def read_db_path():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)

    # 1. Read .env
    stdin, stdout, stderr = ssh.exec_command("cat /home/nishan/flask_replica/.env")
    env_content = stdout.read().decode('utf-8')
    print("--- .env Content ---")
    print(env_content)

    # 2. Read app.py database config section
    stdin, stdout, stderr = ssh.exec_command("grep -n 'SQLALCHEMY_DATABASE_URI' /home/nishan/flask_replica/app.py")
    app_content = stdout.read().decode('utf-8')
    print("--- app.py DB config ---")
    print(app_content)

    ssh.close()

if __name__ == "__main__":
    read_db_path()
