import paramiko

def test():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)

    # Execute a python block remotely that tests Telegram with full output capture
    script = """
import requests
TOKEN = "8571904781:AAEhaViQiEihWOHShd0a0ywJ0BMufSh13p8"
CHAT_ID = "8687680759"

url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
try:
    r = requests.get(url, params={'chat_id': CHAT_ID, 'text': '🚨 Test Alert from Server Diagnose Script'}, timeout=10)
    print(f'Status: {r.status_code}')
    print(f'Response: {r.text}')
except Exception as e:
    print(f'Exception: {e}')
"""
    # Write to a temp file and run it
    ssh.exec_command("echo " + repr(script) + " > /home/nishan/test_tele.py")
    stdin, stdout, stderr = ssh.exec_command("python3 /home/nishan/test_tele.py")
    
    out = stdout.read().decode('utf-8')
    err = stderr.read().decode('utf-8')

    print("--- Telegram Diagnose Output ---")
    print(out)
    print("--- Errors ---")
    print(err)

    ssh.close()

if __name__ == "__main__":
    test()
