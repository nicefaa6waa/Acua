from fastapi import APIRouter, HTTPException
from app.models import IrrigationRecommendation
from app.services import weather_service
from datetime import date

router = APIRouter(prefix="/irrigation", tags=["Sulama"])

@router.get("/{field_id}/recommendation", response_model=IrrigationRecommendation)
async def get_irrigation_recommendation(
    field_id: str,
    crop_name: str,
    latitude: float,
    longitude: float,
    target_date: date | None = None
):
    try:
        if not target_date:
            target_date = date.today()

        location = {"latitude": latitude, "longitude": longitude}
        forecast = await weather_service.get_weather_forecast(location)

        precipitation_expected = False
        for day in forecast:
            if "rain" in day["description"].lower() or day["precipitation"] > 2.0:
                precipitation_expected = True
                break

        water_amount = 5.0
        recommendation = "Normal sulama"

        if precipitation_expected:
            recommendation = "Yağmur bekleniyor. Sulamaya gerek yok."
            water_amount = 0.0
        elif forecast[0]["temperature"] > 30:
            recommendation = "Sıcaklık yüksek. Su miktarını artır."
            water_amount *= 1.2

        return IrrigationRecommendation(
            field_id=field_id,
            date=target_date,
            crop_name=crop_name,
            water_amount_liters=water_amount,
            recommendation=recommendation
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sulama önerisi oluşturulurken hata oluştu: {str(e)}")