from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class Location(BaseModel):
    latitude: float
    longitude: float

class CropRecommendation(BaseModel):
    crop_name: str
    water_requirement_liters_per_sqm: float
    suitability_score: float

class WeatherRecommendation(BaseModel):
    date: str
    hour: int
    temperature: float
    humidity: float
    precipitation: float
    recommended_water_liters_per_sqm: float

class FieldRequest(BaseModel):
    location: Location
    user_id: str

class FieldResponse(BaseModel):
    user_id: str
    latitude: float
    longitude: float
    area_sqm: float
    recommended_crops: List[CropRecommendation]
    weather_recommendations: List[WeatherRecommendation]