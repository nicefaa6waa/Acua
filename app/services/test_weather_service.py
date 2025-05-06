# app/services/test_weather_service.py
import asyncio
from datetime import date

from app.services.weather_service import get_weather_data

async def main():
    location = {
        "latitude": 39.9208,   # Example: Ankara, Turkey
        "longitude": 32.8541
    }

    print("Fetching 7-day weather forecast for Ankara (morning, afternoon, evening):")
    result = await get_weather_data(location)
    if isinstance(result, list):
        for day_data in result:
            print(f"Date: {day_data['Date']}")
            for hourly_item in day_data['HourlyData']:
                print(f"  Hour: {hourly_item['hour']:02d}:00")
                print(f"    Temperature: {hourly_item['temperature']} °C")
                print(f"    Precipitation: {hourly_item['precipitation']} mm")
                print(f"    Humidity: {hourly_item['humidity']} %")
            print("-" * 20)
    elif isinstance(result, dict) and 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print("Unexpected result format.")

if __name__ == "__main__":
    asyncio.run(main())