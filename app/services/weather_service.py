import httpx
from datetime import datetime, timedelta

async def get_weather_data(location: dict, target_date: datetime = None) -> dict:
    if target_date is None:
        target_date = datetime.now()

    lat = location.get('latitude')
    lon = location.get('longitude')

    start_date = target_date.strftime('%Y-%m-%d')
    end_date = (target_date + timedelta(days=6)).strftime('%Y-%m-%d')

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation,relativehumidity_2m&timezone=auto&start_date={start_date}&end_date={end_date}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as e:
            return {'error': f"Failed to fetch weather data. Status: {e.response.status_code}, Message: {e.response.text}"}
        except httpx.RequestError as e:
            return {'error': f"Failed to connect to the weather service: {e}"}

    forecast_data = []
    if 'hourly' in data and 'time' in data['hourly']:
        hourly_data = data['hourly']
        for i in range(len(hourly_data['time'])):
            timestamp_str = hourly_data['time'][i]
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00')) # Handle UTC 'Z'

            # Approximate morning (09:00), afternoon (15:00), evening (21:00) UTC
            if timestamp.hour in [6, 12, 18]: # Adjust hours for your local time if needed
                date_str = timestamp.strftime('%Y-%m-%d')
                forecast_data.append({
                    'date': date_str,
                    'hour': timestamp.hour,
                    'temperature': hourly_data.get('temperature_2m', [])[i] if 'temperature_2m' in hourly_data and i < len(hourly_data['temperature_2m']) else None,
                    'precipitation': hourly_data.get('precipitation', [])[i] if 'precipitation' in hourly_data and i < len(hourly_data['precipitation']) else None,
                    'humidity': hourly_data.get('relativehumidity_2m', [])[i] if 'relativehumidity_2m' in hourly_data and i < len(hourly_data['relativehumidity_2m']) else None,
                })
    else:
        return {'error': 'Unexpected data format received from the weather service.'}

    # Group data by date
    daily_forecast = {}
    for item in forecast_data:
        if item['date'] not in daily_forecast:
            daily_forecast[item['date']] = []
        daily_forecast[item['date']].append({
            'hour': item['hour'],
            'temperature': item['temperature'],
            'precipitation': item['precipitation'],
            'humidity': item['humidity']
        })

    readable_forecast = []
    for date, hourly_data in daily_forecast.items():
        readable_forecast.append({
            'Date': date,
            'HourlyData': sorted(hourly_data, key=lambda x: x['hour']) # Sort by hour
        })

    return readable_forecast