import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"Testing connectivity with key: {key[:15]}...")

try:
    client = create_client(url, key)
    # Try a simple read. Even if 'nonexistent_table' doesn't exist, 
    # a valid key should return a 404 or specific error, NOT a 400/401 generic auth failure.
    # Actually, let's try to list something that might exist or just check health?
    # RLS usually blocks reads on unknown tables.
    
    print("Attempting to access a nonexistent table to check Auth validity...")
    try:
        res = client.table('nonexistent_table').select('*').limit(1).execute()
        print(f"Result: {res}")
    except Exception as e:
        print(f"Read Error: {repr(e)}")
        # If the error is 'relation "public.nonexistent_table" does not exist', then AUTH worked!
        # If the error is 'JWT invalid' or 'API key not found', then AUTH failed.

except Exception as e:
    print(f"Initialization Error: {e}")
