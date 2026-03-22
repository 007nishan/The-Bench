import subprocess
import time
import sys
import re

def start_both():
    print("Starting Flask app (The Bench) in background...")
    app_process = subprocess.Popen([sys.executable, "app.py"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
    
    time.sleep(3) # Wait for app to boot
    
    print("Starting Tunnel 1: The Bench...")
    # Standalone we downloaded
    tunnel1 = subprocess.Popen(["cloudflared.exe", "tunnel", "--url", "http://127.0.0.1:5000"],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             text=True)
    
    print("Starting Tunnel 2: Portfolio...")
    tunnel2 = subprocess.Popen(["cloudflared.exe", "tunnel", "--url", "http://192.168.1.150:80"],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             text=True)
    
    bench_url = None
    portfolio_url = None
    
    print("Polling for URLs from Cloudflare...")
    start_time = time.time()
    
    # Read outputs safely to prevent deadlock
    while (time.time() - start_time) < 30:
        if not bench_url:
            line1 = tunnel1.stderr.readline()
            if line1:
                print(f"[Bench] {line1.strip()}")
                if ".trycloudflare.com" in line1:
                    match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line1)
                    if match:
                        bench_url = match.group(0)
                        print(f"\nFOUND BENCH URL: {bench_url}\n")

        if not portfolio_url:
            line2 = tunnel2.stderr.readline()
            if line2:
                print(f"[Portfolio] {line2.strip()}")
                if ".trycloudflare.com" in line2:
                    match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line2)
                    if match:
                        portfolio_url = match.group(0)
                        print(f"\nFOUND PORTFOLIO URL: {portfolio_url}\n")

        if bench_url and portfolio_url:
            print("\nSUCCESS: BOTH URLs FOUND! Saving to URLS.txt...\n")
            with open("URLS.txt", "w") as f:
                f.write(f"The Bench: {bench_url}\n")
                f.write(f"Portfolio: {portfolio_url}\n")
            break
            
        time.sleep(1)

    if bench_url and portfolio_url:
        print("Tunnels are active. Keep this script running.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping...")
    else:
        print("Failed to start both tunnels in time.")

    tunnel1.terminate()
    tunnel2.terminate()
    app_process.terminate()

if __name__ == "__main__":
    start_both()
