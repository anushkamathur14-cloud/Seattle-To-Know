import os
import requests
from typing import Dict, List

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Seattle coordinates
SEATTLE_LAT = 47.6062
SEATTLE_LON = -122.3321

# US EPA AQI (Air Quality Index) categories (0-500 scale)
EPA_AQI_CATEGORIES = {
    (0, 50): {"label": "Good", "color": "green", "health_concern": "Air quality is satisfactory"},
    (51, 100): {"label": "Moderate", "color": "yellow", "health_concern": "Acceptable for most people"},
    (101, 150): {"label": "Unhealthy for Sensitive Groups", "color": "orange", "health_concern": "Sensitive groups may experience effects"},
    (151, 200): {"label": "Unhealthy", "color": "red", "health_concern": "Everyone may begin to experience effects"},
    (201, 300): {"label": "Very Unhealthy", "color": "purple", "health_concern": "Health alert: everyone may experience serious effects"},
    (301, 500): {"label": "Hazardous", "color": "maroon", "health_concern": "Health warning of emergency conditions"}
}

# EPA AQI breakpoints for each pollutant
# Format: (low_conc, high_conc, low_aqi, high_aqi)
EPA_AQI_BREAKPOINTS = {
    "pm2_5": [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 500.4, 301, 500),
    ],
    "pm10": [
        (0, 54, 0, 50),
        (55, 154, 51, 100),
        (155, 254, 101, 150),
        (255, 354, 151, 200),
        (355, 424, 201, 300),
        (425, 604, 301, 500),
    ],
    "o3": [  # 8-hour average (ppb)
        (0, 54, 0, 50),
        (55, 70, 51, 100),
        (71, 85, 101, 150),
        (86, 105, 151, 200),
        (106, 200, 201, 300),
        (201, 500, 301, 500),
    ],
    "no2": [  # 1-hour average (ppb)
        (0, 53, 0, 50),
        (54, 100, 51, 100),
        (101, 360, 101, 150),
        (361, 649, 151, 200),
        (650, 1249, 201, 300),
        (1250, 2049, 301, 500),
    ],
    "co": [  # 8-hour average (ppm (convert from μg/m³: 1 ppm = 1.15 mg/m³ = 1150 μg/m³)
        (0, 4.4, 0, 50),
        (4.5, 9.4, 51, 100),
        (9.5, 12.4, 101, 150),
        (12.5, 15.4, 151, 200),
        (15.5, 30.4, 201, 300),
        (30.5, 50.4, 301, 500),
    ],
}


def _calculate_epa_aqi(concentration: float, breakpoints: List) -> int:
    """
    Calculate EPA AQI for a given pollutant concentration.
    
    Formula: AQI = ((I_high - I_low) / (C_high - C_low)) * (C - C_low) + I_low
    where:
    - I_high, I_low = AQI values corresponding to C_high, C_low
    - C = pollutant concentration
    - C_high, C_low = concentration breakpoints
    """
    for low_conc, high_conc, low_aqi, high_aqi in breakpoints:
        if low_conc <= concentration <= high_conc:
            if high_conc == low_conc:
                return low_aqi
            aqi = ((high_aqi - low_aqi) / (high_conc - low_conc)) * (concentration - low_conc) + low_aqi
            return round(aqi)
    
    # If concentration exceeds highest breakpoint, return max AQI
    return 500


def _get_epa_aqi_category(aqi: int) -> Dict:
    """Get EPA AQI category information for a given AQI value."""
    for (low, high), category in EPA_AQI_CATEGORIES.items():
        if low <= aqi <= high:
            return category
    # Default to hazardous if out of range
    return EPA_AQI_CATEGORIES[(301, 500)]

