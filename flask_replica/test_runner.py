import subprocess
import time
import requests
import sys
import os

def run_test():
    print("Starting Flask app...")
    # Start flask app in background
    process = subprocess.Popen([sys.executable, "app.py"], 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE,
                             text=True)
    
    # Wait for app to boot
    time.sleep(5)
    
    if process.poll() is not None:
        print("Flask app crashed on startup:")
        print(process.stderr.read())
        return False
        
    print("Testing health endpoint...")
    try:
        res = requests.get("http://127.0.0.1:5000/api/health", timeout=5)
        print(f"Health Check Status: {res.status_code}")
        print(f"Response: {res.text}")
        if res.status_code == 200:
            print("✅ app.py is running and healthy!")
            process.terminate()
            return True
    except Exception as e:
        print(f"FAIL: Connection failed: {e}")
        # Print anything from stderr to help diagnose
        err = process.stderr.read()
        if err:
            print("App Stderr:")
            print(err)
        return False

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
