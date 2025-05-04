from typing import List
from app.models import CropRecommendation

async def get_crop_recommendations(soil_data: dict, area_sqm: float) -> List[CropRecommendation]:
    """Mocked crop recommendation logic"""
    return [
        CropRecommendation(
            crop_name="Wheat",
            water_requirement_liters_per_sqm=5.0,
            suitability_score=0.9
        ),
        CropRecommendation(
            crop_name="Corn",
            water_requirement_liters_per_sqm=6.5,
            suitability_score=0.85
        )
    ]
