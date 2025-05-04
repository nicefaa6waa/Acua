import httpx
from datetime import datetime
from typing import List
from app.config import settings 

async def get_weather_forecast(location: dict) -> List[dict]:
    """
    OpenWeatherMap API'den 5 günlük hava durumu tahmini alır
    """
    API_KEY = settings.OPENWEATHER_API_KEY  
    lat = location["latitude"]
    lon = location["longitude"]

    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise Exception(f"Hava durumu verisi alınamadı: {response.text}")

        data = response.json()

        forecast_list = []
        for item in data["list"][:10]:  # İlk 5 gün için yaklaşık veri
            forecast_date = datetime.fromtimestamp(item["dt"]).isoformat()
            rain = item.get("rain", {}).get("3h", 0)

            forecast_list.append({
                "date": forecast_date,
                "temperature": item["main"]["temp"],
                "feels_like": item["main"]["feels_like"],
                "humidity": item["main"]["humidity"],
                "wind_speed": item["wind"]["speed"],
                "description": item["weather"][0]["description"],
                "precipitation": rain
            })

        return forecast_list