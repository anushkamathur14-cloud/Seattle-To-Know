from fastapi import APIRouter, Query
from datetime import date, datetime, timedelta
from typing import Optional
from app.services.weather_service import get_seattle_weather, get_weather_forecast_next_hours
from app.services.events_service import get_seattle_events, check_events_selling_out
from app.services.king_county_service import get_king_county_updates
from app.services.air_quality_service import get_seattle_air_quality
from app.services.food_service import get_seattle_food_joints, get_food_areas, get_food_cuisines, get_price_ranges
from app.services.outdoor_activities_service import get_seattle_outdoor_activities, get_activity_types


router = APIRouter()

# Cache for weather and air quality (call API only once)
_weather_cache = None
_air_quality_cache = None
_cache_timestamp = None
CACHE_DURATION = timedelta(minutes=10)  # Cache for 10 minutes

def _get_cached_weather():
    """Get weather, using cache if available and fresh."""
    global _weather_cache, _cache_timestamp
    now = datetime.now()
    
    if _weather_cache is None or _cache_timestamp is None or (now - _cache_timestamp) > CACHE_DURATION:
        _weather_cache = get_seattle_weather()
        _cache_timestamp = now
    return _weather_cache

def _get_cached_air_quality():
    """Get air quality, using cache if available and fresh."""
    global _air_quality_cache, _cache_timestamp
    now = datetime.now()
    
    if _air_quality_cache is None or _cache_timestamp is None or (now - _cache_timestamp) > CACHE_DURATION:
        _air_quality_cache = get_seattle_air_quality()
        _cache_timestamp = now
    return _air_quality_cache

@router.get("/overview")
def get_overview():
    """
    Get overview with weather, air quality, and health section.
    Weather API is called only once and cached.
    """
    weather = _get_cached_weather()
    air_quality = _get_cached_air_quality()
    weather_forecast = get_weather_forecast_next_hours(3)
    king_county_updates = get_king_county_updates()
    
    # Weather-based advice
    weather_advice = []
    if weather["temperature_c"] < 7:  # ~45°F in Celsius
        weather_advice.append("Cold today — wear a warm layer")
    if weather["wind_mph"] > 15:
        weather_advice.append("Windy conditions — bundle up")
    if "Rain" in weather["condition"]:
        weather_advice.append("Carry an umbrella")
    
    # Add forecast-based advice
    if weather_forecast.get("will_rain"):
        weather_advice.append(weather_forecast.get("forecast", ""))
    
    # Air quality-based advice (US EPA AQI scale 0-500)
    air_quality_advice = []
    if air_quality["aqi"] >= 201:  # Very Unhealthy or Hazardous
        air_quality_advice.append(f"⚠️ Poor air quality ({air_quality['aqi_label']}) - limit outdoor activities")
    elif air_quality["aqi"] >= 151:  # Unhealthy
        air_quality_advice.append(f"⚠️ Unhealthy air quality ({air_quality['aqi_label']}) - sensitive groups should avoid outdoor activities")
    elif air_quality["aqi"] >= 101:  # Unhealthy for Sensitive Groups
        air_quality_advice.append(f"Air quality is {air_quality['aqi_label'].lower()} - sensitive groups take caution")
    
    # Categorize updates
    what_to_know = {
        "traffic": king_county_updates,
        "weather": weather_advice,
        "air_quality": air_quality_advice
    }
    
    return {
        "date": date.today().isoformat(),
        "city": "Seattle",
        "weather": weather,
        "air_quality": air_quality,
        "weather_forecast": weather_forecast,
        "what_to_know_today": what_to_know,
    }

@router.get("/food")
def get_food(
    price_range: Optional[str] = Query(None, description="Filter by price range ($, $$, $$$, $$$$)")
):
    """Get food joints with Google Maps links."""
    weather = _get_cached_weather()
    air_quality = _get_cached_air_quality()
    
    # Get the filtered food joints (price range filter only)
    food_joints = get_seattle_food_joints(area=None, cuisine=None, price_range=price_range)
    
    price_ranges = get_price_ranges()
    
    # Get Google Maps API key for frontend (same key used for Places API)
    import os
    google_maps_key = os.getenv("GOOGLE_PLACES_API_KEY", "")
    
    return {
        "weather": weather,
        "air_quality": air_quality,
        "food_joints": food_joints,
        "price_ranges": price_ranges,
        "google_maps_api_key": google_maps_key,
    }

@router.get("/events")
def get_events(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    time_range: str = Query("today", description="Time range: 'today', 'tomorrow', or 'week'"),
    locations: Optional[str] = Query(None, description="Comma-separated list of locations to filter by"),
    event_limit: int = Query(20, ge=1, le=50)
):
    """Get events for today, tomorrow, or this week."""
    weather = _get_cached_weather()
    air_quality = _get_cached_air_quality()
    
    # Set date range based on time_range parameter
    today = date.today()
    if time_range == "week":
        start_date = today
        end_date = today + timedelta(days=7)
    elif time_range == "tomorrow":
        start_date = today + timedelta(days=1)
        end_date = today + timedelta(days=1)
    else:  # today (default)
        start_date = today
        end_date = today
    
    # Parse locations if provided
    location_list = None
    if locations:
        location_list = [loc.strip() for loc in locations.split(",") if loc.strip()]
    
    # First, get all events WITHOUT location filtering to get the full list of available locations
    all_events_for_locations = get_seattle_events(
        event_type=event_type,
        start_date=start_date,
        end_date=end_date,
        locations=None,  # Don't filter by location yet
        limit=event_limit * 3  # Get more events to have a better location list
    )
    
    # Get unique locations from ALL events (before location filtering) for filter options
    unique_locations = sorted(list(set([event.get("area", "Seattle") for event in all_events_for_locations if event.get("area")])))
    
    # Now get the filtered events with location filtering applied
    events = get_seattle_events(
        event_type=event_type,
        start_date=start_date,
        end_date=end_date,
        locations=location_list,
        limit=event_limit
    )
    
    return {
        "weather": weather,
        "air_quality": air_quality,
        "events": events,
        "locations": unique_locations,
        "time_range": time_range,
    }

@router.get("/outdoor")
def get_outdoor_activities(activity_type: Optional[str] = Query(None, description="Filter by activity type")):
    """Get outdoor activities with rules and tutorial links."""
    weather = _get_cached_weather()
    air_quality = _get_cached_air_quality()
    activities = get_seattle_outdoor_activities()
    activity_types = get_activity_types()
    
    # Filter by activity type if specified
    if activity_type:
        activities = [a for a in activities if activity_type.lower() in a["type"].lower()]
    
    return {
        "weather": weather,
        "air_quality": air_quality,
        "activities": activities,
        "activity_types": activity_types,
    }
