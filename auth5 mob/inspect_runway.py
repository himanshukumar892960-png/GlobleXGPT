from runwayml import RunwayML
import os
from dotenv import load_dotenv

load_dotenv()

client = RunwayML(api_key=os.getenv("RUNWAYML_API_KEY"))

print("Methods in client:")
for attr in dir(client):
    if not attr.startswith("_"):
        print(f" - {attr}")

print("\nMethods in client.image_to_video:")
for attr in dir(client.image_to_video):
    if not attr.startswith("_"):
        print(f" - {attr}")

# Try to find text-to-video if it exists
if hasattr(client, 'text_to_video'):
    print("\nMethods in client.text_to_video:")
    for attr in dir(client.text_to_video):
        if not attr.startswith("_"):
            print(f" - {attr}")
else:
    print("\nclient.text_to_video does NOT exist.")
