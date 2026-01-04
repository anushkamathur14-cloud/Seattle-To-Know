import os
import requests
from typing import List, Dict, Optional

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

# Map cuisine types to Google Places API types
CUISINE_TO_PLACE_TYPE = {
    "American": "restaurant",
    "Chinese": "chinese_restaurant",
    "Italian": "italian_restaurant",
    "Japanese": "japanese_restaurant",
    "Korean": "korean_restaurant",
    "Mediterranean": "mediterranean_restaurant",
    "Mexican": "mexican_restaurant",
    "Seafood": "seafood_restaurant",
    "Thai": "thai_restaurant",
    "Vietnamese": "vietnamese_restaurant",
    "Indian": "indian_restaurant",
    "French": "french_restaurant",
    "Middle Eastern": "meal_takeaway",  # Fallback, will filter by keyword
    "Fine Dining": "restaurant",
    "Hawaiian": "restaurant",
    "Fusion": "restaurant"
}

# Map price range ($, $$, $$$, $$$$) to Google price level (0-4)
PRICE_RANGE_TO_LEVEL = {
    "$": 1,
    "$$": 2,
    "$$$": 3,
    "$$$$": 4
}

# Seattle area coordinates
SEATTLE_AREAS = {
    "Capitol Hill": {"lat": 47.6231, "lng": -122.3196},
    "Downtown": {"lat": 47.6062, "lng": -122.3321},
    "Fremont": {"lat": 47.6510, "lng": -122.3509},
    "Queen Anne": {"lat": 47.6289, "lng": -122.3568},
    "Ballard": {"lat": 47.6689, "lng": -122.3760},
    "Wallingford": {"lat": 47.6606, "lng": -122.3334},
    "Ravenna": {"lat": 47.6769, "lng": -122.3000},
    "West Seattle": {"lat": 47.5626, "lng": -122.3870}
}

def get_seattle_food_joints(
    area: Optional[str] = None,
    cuisine: Optional[str] = None,
    price_range: Optional[str] = None
) -> List[Dict]:
    """
    Get Seattle food joints using Google Places API.
    
    Args:
        area: Optional area filter (e.g., "Capitol Hill", "Downtown", "Fremont", etc.)
        cuisine: Optional cuisine type filter
        price_range: Optional price range filter ($, $$, $$$, $$$$)
    
    Returns:
        List of food joints with name, area, cuisine type, and Google Maps link
    """
    # If no API key, return placeholder data
    if not GOOGLE_PLACES_API_KEY:
        return _get_placeholder_food_joints(area, cuisine, price_range)
    
    try:
        # Build search query
        location = "Seattle, WA"
        if area and area in SEATTLE_AREAS:
            coords = SEATTLE_AREAS[area]
            location = f"{coords['lat']},{coords['lng']}"
            query = f"restaurants in {area}, Seattle, WA"
        else:
            query = "restaurants in Seattle, WA"
        
        # Add cuisine to query if specified
        if cuisine:
            # Map cuisine to search term
            cuisine_terms = {
                "Korean Fusion": "Korean fusion",
                "Korean-American": "Korean American",
                "Hawaiian-Korean": "Hawaiian Korean",
                "French/Creole": "French Creole",
                "Middle Eastern": "Middle Eastern"
            }
            cuisine_term = cuisine_terms.get(cuisine, cuisine.lower())
            query = f"{cuisine_term} {query}"
        
        # Use Places API Text Search
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": query,
            "key": GOOGLE_PLACES_API_KEY,
            "type": "restaurant"
        }
        
        # Add price level filter if specified
        if price_range and price_range in PRICE_RANGE_TO_LEVEL:
            params["minprice"] = PRICE_RANGE_TO_LEVEL[price_range] - 1
            params["maxprice"] = PRICE_RANGE_TO_LEVEL[price_range]
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "OK":
            print(f"Google Places API error: {data.get('status')}")
            return _get_placeholder_food_joints(area, cuisine, price_range)
        
        # Transform results
        food_joints = []
        for place in data.get("results", [])[:20]:  # Limit to 20 results
            # Extract cuisine from types
            cuisine_type = _extract_cuisine_from_types(place.get("types", []))
            
            # Get price level and convert to $ format
            price_level = place.get("price_level", 2)
            price_range_str = _price_level_to_range(price_level)
            
            # Get area from address or use provided area
            address = place.get("formatted_address", "")
            area_name = area if area else _extract_area_from_address(address)
            
            # Build Google Maps link
            place_id = place.get("place_id", "")
            maps_link = f"https://www.google.com/maps/place/?q=place_id:{place_id}" if place_id else f"https://www.google.com/maps/search/?api=1&query={place.get('name', '').replace(' ', '+')}+Seattle"
            
            food_joints.append({
                "name": place.get("name", "Unknown"),
                "area": area_name,
                "cuisine": cuisine_type,
                "price_range": price_range_str,
                "address": address,
                "rating": place.get("rating", 0),
                "google_maps_link": maps_link
            })
        
        # Apply additional filters if needed (in case API didn't filter perfectly)
        if cuisine:
            cuisine_lower = cuisine.lower()
            food_joints = [j for j in food_joints if cuisine_lower in j["cuisine"].lower() or j["cuisine"].lower() in cuisine_lower]
        
        if price_range:
            food_joints = [j for j in food_joints if j["price_range"] == price_range]
        
        return food_joints if food_joints else _get_placeholder_food_joints(area, cuisine, price_range)
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching food from Google Places API: {e}")
        return _get_placeholder_food_joints(area, cuisine, price_range)
    except Exception as e:
        print(f"Unexpected error in get_seattle_food_joints: {e}")
        return _get_placeholder_food_joints(area, cuisine, price_range)


