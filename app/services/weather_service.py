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
        # Get current time
        now = datetime.now()
        target_time = now + timedelta(hours=hours)
        
        # OpenWeatherMap Forecast API (3-hour intervals, but we'll filter for next 2-3 hours)
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "lat": SEATTLE_LAT,
            "lon": SEATTLE_LON,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
            "cnt": 40,  # Get more forecasts to find the right ones
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Filter forecasts to only include those within the next 2-3 hours
        all_forecasts = data.get("list", [])
        relevant_forecasts = []
        
        for forecast in all_forecasts:
            forecast_time = datetime.fromtimestamp(forecast.get("dt", 0))
            # Only include forecasts within the next 'hours' hours
            if now <= forecast_time <= target_time:
                relevant_forecasts.append(forecast)
            # Stop if we've gone past our target time
            if forecast_time > target_time:
                break
        
        # If we don't have enough forecasts, take the first 2 that are after now
        if len(relevant_forecasts) == 0:
            for forecast in all_forecasts:
                forecast_time = datetime.fromtimestamp(forecast.get("dt", 0))
                if forecast_time > now:
                    relevant_forecasts.append(forecast)
                    if len(relevant_forecasts) >= 2:
                        break
        
        will_rain = False
        rain_probability = 0
        forecast_details = []
        
        for forecast in relevant_forecasts:
            # Check for rain
            rain = forecast.get("rain", {})
            pop = forecast.get("pop", 0)  # Probability of precipitation (0-1)
            
            if rain or pop > 0.3:  # 30% chance or actual rain
                will_rain = True
                rain_probability = max(rain_probability, int(pop * 100))
            
            # Get forecast time
            forecast_time = datetime.fromtimestamp(forecast.get("dt", 0))
            # Format time correctly (remove leading zero, show AM/PM)
            hour = forecast_time.hour
            if hour == 0:
                time_str = "12 AM"
            elif hour < 12:
                time_str = f"{hour} AM"
            elif hour == 12:
                time_str = "12 PM"
            else:
                time_str = f"{hour - 12} PM"
            
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
