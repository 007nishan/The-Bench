
import requests

def upload_secret():
    payload = {
        "user_role": "accuser",
        "doc_id": "secret_email_001",
        "content": "CONFIDENTIAL: The defendant privately admitted in an email on Jan 1st that they missed the delivery deadline due to internal negligence, not force majeure."
    }
    
    try:
        response = requests.post("http://localhost:8000/ingest_document", json=payload)
        print(response.json())
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    upload_secret()