def _extract_cuisine_from_types(types: List[str]) -> str:
    """Extract cuisine type from Google Places API types."""
    cuisine_keywords = {
        "chinese": "Chinese",
        "japanese": "Japanese",
        "korean": "Korean",
        "italian": "Italian",
        "mexican": "Mexican",
        "thai": "Thai",
        "vietnamese": "Vietnamese",
        "indian": "Indian",
        "french": "French",
        "mediterranean": "Mediterranean",
        "seafood": "Seafood",
        "american": "American"
    }
    
    for type_str in types:
        type_lower = type_str.lower()
        for keyword, cuisine in cuisine_keywords.items():
            if keyword in type_lower:
                return cuisine
    
    return "Restaurant"  # Default


def _price_level_to_range(price_level: Optional[int]) -> str:
    """Convert Google price level (0-4) to $ format."""
    if price_level is None:
        return "$$"
    price_map = {0: "$", 1: "$", 2: "$$", 3: "$$$", 4: "$$$$"}
    return price_map.get(price_level, "$$")


def _extract_area_from_address(address: str) -> str:
    """Extract area/neighborhood from address."""
    for area in SEATTLE_AREAS.keys():
        if area.lower() in address.lower():
            return area
    return "Seattle"


def _get_placeholder_food_joints(area: Optional[str] = None, cuisine: Optional[str] = None, price_range: Optional[str] = None) -> List[Dict]:
    """Fallback placeholder food joints when API is unavailable."""
    # Popular Seattle food joints by area
    all_food_joints = [
        {
            "name": "Pike Place Chowder",
            "area": "Downtown",
            "cuisine": "Seafood",
            "price_range": "$$",
            "address": "1530 Post Alley, Seattle, WA 98101",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Pike+Place+Chowder+Seattle"
        },
        {
            "name": "Canlis",
            "area": "Queen Anne",
            "cuisine": "American",
            "price_range": "$$$$",
            "address": "2576 Aurora Ave N, Seattle, WA 98109",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Canlis+Seattle"
        },
        {
            "name": "Tilikum Place Cafe",
            "area": "Queen Anne",
            "cuisine": "American",
            "price_range": "$$",
            "address": "407 Cedar St, Seattle, WA 98121",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Tilikum+Place+Cafe+Seattle"
        },
        {
            "name": "Mamnoon",
            "area": "Capitol Hill",
            "cuisine": "Mediterranean",
            "price_range": "$$$",
            "address": "1508 Melrose Ave, Seattle, WA 98122",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Mamnoon+Seattle"
        },
        {
            "name": "Stateside",
            "area": "Capitol Hill",
            "cuisine": "Vietnamese",
            "price_range": "$$",
            "address": "300 E Pike St, Seattle, WA 98122",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Stateside+Seattle"
        },
        {
            "name": "Revel",
            "area": "Fremont",
            "cuisine": "Korean",
            "price_range": "$$",
            "address": "403 N 36th St, Seattle, WA 98103",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Revel+Fremont+Seattle"
        },
        {
            "name": "The Walrus and the Carpenter",
            "area": "Ballard",
            "cuisine": "Seafood",
            "price_range": "$$$",
            "address": "4743 Ballard Ave NW, Seattle, WA 98107",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=The+Walrus+and+the+Carpenter+Seattle"
        },
        {
            "name": "Toulouse Petit",
            "area": "Queen Anne",
            "cuisine": "French",
            "price_range": "$$$",
            "address": "601 Queen Anne Ave N, Seattle, WA 98109",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Toulouse+Petit+Seattle"
        },
        {
            "name": "Din Tai Fung",
            "area": "Downtown",
            "cuisine": "Chinese",
            "price_range": "$$",
            "address": "700 Bellevue Way NE, Bellevue, WA 98004",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Din+Tai+Fung+Seattle"
        },
        {
            "name": "Joule",
            "area": "Wallingford",
            "cuisine": "Korean",
            "price_range": "$$$",
            "address": "3506 Stone Way N, Seattle, WA 98103",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Joule+Seattle"
        },
        {
            "name": "Terra Plata",
            "area": "Capitol Hill",
            "cuisine": "Mediterranean",
            "price_range": "$$$",
            "address": "1501 Melrose Ave, Seattle, WA 98122",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Terra+Plata+Seattle"
        },
        {
            "name": "The Pink Door",
            "area": "Downtown",
            "cuisine": "Italian",
            "price_range": "$$$",
            "address": "1919 Post Alley, Seattle, WA 98101",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=The+Pink+Door+Seattle"
        },
        {
            "name": "Salare",
            "area": "Ravenna",
            "cuisine": "American",
            "price_range": "$$$",
            "address": "2404 NE 65th St, Seattle, WA 98115",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Salare+Seattle"
        },
        {
            "name": "Fremont Bowl",
            "area": "Fremont",
            "cuisine": "Japanese",
            "price_range": "$",
            "address": "4250 Fremont Ave N, Seattle, WA 98103",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Fremont+Bowl+Seattle"
        },
        {
            "name": "Marination Ma Kai",
            "area": "West Seattle",
            "cuisine": "Korean",  # Changed to match Google Places API
            "price_range": "$",
            "address": "1660 Harbor Ave SW, Seattle, WA 98126",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Marination+Ma+Kai+Seattle"
        }
    ]
    
    # Apply filters
    filtered = all_food_joints
    
    # Filter by area
    if area:
        area_lower = area.lower()
        filtered = [joint for joint in filtered if area_lower in joint["area"].lower()]
    
    # Filter by cuisine (normalize cuisine names for matching)
    if cuisine:
        cuisine_lower = cuisine.lower()
        # Map variations to standard names
        cuisine_mapping = {
            "korean fusion": "korean",
            "korean-american": "korean",
            "hawaiian-korean": "korean",
            "french/creole": "french",
            "middle eastern": "mediterranean"  # Approximate match
        }
        search_cuisine = cuisine_mapping.get(cuisine_lower, cuisine_lower)
        filtered = [joint for joint in filtered 
                    if search_cuisine in joint["cuisine"].lower() 
                    or joint["cuisine"].lower() in search_cuisine]
    
    # Filter by price range
    if price_range:
        filtered = [joint for joint in filtered if joint["price_range"] == price_range]
    
    return filtered if filtered else all_food_joints


def get_food_areas() -> List[str]:
    """Get list of available food areas in Seattle."""
    return [
        "Capitol Hill",
        "Downtown",
        "Fremont",
        "Queen Anne",
        "Ballard",
        "Wallingford",
        "Ravenna",
        "West Seattle"
    ]


def get_food_cuisines() -> List[str]:
    """Get list of available cuisine types based on Google Places API."""
    return [
        "American",
        "Chinese",
        "French",
        "Indian",
        "Italian",
        "Japanese",
        "Korean",
        "Mediterranean",
        "Mexican",
        "Seafood",
        "Thai",
        "Vietnamese"
    ]


def get_price_ranges() -> List[str]:
    """Get list of available price ranges."""
    return ["$", "$$", "$$$", "$$$$"]

