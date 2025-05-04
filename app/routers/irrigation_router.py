# irrigation_router.py: Endpoints for daily irrigation recommendations
from fastapi import APIRouter, HTTPException
from app.models import IrrigationRecommendation, Location  # Absolute import
from app.services import weather_service  # Absolute import
from datetime import date
from typing import Optional

router = APIRouter()

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

        # Mocked logic for irrigation
        water_amount = 5.0
        recommendation = "Water normally"
        if weather["precipitation"] > 2.0:
            recommendation = "Do not water today"
            water_amount = 0.0
        elif weather["temperature"] > 30:
            recommendation = "Increase watering due to high temperature"
            water_amount *= 1.2

        return IrrigationRecommendation(
            field_id=field_id,
            date=target_date,
            crop_name=crop_name,
            water_amount_liters=water_amount,
            recommendation=recommendation
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recommendation: {str(e)}")