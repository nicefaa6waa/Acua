import aiohttp
import asyncio

async def get_soil_fertility(location: dict) -> dict:
    """Retrieve soil fertility data from SoilGrids API based on latitude and longitude"""
    latitude = location.get('latitude')
    longitude = location.get('longitude')
    
    if not latitude or not longitude:
        return {"error": "Invalid latitude or longitude provided"}

    result = {"soil_type": "Unknown"}
    
    async with aiohttp.ClientSession() as session:
        # Fetch WRB classification
        class_url = f"https://rest.isric.org/soilgrids/v2.0/classification/query?lon={longitude}&lat={latitude}&number_classes=5"
        try:
            async with session.get(class_url) as response:
                if response.status != 200:
                    response_text = await response.text()
                    return {"error": f"Classification query failed: Status {response.status}, Response: {response_text}"}
                class_data = await response.json()
                result["soil_type"] = class_data.get("wrb_class_name", "Unknown")
        except Exception as e:
            return {"error": f"Error fetching classification data: {str(e)}"}

        # Fetch soil properties
        props_url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lon={longitude}&lat={latitude}&property=phh2o&property=nitrogen&property=soc&property=cec&property=wv0033&depth=0-5cm&value=mean"
        try:
            async with session.get(props_url) as response:
                if response.status != 200:
                    response_text = await response.text()
                    return {"error": f"Properties query failed: Status {response.status}, Response: {response_text}"}
                props_data = await response.json()
        except Exception as e:
            return {"error": f"Error fetching properties data: {str(e)}"}

        # Extract properties from properties data
        layers = props_data.get("properties", {}).get("layers", [])
        soil_properties = {}
        for layer in layers:
            layer_name = layer.get("name")
            for depth in layer.get("depths", []):
                if depth.get("label") == "0-5cm":
                    values = depth.get("values", {})
                    mean_value = values.get("mean")
                    if mean_value is not None:
                        # Convert units based on layer's d_factor
                        d_factor = layer.get("unit_measure", {}).get("d_factor", 1)
                        soil_properties[layer_name] = mean_value / d_factor

        # Categorize soil properties
        ph = soil_properties.get("phh2o", 7.0)  # Default to neutral pH if missing
        nitrogen = soil_properties.get("nitrogen", 0)  # g/kg
        organic_carbon = soil_properties.get("soc", 0)  # g/kg
        cec = soil_properties.get("cec", 0)  # cmol(c)/kg
        moisture = soil_properties.get("wv0033", 0)  # 10^-2 cm³/cm³

        # Nitrogen content categorization
        if nitrogen > 2:
            nitrogen_content = "High"
        elif nitrogen >= 1:
            nitrogen_content = "Moderate"
        else:
            nitrogen_content = "Low"

        # Organic content (approximated as percentage)
        organic_content = f"{min(organic_carbon / 1.724, 100):.0f}%"  # Convert SOC to organic matter (SOC * 1.724 ≈ OM)

        # Fertility based on CEC
        if cec > 20:
            fertility = "High"
        elif cec >= 10:
            fertility = "Moderate"
        else:
            fertility = "Low"

        # Moisture level based on water retention at 33 kPa
        if moisture > 30:
            moisture_level = "High"
        elif moisture >= 15:
            moisture_level = "Moderate"
        else:
            moisture_level = "Low"

        # Update result with soil properties
        result.update({
            "fertility": fertility,
            "ph": round(ph, 1),
            "organic_content": organic_content,
            "nitrogen_content": nitrogen_content,
            "moisture_level": moisture_level
        })
        return result