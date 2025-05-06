import asyncio
from app.services.maps_service import get_field_data

async def main():
    location = {"latitude": 40, "longitude": 39}
    result = await get_field_data(location, radius_m=100)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())