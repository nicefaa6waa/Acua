# models.py: Pydantic models for request and response validation
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import date

class Location(BaseModel):
    """Model for field location coordinates"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class FieldRequest(BaseModel):
    """Request model for field selection"""
    location: Location
    user_id: str

class CropRecommendation(BaseModel):
    """Model for crop recommendation from Gemini API"""
    crop_name: str
    water_requirement_liters_per_sqm: float
    suitability_score: float = Field(..., ge=0, le=1)

class FieldResponse(BaseModel):
    """Response model for field details and recommendations"""
    field_id: Optional[str]  # Allow None for field_id
    location: Location
    area_sqm: float
    soil_fertility: Dict
    recommended_crops: List[CropRecommendation]

class IrrigationRecommendation(BaseModel):
    """Model for daily irrigation recommendation"""
    field_id: str
    date: date
    crop_name: str
    water_amount_liters: float
    recommendation: str