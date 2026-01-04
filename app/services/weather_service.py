import os
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Seattle coordinates
SEATTLE_LAT = 47.6062
SEATTLE_LON = -122.3321

def get_seattle_weather() -> Dict:
    """Get current weather for Seattle in Celsius."""
    if not OPENWEATHER_API_KEY:
        raise RuntimeError("OPENWEATHER_API_KEY is not set")

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": SEATTLE_LAT,
        "lon": SEATTLE_LON,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",  # Celsius
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    return {
        "temperature_c": round(data["main"]["temp"]),
        "feels_like_c": round(data["main"]["feels_like"]),
        "condition": data["weather"][0]["description"].title(),
        "wind_mph": round(data["wind"]["speed"] * 2.237),  # Convert m/s to mph
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
    }


def get_weather_forecast_next_hours(hours: int = 3) -> Dict:
    """
    Get weather forecast for the next 2-3 hours.
    Returns prediction for rain/weather changes.
    """
    if not OPENWEATHER_API_KEY:
        return {
            "will_rain": False,
            "rain_probability": 0,
            "forecast": "Weather forecast unavailable",
            "next_hours": []
        }
    
    try:
        # OpenWeatherMap Forecast API (3-hour intervals)
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "lat": SEATTLE_LAT,
            "lon": SEATTLE_LON,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
            "cnt": 2,  # Get next 2 forecasts (6 hours)
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Get next 2-3 hours of forecasts
        forecasts = data.get("list", [])[:2]  # Next 2 forecast periods (6 hours)
        
        will_rain = False
        rain_probability = 0
        forecast_details = []
        
        for forecast in forecasts:
            # Check for rain
            rain = forecast.get("rain", {})
            pop = forecast.get("pop", 0)  # Probability of precipitation (0-1)
            
            if rain or pop > 0.3:  # 30% chance or actual rain
                will_rain = True
                rain_probability = max(rain_probability, int(pop * 100))
            
            # Get forecast time
            dt = datetime.fromtimestamp(forecast.get("dt", 0))
            time_str = dt.strftime("%I %p")
            
            # Get weather condition
            weather = forecast.get("weather", [{}])[0]
            condition = weather.get("description", "").title()
            temp = round(forecast.get("main", {}).get("temp", 0))
            
            forecast_details.append({
                "time": time_str,
                "condition": condition,
                "temperature_c": temp,
                "rain_probability": int(pop * 100) if pop else 0,
                "will_rain": bool(rain) or pop > 0.3
            })
        
        # Generate forecast message
        if will_rain:
            forecast_msg = f"🌧️ Rain expected in the next {hours} hours ({rain_probability}% chance)"
        else:
            forecast_msg = f"☀️ No rain expected in the next {hours} hours"
        
        return {
            "will_rain": will_rain,
            "rain_probability": rain_probability,
            "forecast": forecast_msg,
            "next_hours": forecast_details
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather forecast: {e}")
        return {
            "will_rain": False,
            "rain_probability": 0,
            "forecast": "Weather forecast unavailable",
            "next_hours": []
        }
    except Exception as e:
        print(f"Unexpected error in get_weather_forecast_next_hours: {e}")
        return {
            "will_rain": False,
            "rain_probability": 0,
            "forecast": "Weather forecast unavailable",
            "next_hours": []
        }
