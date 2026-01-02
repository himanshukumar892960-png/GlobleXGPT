import os
import random
import string
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"URL: {url}")
print(f"KEY: {key}")

if not url or not key:
    print("Missing URL or KEY in .env")
    exit(1)

client = create_client(url, key)

# Generate random email to avoid collision
rand_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
email = f"test_{rand_str}@example.com"
password = "testpassword123"

print(f"Attempting signup for {email}...")

try:
    res = client.auth.sign_up({"email": email, "password": password})
    print("Signup result:", res)
    if res.user:
        print("SUCCESS: User created!")
    else:
        print("FAILED: No user returned (maybe email confirmation required)")

except Exception as e:
    print(f"FULL ERROR: {e}")
    if hasattr(e, 'code'):
         print(f"Error Code: {e.code}")
    if hasattr(e, 'details'):
         print(f"Error Details: {e.details}")
    if hasattr(e, 'message'):
         print(f"Error Message: {e.message}")
