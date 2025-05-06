from fastapi import APIRouter, HTTPException
from app.models import FieldRequest, FieldResponse, Location
from app.services import gemini_service

router = APIRouter()

@router.post("/", response_model=FieldResponse)
async def create_field(field_request: FieldRequest):
    """Create a new field and get crop recommendations"""
    try:
        # Get crop recommendations, soil fertility, and area from gemini_service
        recommended_crops, soil_fertility, area_sqm = await gemini_service.get_crop_recommendations(
            soil_data={},
            latitude=field_request.location.latitude,
            longitude=field_request.location.longitude
        )

        # Check if an error was returned
        if isinstance(recommended_crops, list) and "error" in recommended_crops[0]:
            raise HTTPException(status_code=500, detail=recommended_crops[0]["error"])

        return FieldResponse(
            field_id=None,  # Set to None as specified
            location=field_request.location,
            area_sqm=area_sqm,
            soil_fertility=soil_fertility,
            recommended_crops=recommended_crops
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing field: {str(e)}")