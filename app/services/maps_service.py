import aiohttp
import asyncio
import math
from uuid import uuid4
from app.config import settings
from shapely.geometry import Polygon, Point
from shapely.ops import transform
import pyproj

async def get_field_data(location: dict, radius_m: float = 75) -> dict:

    latitude = location.get('latitude')
    longitude = location.get('longitude')
    
    if not latitude or not longitude:
        return {"error": "Invalid latitude or longitude provided"}

    async with aiohttp.ClientSession() as session:
        # Reverse geocode to get address (Google Maps API)
        address = "Unknown Farm Address"
        try:
            geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={settings.GOOGLE_MAPS_API_KEY}"
            async with session.get(geocode_url) as response:
                if response.status != 200:
                    return {"error": f"Geocoding failed: Status {response.status}"}
                geocode_data = await response.json()
                if geocode_data.get("status") == "OK" and geocode_data.get("results"):
                    result = geocode_data["results"][0]
                    components = {comp["types"][0]: comp["long_name"] for comp in result.get("address_components", [])}
                    street = components.get("route", "Farm Road")
                    city = components.get("locality", components.get("administrative_area_level_1", "Unknown Region"))
                    address = f"{street}, {city}"
        except Exception as e:
            return {"error": f"Error fetching geocoding data: {str(e)}"}

        # Query OpenStreetMap for farmland polygons (Overpass API)
        area_sqm = math.pi * radius_m ** 2  # Fallback area
        try:
            overpass_url = "http://overpass-api.de/api/interpreter"
            query = f"""
            [out:json];
            way["landuse"="farmland"](around:2000,{latitude},{longitude});
            out geom;
            """
            async with session.post(overpass_url, data={"data": query}) as response:
                if response.status != 200:
                    return {"error": f"Overpass API failed: Status {response.status}"}
                osm_data = await response.json()
                elements = osm_data.get("elements", [])
                
                if elements:
                    # Find the farmland polygon closest to the input coordinates
                    input_point = Point(longitude, latitude)
                    closest_polygon = None
                    min_distance = float('inf')
                    closest_area = 0

                    # Define projection: WGS84 to Web Mercator (EPSG:3857) for accurate area
                    wgs84 = pyproj.CRS('EPSG:4326')
                    mercator = pyproj.CRS('EPSG:3857')
                    project = pyproj.Transformer.from_crs(wgs84, mercator, always_xy=True).transform

                    for element in elements:
                        if element["type"] == "way" and "geometry" in element:
                            coords = [(point["lon"], point["lat"]) for point in element["geometry"]]
                            if len(coords) >= 3 and coords[0] == coords[-1]:  # Ensure closed polygon
                                polygon = Polygon(coords)
                                if polygon.is_valid:
                                    # Calculate distance to polygon centroid
                                    centroid = polygon.centroid
                                    distance = input_point.distance(centroid)
                                    if distance < min_distance:
                                        # Transform to Web Mercator for area calculation
                                        projected_polygon = transform(project, polygon)
                                        closest_area = projected_polygon.area  # Area in square meters
                                        min_distance = distance
                                        closest_polygon = polygon

                    if closest_polygon:
                        area_sqm = closest_area
        except Exception as e:
            return {"error": f"Error fetching OSM data: {str(e)}"}

        return {
            "field_id": str(uuid4()),
            "area_sqm": round(area_sqm, 2),
            "address": address
        }