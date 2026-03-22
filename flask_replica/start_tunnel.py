import subprocess
import time
import sys
import os
import re

def run_tunnel():
    print("Starting Flask app in background...")
    app_process = subprocess.Popen([sys.executable, "app.py"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
    
    time.sleep(3) # Wait for app to start
    
    print("Starting Cloudflare Tunnel...")
    tunnel_process = subprocess.Popen(["cloudflared.exe", "tunnel", "--url", "http://127.0.0.1:5000"],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     text=True)
    
    url = None
    print("Waiting for tunnel URL...")
    # Read stderr stream as cloudflared logs output there
    while True:
        line = tunnel_process.stderr.readline()
        if not line:
            break
        print(line.strip())
        
        # Look for the trycloudflare URL
        if ".trycloudflare.com" in line:
            match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
            if match:
                url = match.group(0)
                print(f"\n✅ TUNNEL URL FOUND: {url}\n")
                with open("TUNNEL_URL.txt", "w") as f:
                    f.write(url)
                break
                
    if url:
        print("Tunnel is active. Press CTRL+C in this terminal to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping...")
    else:
        print("Failed to find tunnel URL in output.")
        
    tunnel_process.terminate()
    app_process.terminate()

if __name__ == "__main__":
    run_tunnel()
