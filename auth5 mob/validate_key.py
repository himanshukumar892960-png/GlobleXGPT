import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("SUPABASE_KEY")

print("\n" + "="*50)
print("Checking SUPABASE_KEY format...")
print(f"Current Key in .env: {key}")

if key.startswith("sb_publishable"):
    print("\n❌ CRITICAL ISSUE DETECTED:")
    print("The key you are using ('sb_publishable_...') is a PUBLISHABLE TOKEN (possibly from a different service or an older legacy format).")
    print("Supabase Python Client requires the 'ANON' key which is a JWT.")
    print("\n✅ IT SHOULD LOOK LIKE THIS: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    print("\nPLEASE DO THIS:")
    print("1. Go to Supabase Dashboard > Project Settings > API")
    print("2. Copy the 'anon' public key")
    print("3. Paste it effectively into .env")
elif not key.startswith("ey"):
    print("\n❌ WARNING:")
    print("The key does not start with 'ey'. Valid Supabase JWTs (anon keys) usually start with 'ey'.")
else:
    print("\n✅ Key format looks correct (starts with 'ey').")

print("="*50 + "\n")
