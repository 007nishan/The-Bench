import paramiko, time
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.150', username='nishan', password='6WKW5_3w2w5121')

remote_dest = "/home/nishan/flask_replica"
remote_zip = "/home/nishan/flask_replica.zip"

print("Extracting...")
stdin, stdout, stderr = ssh.exec_command(f"unzip -o {remote_zip} -d {remote_dest}")
print(stdout.read().decode())

print("Fixing line endings and start...")
ssh.exec_command(f"sed -i 's/\r$//' {remote_dest}/start_app.sh")
ssh.exec_command(f"chmod +x {remote_dest}/start_app.sh")

print("Initializing DB...")
stdin, stdout, stderr = ssh.exec_command(f"cd {remote_dest} && rm -f the_bench.db && rm -rf instance && mkdir -p instance && python3 init_db.py")
print(stdout.read().decode())

print("Starting App...")
stdin, stdout, stderr = ssh.exec_command(f"bash {remote_dest}/start_app.sh")
print(stdout.read().decode())

print("Triggering Cloudflare...")
ssh.exec_command("nohup /home/nishan/cloudflared tunnel --url http://127.0.0.1:5000 > /home/nishan/tunnel.log 2>&1 &")

ssh.close()
print("Manual Deploy trigger successful.")
