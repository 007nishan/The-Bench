import subprocess
import time
import sys
import re

def run_portfolio_tunnel():
    print("Starting Cloudflare Tunnel for Portfolio (192.168.1.150:80)...")
    # Use standalone binary we downloaded
    tunnel_process = subprocess.Popen(["cloudflared.exe", "tunnel", "--url", "http://192.168.1.150:80"],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     text=True)
    
    url = None
    print("Waiting for Portfolio tunnel URL...")
    # Timeout after 20 seconds
    start_time = time.time()
    
    while (time.time() - start_time) < 20:
        line = tunnel_process.stderr.readline()
        if not line:
            # check stdout just in case
            if tunnel_process.poll() is not None:
                print("Tunnel stopped prematurely.")
                break
            time.sleep(1)
            continue
            
        print(line.strip())
        
        if ".trycloudflare.com" in line:
            match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
            if match:
                url = match.group(0)
                print(f"\n✅ PORTFOLIO TUNNEL URL FOUND: {url}\n")
                with open("PORTFOLIO_URL.txt", "w") as f:
                    f.write(url)
                break
                
    if url:
        print("Portfolio Tunnel is active.")
    else:
        print("Failed to find tunnel URL for portfolio.")

if __name__ == "__main__":
    run_portfolio_tunnel()
