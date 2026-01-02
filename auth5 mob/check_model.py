import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY").strip()
genai.configure(api_key=api_key)

print("Checking for gemini-1.5-flash...")
models = [m.name for m in genai.list_models()]
for m in models:
    if "flash" in m:
        print(f"Found flash model: {m}")

if "models/gemini-1.5-flash" in models:
    print("MATCH FOUND: models/gemini-1.5-flash")
elif "gemini-1.5-flash" in models:
    print("MATCH FOUND: gemini-1.5-flash")
else:
    print("NO MATCH for gemini-1.5-flash")
    print(f"First 10 models: {models[:10]}")
