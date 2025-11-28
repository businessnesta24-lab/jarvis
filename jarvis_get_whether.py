# jarvis_get_whether.py
import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def get_current_city():
    try:
        response = requests.get("https://ipinfo.io", timeout=5)
        data = response.json()
        return data.get("city", "Unknown")
    except Exception:
        return "Unknown"

def get_weather(city: str = "") -> str:
    api_key = os.getenv("WEATHERAPI_KEY")
    if not api_key:
        logger.error("WEATHERAPI_KEY missing है।")
        return "Environment variables में WEATHERAPI_KEY नहीं मिली।"

    if not city:
        city = get_current_city()

    url = "http://api.weatherapi.com/v1/current.json"
    params = {"key": api_key, "q": city, "aqi": "no"}

    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code != 200:
            logger.error(f"WeatherAPI error: {response.status_code} - {response.text}")
            return f"Error: {city} के लिए weather fetch नहीं कर पाए।"

        data = response.json()
        weather = data["current"]["condition"]["text"]
        temp = data["current"]["temp_c"]
        humidity = data["current"]["humidity"]
        wind = data["current"]["wind_kph"]

        return (f"Weather in {city}:\n"
                f"- Condition: {weather}\n"
                f"- Temperature: {temp}°C\n"
                f"- Humidity: {humidity}%\n"
                f"- Wind Speed: {wind} kph")

    except Exception as e:
        logger.exception(f"Weather fetch error: {e}")
        return "Weather fetch करते समय error आया"
