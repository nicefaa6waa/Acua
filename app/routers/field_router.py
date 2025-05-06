from fastapi import APIRouter, HTTPException
from app.models import FieldRequest, FieldResponse, CropRecommendation
from app.services.gemini_weather_service import get_weather_water_recommendations
import logging

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/", response_model=FieldResponse)
async def create_field(request: FieldRequest):
    """Create a field and return crop and irrigation recommendations"""
    try:
        latitude = request.location.latitude
        longitude = request.location.longitude
        user_id = request.user_id

        # Mocked crop recommendations (replace with actual logic or AI service)
        recommended_crops = [
            CropRecommendation(crop_name="Buğday", water_requirement_liters_per_sqm=1.5, suitability_score=0.95),
            CropRecommendation(crop_name="Mısır", water_requirement_liters_per_sqm=2.0, suitability_score=0.90),
            CropRecommendation(crop_name="Ayçiçeği", water_requirement_liters_per_sqm=1.2, suitability_score=0.85),
            CropRecommendation(crop_name="Pamuk", water_requirement_liters_per_sqm=1.8, suitability_score=0.80),
            CropRecommendation(crop_name="Şeker Pancarı", water_requirement_liters_per_sqm=1.7, suitability_score=0.75),
        ]

        # Fetch weather and irrigation recommendations
        weather_recommendations, area_sqm = await get_weather_water_recommendations(
            crop_name=recommended_crops[0].crop_name,  # Use the first crop for weather data
            lat=latitude,
            lon=longitude
        )

        if 'error' in weather_recommendations:
            raise HTTPException(status_code=500, detail=weather_recommendations['error'])

        logger.info(f"Field created for user {user_id} at ({latitude}, {longitude}): {len(recommended_crops)} crops, {len(weather_recommendations)} weather entries")

        return FieldResponse(
            user_id=user_id,
            latitude=latitude,
            longitude=longitude,
            area_sqm=area_sqm,
            recommended_crops=recommended_crops,
            weather_recommendations=weather_recommendations
        )
    except Exception as e:
        logger.error(f"Error creating field: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))