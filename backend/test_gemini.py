
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
print(f"API Key found: {bool(api_key)}")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("Model initialized.")
    response = model.generate_content("Hello")
    print("Response:", response.text)
except Exception as e:
    print(f"Error: {e}")
