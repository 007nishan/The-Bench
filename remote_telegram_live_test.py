import paramiko

def diagnose():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"
    
    bot_token = "8571904781:AAEhaViQiEihWOHShd0a0ywJ0BMufSh13p8"
    chat_id = "8687680759"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)

    # Trigger a Telegram message raw inside the venv and get response
    test_cmd = (
        f"cd /home/nishan/flask_replica && "
        f"source venv/bin/activate && "
        f"python3 -c \"import requests; r=requests.get('https://api.telegram.org/bot{bot_token}/sendMessage', params={{'chat_id': '{chat_id}', 'text': '🛠️ test-message'}}); print('API_RESPONSE:', r.status_code, r.text)\""
    )

    print("Running raw Telegram API test on remote server...")
    stdin, stdout, stderr = ssh.exec_command(test_cmd)
    
    with open("telegram_live_response.txt", "w", encoding="utf-8") as f:
        f.write("--- STDOUT ---\n")
        f.write(stdout.read().decode('utf-8', errors='replace'))
        f.write("\n--- STDERR ---\n")
        f.write(stderr.read().decode('utf-8', errors='replace'))

    print("Results saved to telegram_live_response.txt")
    ssh.close()

if __name__ == "__main__":
    diagnose()
