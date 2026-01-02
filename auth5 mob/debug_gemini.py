import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: GEMINI_API_KEY not found in environment.")
else:
    print(f"API Key found (length: {len(api_key)})")
    genai.configure(api_key=api_key)

    print("\n--- Listing Available Models ---")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
    except Exception as e:
        print(f"Error listing models: {e}")

    print("\n--- Testing Generation with gemini-1.5-flash ---")
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello, can you hear me?")
        print(f"Success! Response: {response.text}")
    except Exception as e:
        print(f"Error with gemini-1.5-flash: {e}")

    print("\n--- Testing Generation with gemini-pro ---")
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Hello, can you hear me?")
        print(f"Success! Response: {response.text}")
    except Exception as e:
        print(f"Error with gemini-pro: {e}")
