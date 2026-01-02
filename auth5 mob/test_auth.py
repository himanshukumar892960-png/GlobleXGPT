import os
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

try:
    print("Attempting to create Supabase client...")
    client = create_client(url, key)
    print("Client created successfully.")
    
    print("Attempting dummy sign-in...")
    # This might fail with invalid credentials, but we want to see if the CLIENT/KEY is valid
    res = client.auth.sign_in_with_password({"email": "test@test.com", "password": "password"})
    print("Sign-in result:", res)

except Exception as e:
    error_msg = str(e)
    logger.error(f"SIGNUP ERROR: {error_msg}")
    return jsonify({"error": error_msg}), 500

