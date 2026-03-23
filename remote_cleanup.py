import paramiko

def remote_cleanup():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)

    # 1. Scripts to preserve in /home/nishan
    # - cloudflared
    # - monitor_tunnels.py
    # - tunnel.log
    # - tunnel_portfolio.log
    
    # Scripts to preserve in /home/nishan/flask_replica
    # We will use python's find / rm commands on the server to keep EXACT matches.
    
    keep_list = [
        "app.py", "auth.py", "case_manager.py", "models.py", "rag_engine.py", 
        "requirements.txt", "templates", "static", ".env", "instance", "venv",
        "cloudflared_linux", "app.log", "init_db.py", "__pycache__"
    ]

    print("Cleaning remote server folder `/home/nishan/flask_replica`...")
    
    # Commands to execute on server inside the folder
    cleanup_cmd = f"""
    cd /home/nishan/flask_replica
    for item in * .*; do
        if [[ "$item" == "." ]] || [[ "$item" == ".." ]]; then
            continue
        fi
        matched=0
        for keep in {" ".join(keep_list)}; do
            if [[ "$item" == "$keep" ]]; then
                matched=1
                break
            fi
        done
        if [[ $matched -eq 0 ]]; then
            echo "Deleting: $item"
            rm -rf "$item"
        fi
    done
    """
    
    stdin, stdout, stderr = ssh.exec_command(cleanup_cmd)
    print(stdout.read().decode('utf-8'))
    print(stderr.read().decode('utf-8'))
    
    print("\nListing remaining files:")
    stdin, stdout, stderr = ssh.exec_command("ls -la /home/nishan/flask_replica")
    print(stdout.read().decode('utf-8'))

    ssh.close()

if __name__ == "__main__":
    remote_cleanup()
