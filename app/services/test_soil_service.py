import asyncio
from app.services.soil_service import get_soil_fertility

async def main():
    location = {"latitude": 20, "longitude": 50}
    result = await get_soil_fertility(location)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())