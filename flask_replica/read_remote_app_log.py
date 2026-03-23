import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.150', username='nishan', password='6WKW5_3w2w5121')

print("=== app_output.log ===")
stdin, stdout, stderr = ssh.exec_command("cat /home/nishan/flask_replica/app_output.log")
print(stdout.read().decode())

print("=== pip_output.log ===")
stdin, stdout, stderr = ssh.exec_command("cat /home/nishan/flask_replica/pip_output.log")
print(stdout.read().decode())

ssh.close()
