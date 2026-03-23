import paramiko

def search():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)

    # Search for any active .trycloudflare.com link in all logs, home directory files, etc.
    # To reduce time/noise, just search in /home/nishan and /tmp
    command = "grep -R -h -o 'https://[a-zA-Z0-9.-]*\\.trycloudflare\\.com' /home/nishan/ 2>/dev/null | sort | uniq"
    stdin, stdout, stderr = ssh.exec_command(command)
    
    links = stdout.read().decode('utf-8')
    err = stderr.read().decode('utf-8')

    print("--- Found Cloudflare Links ---")
    print(links)
    if err:
        print("--- Errors ---")
        print(err)

    ssh.close()

if __name__ == "__main__":
    search()
