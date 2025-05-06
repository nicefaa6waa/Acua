from typing import List, Tuple
from app.models import CropRecommendation
from app.services.soil_service import get_soil_fertility
from app.services.maps_service import get_field_data
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import re

# Load .env file from the project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

async def get_area_from_maps_service(latitude: float, longitude: float) -> float:
    """Fetch the field area (in square meters) using maps_service based on latitude and longitude."""
    field_data = await get_field_data({"latitude": latitude, "longitude": longitude})
    
    if "error" in field_data:
        return 0.0
    
    return field_data.get("area_sqm", 0.0)

def clean_json_response(response_text: str) -> str:
    """Clean the API response to extract valid JSON."""
    # Remove markdown code fences (e.g., ```json\n...\n```)
    cleaned = re.sub(r'^```json\n|\n```$', '', response_text, flags=re.MULTILINE)
    # Remove any leading/trailing whitespace
    cleaned = cleaned.strip()
    return cleaned

async def get_crop_recommendations(soil_data: dict, latitude: float, longitude: float) -> Tuple[List[CropRecommendation], dict, float]:
    """Get crop recommendations, soil fertility, and area based on location using Gemini API"""
    
    area_sqm = await get_area_from_maps_service(latitude, longitude)
    
    if area_sqm == 0.0:
        return ([{"error": "Error fetching area from maps_service"}], {}, 0.0)

    formatted_soil_data = await get_soil_fertility({"latitude": latitude, "longitude": longitude})
    
    if "error" in formatted_soil_data:
        return ([{"error": formatted_soil_data["error"]}], formatted_soil_data, area_sqm)
    
    # Configure Gemini API
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
    
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        prompt = f"""
        You are an agricultural expert. Given the following soil data and field area, provide exactly 5 crop recommendations with their water requirements and suitability scores. Return the response **strictly as a JSON array** with no additional text, markdown, or code fences. Do not include any explanations or extra content outside the JSON array.

        Soil Data:
        - Soil Type: {formatted_soil_data.get('soil_type')}
        - Fertility: {formatted_soil_data.get('fertility')}
        - pH: {formatted_soil_data.get('ph')}
        - Organic Content: {formatted_soil_data.get('organic_content')}
        - Nitrogen Content: {formatted_soil_data.get('nitrogen_content')}
        - Moisture Level: {formatted_soil_data.get('moisture_level')}
        - Field Area: {area_sqm} square meters

        Return exactly 5 crop recommendations in the following JSON format:
        [
            {{
                "crop_name": "string",
                "water_requirement_liters_per_sqm": float,
                "suitability_score": float
            }},
            ...
        ]

        Each suitability_score must be between 0 and 1. Ensure the response is valid JSON with exactly 5 entries. Use Turkish crop names (e.g., 'İnci Darı' instead of 'Pearl Millet')
        """
        
        response = await model.generate_content_async(prompt)
        recommendations_data = response.text
        
        # Clean the response to extract JSON
        cleaned_data = clean_json_response(recommendations_data)
        
        try:
            recommendations_json = json.loads(cleaned_data)
        except json.JSONDecodeError as json_error:
            error_msg = f"Invalid JSON response: {json_error}. Raw response: {cleaned_data}"
            return ([{"error": f"Error processing Gemini API response: {error_msg}"}], formatted_soil_data, area_sqm)
        
        # Validate the response is a list with 5 items
        if not isinstance(recommendations_json, list) or len(recommendations_json) != 5:
            return ([{"error": "Gemini API response must bepropagating error list with exactly 5 crop recommendations"}], formatted_soil_data, area_sqm)
        
        recommendations = [
            CropRecommendation(
                crop_name=item["crop_name"],
                water_requirement_liters_per_sqm=item["water_requirement_liters_per_sqm"],
                suitability_score=item["suitability_score"]
            )
            for item in recommendations_json
        ]
        
        return (recommendations, formatted_soil_data, area_sqm)
        
    except Exception as e:
        if "404" in str(e) or "not found" in str(e).lower():
            try:
                models = genai.list_models()
                available_models = [m.name for m in models]
                error_msg = f"Model 'gemini-1.5-pro' not found. Available models: {available_models}"
            except Exception as list_error:
                error_msg = f"Model 'gemini-1.5-pro' not found, and failed to list models: {str(list_error)}"
        else:
            error_msg = str(e)
        return ([{"error": f"Error processing Gemini API response: {error_msg}"}], formatted_soil_data, area_sqm)