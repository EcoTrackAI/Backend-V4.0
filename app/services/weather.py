import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY = os.getenv("WEATHER_CITY", "Kolkata")


def get_outdoor_weather(city: str = None) -> dict:
    """
    Fetches real-time outdoor weather from OpenWeather API.
    """

    try:
        if not API_KEY:
            return {"error": "Missing OPENWEATHER_API_KEY in .env"}

        target_city = city if city else CITY

        url = (
            "https://api.openweathermap.org/data/2.5/weather"
            f"?q={target_city}&appid={API_KEY}&units=metric"
        )

        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            return {"error": "OpenWeather API error", "details": response.json()}

        data = response.json()

        return {
            "outdoor_temp": data["main"]["temp"],
            "outdoor_humidity": data["main"]["humidity"],
            "weather_condition": data["weather"][0]["description"],
            "city": target_city,
        }

    except requests.exceptions.Timeout:
        return {"error": "Weather API timeout"}

    except requests.exceptions.ConnectionError:
        return {"error": "Weather API connection failed"}

    except Exception as e:
        return {"error": f"Unexpected weather error: {str(e)}"}
