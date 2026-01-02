import requests
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("NEWS_API_KEY")
url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={key}"

print(f"Testing News API key: {key}")
response = requests.get(url)
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    print("\n--- SUCCESS ---")
    print("The News API key is working correctly!")
    data = response.json()
    print(f"Found {data.get('totalResults')} articles.")
elif response.status_code == 401:
    print("\n--- ERROR ANALYSIS ---")
    print("NewsAPI.org returned 401 Unauthorized.")
    print(f"Message: {response.json().get('message')}")
else:
    print(f"\n--- ERROR ---")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
