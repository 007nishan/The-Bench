
import requests

def test_rag():
    payload = {
        "user_role": "accused",
        "query_text": "What is our main vulnerability regarding the delay?"
    }
    
    try:
        print("Sending request to /chat/strategy...")
        response = requests.post("http://localhost:8000/chat/strategy", json=payload, timeout=20)
        print("Status Code:", response.status_code)
        print("Response:", response.json())
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_rag()
