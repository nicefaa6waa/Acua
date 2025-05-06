from fastapi import APIRouter, HTTPException
from app.models import IrrigationRecommendation, Location
from app.services import weather_service
from datetime import date
from typing import Optional
from pydantic import BaseModel
from app.services.gemini_weather_service import get_weather_water_recommendations

router = APIRouter()

class WeatherRequest(BaseModel):
    crop_name: str
    latitude: float
    longitude: float

@router.get("/{field_id}/recommendation", response_model=IrrigationRecommendation)
async def get_irrigation_recommendation(
    field_id: str,
    crop_name: str,
    latitude: float,
    longitude: float,
    target_date: Optional[date] = None
):
    """Get daily irrigation recommendation for a field"""
    try:
        if not target_date:
            target_date = date.today()

        # Fetch weather data
        location = {"latitude": latitude, "longitude": longitude}
        weather = await weather_service.get_weather_data(location, target_date)

        # Improved irrigation logic
        water_amount = 5.0  # Base water amount in liters/m²
        recommendation = "Water normally"
        if weather["precipitation"] > 2.0:
            recommendation = "Do not water today due to high precipitation"
            water_amount = 0.0
        elif weather["temperature"] > 30:
            recommendation = "Increase watering due to high temperature"
            water_amount *= 1.2
        elif weather["temperature"] < 15:
            recommendation = "Reduce watering due to low temperature"
            water_amount *= 0.8

        print(f"Irrigation recommendation for {crop_name} on {target_date}: {recommendation}, {water_amount} L/m²")  # Debug log

        return IrrigationRecommendation(
            field_id=field_id,
            date=target_date,
            crop_name=crop_name,
            water_amount_liters=water_amount,
            recommendation=recommendation
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recommendation: {str(e)}")

@router.post("/weather_recommendations")
async def get_weather_recommendations(request: WeatherRequest):
    """Get weather and irrigation recommendations for a crop over 7 days"""
    try:
        recommendations, area_sqm = await get_weather_water_recommendations(
            crop_name=request.crop_name,
            lat=request.latitude,
            lon=request.longitude
        )
        response = {
            "weather_recommendations": recommendations,
            "area_sqm": area_sqm
        }
        print(f"Response from /weather_recommendations: {response}")  # Debug log
        if 'error' in recommendations:
            raise HTTPException(status_code=500, detail=recommendations['error'])
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))