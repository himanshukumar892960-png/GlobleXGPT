import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY").strip()

try:
    genai.configure(api_key=api_key)
    # Testing with gemini-pro
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say 'Connection Successful'")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"TEST FAILED: {e}")
