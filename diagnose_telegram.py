import paramiko

def diagnose_telegram():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"
    
    bot_token = "8571904781:AAEhaViQiEihWOHShd0a0ywJ0BMufSh13p8"
    chat_id = "8687680759"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)

    commands = [
        "echo '--- 1. Fetching URLs from Logs ---'",
        "cat /home/nishan/tunnel.log | grep -a trycloudflare.com | tail -n 3",
        "cat /home/nishan/tunnel_portfolio.log | grep -a trycloudflare.com | tail -n 3",
        "echo '--- 2. Testing Telegram POST from Remote Venv ---'",
        f"cd /home/nishan/flask_replica && source venv/bin/activate && python3 -c \"import requests; r=requests.get('https://api.telegram.org/bot{bot_token}/sendMessage', params={{'chat_id': '{chat_id}', 'text': '🛠️ remote test notification'}}); print(r.text)\""
    ]

    for cmd in commands:
        print(f"\nRunning: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode('utf-8'))

    ssh.close()

if __name__ == "__main__":
    diagnose_telegram()
