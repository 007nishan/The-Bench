import paramiko

def locate_db():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)

    # Use find to locate accurate DB file paths on disk node trig triggers
    stdin, stdout, stderr = ssh.exec_command("find /home/nishan -name 'the_bench.db' 2>/dev/null")
    out = stdout.read().decode('utf-8')
    print("--- Found DB Paths ---")
    print(out)

    ssh.close()

if __name__ == "__main__":
    locate_db()
