import requests
import os

class WeatherService:
    def __init__(self, api_key=None):
        self.api_key = (api_key or os.getenv("OPENWEATHER_API_KEY", "")).strip()
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city):
        if not self.api_key or self.api_key == "YOUR_OPENWEATHER_API_KEY":
            return "Weather API key is not configured. Please add your OpenWeather API key to the .env file."
        
        try:
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"
            }
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if response.status_code == 200:
                temp = data["main"]["temp"]
                desc = data["weather"][0]["description"]
                humidity = data["main"]["humidity"]
                wind_speed = data["wind"]["speed"]
                return f"The weather in {city} is currently {desc} with a temperature of {temp}°C. Humidity is {humidity}% and wind speed is {wind_speed} m/s."
            elif response.status_code == 401:
                return f"⚠️ **Weather API Error**: Your OpenWeather API key is invalid or not yet active. If you just created it, it can take up to 2 hours to activate. Please verify your key in the .env file."
            else:
                return f"Could not get weather for {city}. Error: {data.get('message', 'Unknown error')}"
        except Exception as e:
            return f"Error fetching weather: {str(e)}"
