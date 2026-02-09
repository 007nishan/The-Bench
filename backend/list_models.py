
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

def list_models():
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            models = response.json().get('models', [])
            for m in models:
                if 'generateContent' in m.get('supportedGenerationMethods', []):
                    print(f"Name: {m['name']}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    list_models()
