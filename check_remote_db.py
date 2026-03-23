import paramiko

def check_db():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)

    print("Checking Database file on remote server:")
    stdin, stdout, stderr = ssh.exec_command("ls -la /home/nishan/flask_replica/instance/the_bench.db")
    out = stdout.read().decode('utf-8')
    err = stderr.read().decode('utf-8')

    if out:
        print("✅ SUCCESS found database file:")
        print(out.strip())
    else:
        print("❌ Database file not found in instance/ folder! Attempting to find elsewhere:")
        stdin, stdout, stderr = ssh.exec_command("find /home/nishan/flask_replica -name '*.db'")
        print(stdout.read().decode('utf-8'))

    ssh.close()

if __name__ == "__main__":
    check_db()
