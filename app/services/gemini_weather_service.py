from datetime import datetime, date
from typing import Dict, List, Tuple
from app.services.weather_service import get_weather_data
from app.services.maps_service import get_field_data
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_weather_water_recommendations(crop_name: str, lat: float, lon: float) -> Tuple[List[Dict], float]:
    # Fetch weather data for 7 days
    location = {'latitude': lat, 'longitude': lon}
    weather_data = await get_weather_data(location)
    logger.info(f"Weather data response: {weather_data}")

    if 'error' in weather_data:
        return [{'error': weather_data['error']}], 0.0

    # Fetch field area
    field_data = await get_field_data(location)
    logger.info(f"Field data response: {field_data}")
    if 'error' in field_data:
        return [{'error': field_data['error']}], 0.0
    area_sqm = field_data.get('area_sqm', 0.0)

    # Generate irrigation recommendations
    forecast_with_recommendations = []
    for day in weather_data:
        date_str = day['Date']
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        for hourly in day['HourlyData']:
            temperature = hourly['temperature']
            humidity = hourly['humidity']
            precipitation = hourly['precipitation']
            hour = hourly['hour']

            # Simple irrigation logic
            water_amount = 5.0  # Base water amount in liters/m²
            if precipitation > 2.0:
                water_amount = 0.0
            elif temperature > 30:
                water_amount *= 1.2
            elif temperature < 15:
                water_amount *= 0.8

            logger.info(f"Irrigation for {date_str} {hour}:00: crop={crop_name}, water={water_amount} L/m²")

            forecast_with_recommendations.append({
                'date': date_str,
                'hour': hour,
                'temperature': temperature,
                'humidity': humidity,
                'precipitation': precipitation,
                'recommended_water_liters_per_sqm': round(water_amount, 2)
            })

    return forecast_with_recommendations, area_sqm