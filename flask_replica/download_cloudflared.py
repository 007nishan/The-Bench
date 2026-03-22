import requests

url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
output_path = "cloudflared.exe"

print(f"Downloading {url} to {output_path}...")
try:
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print("Download complete!")
except Exception as e:
    print(f"Download failed: {e}")
