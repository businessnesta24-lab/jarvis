import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_current_city():
    try:
        response = requests.get("https://ipinfo.io", timeout=5)
        data = response.json()
        return data.get("city", "Unknown")
    except Exception:
        return "Unknown"

def get_weather(city: str) -> str:
    api_key = os.getenv("WEATHERAPI_KEY")
    if not api_key:
        return "WEATHERAPI_KEY missing"

    if not city:
        city = get_current_city()

    url = "http://api.weatherapi.com/v1/current.json"
    params = {"key": api_key, "q": city, "aqi": "no"}

    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        weather = data["current"]["condition"]["text"]
        temperature = data["current"]["temp_c"]
        humidity = data["current"]["humidity"]
        wind_speed = data["current"]["wind_kph"]

        return f"Weather in {city}: {weather}, Temp: {temperature}°C, Humidity: {humidity}%, Wind: {wind_speed} kph"
    except Exception as e:
        logger.exception(e)
        return "Weather fetch error"