def get_seattle_air_quality() -> Dict:
    """
    Fetch current air quality data for Seattle.
    Uses OpenWeatherMap Air Pollution API.
    
    Returns:
        Dictionary with AQI, main pollutants, and health recommendations
    """
    if not OPENWEATHER_API_KEY:
        return _get_default_air_quality()
    
    try:
        # OpenWeatherMap Air Pollution API
        url = "http://api.openweathermap.org/data/2.5/air_pollution"
        params = {
            "lat": SEATTLE_LAT,
            "lon": SEATTLE_LON,
            "appid": OPENWEATHER_API_KEY,
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract pollutant concentrations
        components = data["list"][0]["components"]
        dt = data["list"][0]["dt"]
        
        # Get pollutant values
        pm25 = components.get("pm2_5", 0)  # μg/m³
        pm10 = components.get("pm10", 0)    # μg/m³
        no2 = components.get("no2", 0)      # μg/m³ (but need ppb for EPA)
        o3 = components.get("o3", 0)         # μg/m³ (but need ppb for EPA)
        co = components.get("co", 0)         # μg/m³ (but need ppm for EPA)
        
        # Convert units for EPA AQI calculation
        # NO2: 1 ppb = 1.88 μg/m³ at 25°C
        no2_ppb = no2 / 1.88 if no2 > 0 else 0
        # O3: 1 ppb = 1.96 μg/m³ at 25°C
        o3_ppb = o3 / 1.96 if o3 > 0 else 0
        # CO: 1 ppm = 1150 μg/m³
        co_ppm = co / 1150 if co > 0 else 0
        
        # Calculate EPA AQI for each pollutant
        aqi_pm25 = _calculate_epa_aqi(pm25, EPA_AQI_BREAKPOINTS["pm2_5"])
        aqi_pm10 = _calculate_epa_aqi(pm10, EPA_AQI_BREAKPOINTS["pm10"])
        aqi_o3 = _calculate_epa_aqi(o3_ppb, EPA_AQI_BREAKPOINTS["o3"])
        aqi_no2 = _calculate_epa_aqi(no2_ppb, EPA_AQI_BREAKPOINTS["no2"])
        aqi_co = _calculate_epa_aqi(co_ppm, EPA_AQI_BREAKPOINTS["co"])
        
        # Overall AQI is the maximum of all individual AQIs
        epa_aqi = max(aqi_pm25, aqi_pm10, aqi_o3, aqi_no2, aqi_co)
        
        # Determine which pollutant is driving the AQI
        dominant_pollutant = None
        if epa_aqi == aqi_pm25:
            dominant_pollutant = "PM2.5"
        elif epa_aqi == aqi_pm10:
            dominant_pollutant = "PM10"
        elif epa_aqi == aqi_o3:
            dominant_pollutant = "O₃"
        elif epa_aqi == aqi_no2:
            dominant_pollutant = "NO₂"
        elif epa_aqi == aqi_co:
            dominant_pollutant = "CO"
        
        # Get category info
        category = _get_epa_aqi_category(epa_aqi)
        
        # Generate health recommendations
        health_recommendations = _get_health_recommendations(epa_aqi, components)
        
        return {
            "aqi": epa_aqi,  # US EPA AQI (0-500)
            "aqi_label": category["label"],
            "aqi_color": category["color"],
            "health_concern": category["health_concern"],
            "dominant_pollutant": dominant_pollutant,
            "pollutants": {
                "pm2_5": round(pm25, 1),  # μg/m³
                "pm10": round(pm10, 1),    # μg/m³
                "no2": round(no2, 1),      # μg/m³
                "o3": round(o3, 1),        # μg/m³
                "co": round(co, 1),        # μg/m³
            },
            "health_recommendations": health_recommendations,
            "timestamp": dt,
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching air quality from OpenWeatherMap: {e}")
        return _get_default_air_quality()
    except Exception as e:
        print(f"Unexpected error in get_seattle_air_quality: {e}")
        return _get_default_air_quality()


def _get_health_recommendations(aqi: int, components: Dict) -> List[str]:
    """
    Generate health recommendations based on US EPA AQI (0-500) and pollutant levels.
    """
    recommendations = []
    
    # General AQI-based recommendations (US EPA scale)
    if aqi >= 301:  # Hazardous
        recommendations.append("Health warning of emergency conditions - avoid all outdoor activities")
        recommendations.append("Stay indoors and keep windows and doors closed")
        recommendations.append("Use air purifiers if available")
        recommendations.append("Everyone should avoid physical exertion")
    elif aqi >= 201:  # Very Unhealthy
        recommendations.append("Health alert - everyone may experience serious effects")
        recommendations.append("Avoid outdoor activities, especially exercise")
        recommendations.append("Keep windows and doors closed")
        recommendations.append("Sensitive groups should stay indoors")
    elif aqi >= 151:  # Unhealthy
        recommendations.append("Everyone may begin to experience effects")
        recommendations.append("Sensitive groups should avoid outdoor activities")
        recommendations.append("Consider limiting time outdoors")
    elif aqi >= 101:  # Unhealthy for Sensitive Groups
        recommendations.append("Sensitive groups should reduce outdoor activities")
        recommendations.append("Consider limiting time outdoors if you have respiratory issues")
    elif aqi >= 51:  # Moderate
        recommendations.append("Air quality is acceptable for most people")
        recommendations.append("Unusually sensitive people may experience minor symptoms")
    else:  # Good (0-50)
        recommendations.append("Air quality is good - safe for outdoor activities")
    
    # Specific pollutant-based recommendations
    pm25 = components.get("pm2_5", 0)
    pm10 = components.get("pm10", 0)
    o3 = components.get("o3", 0)
    
    # PM2.5 thresholds (μg/m³)
    if pm25 > 55.4:  # Unhealthy PM2.5
        recommendations.append("High PM2.5 levels - wear N95 mask if going outside")
    elif pm25 > 35.4:  # Unhealthy for sensitive groups
        recommendations.append("Elevated PM2.5 levels - sensitive groups take caution")
    
    # PM10 thresholds (μg/m³)
    if pm10 > 254:  # Unhealthy PM10
        recommendations.append("Elevated PM10 levels detected")
    
    # Ozone thresholds (μg/m³, converted)
    o3_ppb = o3 / 1.96 if o3 > 0 else 0
    if o3_ppb > 85:  # Unhealthy ozone
        recommendations.append("High ozone levels - avoid outdoor exercise during afternoon")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_recommendations = []
    for rec in recommendations:
        if rec not in seen:
            seen.add(rec)
            unique_recommendations.append(rec)
    
    return unique_recommendations if unique_recommendations else ["Monitor air quality if you have respiratory conditions"]


def _get_default_air_quality() -> Dict:
    """
    Return default air quality data when API is unavailable.
    """
    return {
        "aqi": 50,  # US EPA AQI scale
        "aqi_label": "Good",
        "aqi_color": "green",
        "health_concern": "Air quality is satisfactory",
        "dominant_pollutant": None,
        "pollutants": {
            "pm2_5": 0,
            "pm10": 0,
            "no2": 0,
            "o3": 0,
            "co": 0,
        },
        "health_recommendations": [
            "Air quality data temporarily unavailable",
            "Check local air quality resources if you have respiratory conditions"
        ],
        "timestamp": None,
    }
