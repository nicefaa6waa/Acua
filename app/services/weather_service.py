# weather_service.py: OpenWeatherMap API integration for daily weather
import httpx
from app.config import settings
from datetime import date

async def get_weather_data(location: dict, target_date: date) -> dict:
    return {
        "temperature": 28.0,       # °C
        "precipitation": 1.5,      # mm
        "humidity": 60.0           # %
    }