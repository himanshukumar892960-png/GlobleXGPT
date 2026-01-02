import requests
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("OPENWEATHER_API_KEY")
city = "London"
url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}&units=metric"

print(f"Testing key: {key}")
response = requests.get(url)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 401:
    print("\n--- ERROR ANALYSIS ---")
    print("OpenWeather returned 401 Unauthorized.")
    print("Common reasons:")
    print("1. Key is not yet active (takes up to 60 mins for new keys).")
    print("2. You are using a 'One Call API 3.0' key with the 2.5 endpoint (or vice versa).")
    print("3. Typo in the key.")
