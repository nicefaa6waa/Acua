import asyncio
from typing import List
from app.models import CropRecommendation
from app.services.gemini_service import get_crop_recommendations

async def main():
    """Test the Gemini crop recommendation service with latitude and longitude."""
    # Sample location
    latitude = 50.1
    longitude = 42.1

    try:
        # Call get_crop_recommendations with empty soil_data and location
        recommendations = await get_crop_recommendations(
            soil_data={}, latitude=latitude, longitude=longitude
        )

        # Check if an error was returned
        if isinstance(recommendations, list) and "error" in recommendations[0]:
            print(f"Error: {recommendations[0]['error']}")
            return

        # Print the recommendations
        print("\nCrop Recommendations:")
        for recommendation in recommendations:
            print(f"- Crop Name: {recommendation.crop_name}, "
                  f"Water Requirement: {recommendation.water_requirement_liters_per_sqm} L/sqm, "
                  f"Suitability Score: {recommendation.suitability_score}")

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())