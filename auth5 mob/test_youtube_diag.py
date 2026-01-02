import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_youtube_api():
    api_key = os.getenv("YOUTUBE_API_KEY")
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q=test&key={api_key}"
    
    print("--- Testing YouTube API without Referer ---")
    response = requests.get(url)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    print("\n--- Testing YouTube API with Referer (localhost) ---")
    headers = {"Referer": "http://localhost:5000"}
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test_youtube_api()
