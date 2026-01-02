import os
from dotenv import load_dotenv
from runway_client import RunwayClient
from stability_client import StabilityClient

load_dotenv()

def test_stability():
    print("\n--- Testing Stability AI ---")
    key = os.getenv("STABILITY_API_KEY")
    if not key:
        print("Error: No STABILITY_API_KEY found")
        return
    
    client = StabilityClient(key)
    print("Generating image...")
    result = client.generate_image("A beautiful sunset over a calm ocean")
    if result and result.startswith("data:image"):
        print("Success: Image generated (Base64 data received)")
    else:
        print(f"Failed: {result}")

def test_runway():
    print("\n--- Testing RunwayML ---")
    key = os.getenv("RUNWAYML_API_KEY")
    if not key:
        print("Error: No RUNWAYML_API_KEY found")
        return
    
    client = RunwayClient(key)
    print("Generating video (this may take time)...")
    # Using a simple prompt
    result = client.generate_video("A cat playing with a ball")
    if result:
        print(f"Success: Video URL received: {result}")
    else:
        print("Failed to generate video")

if __name__ == "__main__":
    test_stability()
    test_runway()
