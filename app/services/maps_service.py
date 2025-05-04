import httpx
from typing import Dict

async def get_coordinates_from_address(address: str) -> Dict[str, float]:
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "SmartAgricultureApp/1.0"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers)
        if response.status_code != 200:
            raise Exception("OpenStreetMap API'ye bağlanılamadı.")

        data = response.json()
        if not data:
            raise Exception("Adres bulunamadı.")

        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])

        return {"latitude": lat, "longitude": lon}