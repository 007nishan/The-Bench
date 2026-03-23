import paramiko, time
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.150', username='nishan', password='6WKW5_3w2w5121')
# Trigger cloudflared in background
ssh.exec_command("nohup /home/nishan/cloudflared tunnel --url http://127.0.0.1:5000 > /home/nishan/tunnel.log 2>&1 &")
time.sleep(10) # Wait for it to fetch banner 
stdin, stdout, stderr = ssh.exec_command("cat /home/nishan/tunnel.log")
print(stdout.read().decode())
ssh.close()
