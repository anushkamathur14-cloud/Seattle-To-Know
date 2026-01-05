import os
import time
import re
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
    "Coffee": "cafe",
    "Bars": "bar",
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
        area: Optional single area filter (e.g., "Capitol Hill", "Downtown", "Fremont")
        cuisine: Optional single cuisine type filter
        price_range: Optional price range filter ($, $$, $$$, $$$$)
    
    Returns:
        List of food joints with name, area, cuisine type, and Google Maps link (up to 180 from Google Places API)
    """
    # If no API key, return placeholder data
    if not GOOGLE_PLACES_API_KEY:
        all_joints = _get_placeholder_food_joints(area, cuisine, price_range)
        return all_joints[:20]
    
    # For Google Places API, use a single optimized search for faster loading
    try:
        all_food_joints = []
        area_filter_active = area and area in SEATTLE_AREAS  # Track if we're filtering by area
        
        # Determine search location based on area filter for better results
        if area_filter_active:
            # Search from the specific area when filter is selected
            search_location = SEATTLE_AREAS[area]
            search_radius = 20000  # 20km radius for specific area (increased for more results)
            print(f"Searching from {area} area with {search_radius}m radius")
        else:
            # Single search from downtown Seattle with larger radius for broader coverage
            search_location = {"lat": 47.6062, "lng": -122.3321}  # Downtown Seattle
            search_radius = 15000  # 15km radius to cover Seattle area
        
        # Use Nearby Search API
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        
        # Determine place type based on cuisine filter for better accuracy
        place_type = "restaurant"  # Default
        if cuisine:
            cuisine_type_mapping = {
                "Chinese": "chinese_restaurant",
                "Japanese": "japanese_restaurant",
                "Korean": "korean_restaurant",
                "Italian": "italian_restaurant",
                "Mexican": "mexican_restaurant",
                "Thai": "thai_restaurant",
                "Vietnamese": "vietnamese_restaurant",
                "Indian": "indian_restaurant",
                "French": "french_restaurant",
                "Mediterranean": "mediterranean_restaurant",
                "Seafood": "seafood_restaurant",
                "Coffee": "cafe",
                "Bars": "bar"
            }
            place_type = cuisine_type_mapping.get(cuisine, "restaurant")
        
        params = {
            "location": f"{search_location['lat']},{search_location['lng']}",
            "radius": search_radius,
            "type": place_type,
            "key": GOOGLE_PLACES_API_KEY
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "OK":
                # Get all results from first page (up to 60)
                places_to_process = data.get("results", [])
                print(f"Found {len(places_to_process)} places from Google Places API (type: {place_type})")
                
                # Fetch all pages (Google allows up to 3 pages = 180 results max)
                page_token = data.get("next_page_token")
                page_count = 1
                max_pages = 3  # Google Places API allows up to 3 pages
                
                while page_token and page_count < max_pages:
                    try:
                        time.sleep(2)  # Google requires 2 second delay before using next_page_token
                        next_params = {
                            "pagetoken": page_token,
                            "key": GOOGLE_PLACES_API_KEY
                        }
                        next_response = requests.get(url, params=next_params, timeout=10)
                        if next_response.status_code == 200:
                            next_data = next_response.json()
                            if next_data.get("status") == "OK":
                                next_results = next_data.get("results", [])
                                places_to_process.extend(next_results)
                                page_count += 1
                                print(f"Got {len(next_results)} more results from page {page_count} (total: {len(places_to_process)})")
                                page_token = next_data.get("next_page_token")
                            else:
                                print(f"Next page error: {next_data.get('status')}")
                                break
                        else:
                            break
                    except Exception as e:
                        print(f"Error fetching next page: {e}")
                        break
                
                # Fetch Place Details for first 30 places only (for faster initial load)
                # Remaining places will use basic data from Nearby Search
                place_ids_to_detail = [p.get("place_id") for p in places_to_process[:30] if p.get("place_id")]
                place_details_cache = {}
                
                print(f"Fetching Place Details for first {len(place_ids_to_detail)} places (optimized for speed)...")
                # Use concurrent requests with minimal delay for faster loading
                for i, place_id in enumerate(place_ids_to_detail):
                    try:
                        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
                        details_params = {
                            "place_id": place_id,
                            "fields": "types,address_components,formatted_address,photos",
                            "key": GOOGLE_PLACES_API_KEY
                        }
                        details_response = requests.get(details_url, params=details_params, timeout=3)
                        if details_response.status_code == 200:
                            details_data = details_response.json()
                            if details_data.get("status") == "OK":
                                place_details_cache[place_id] = details_data.get("result", {})
                        # Minimal delay for faster loading
                        if i < len(place_ids_to_detail) - 1:  # No delay on last request
                            time.sleep(0.005)  # 5ms delay (reduced from 10ms)
                    except Exception as e:
                        print(f"Error fetching place details for {place_id}: {e}")
                
                print(f"Completed fetching Place Details for {len(place_details_cache)} places")
                
                # Process all places
                for place in places_to_process:
                    # Get rating info (no minimum requirements)
                    rating = place.get("rating", 0)
                    user_ratings_total = place.get("user_ratings_total", 0)
                    
                    # Include all places regardless of rating or review count
                    place_id = place.get("place_id", "")
                    
                    # Get comprehensive types from Place Details (more accurate than Nearby Search)
                    place_details = place_details_cache.get(place_id, {})
                    place_types_list = place_details.get("types", place.get("types", []))
                    place_name = place.get("name", "")
                    # Skip editorial_summary to speed up (not fetching it anymore)
                    editorial_summary = ""
                    
                    # Extract cuisine from comprehensive types and name
                    cuisine_type = _extract_cuisine_from_place_details(
                        place_types_list, 
                        place_name, 
                        editorial_summary
                    )
                    
                    # Get price level and convert to $ format
                    price_level = place.get("price_level", 2)
                    price_range_str = _price_level_to_range(price_level)
                    
                    # Get area from address components (more accurate)
                    address = place.get("formatted_address", "")
                    # Try to get address components from details cache
                    address_components = None
                    if place_id in place_details_cache:
                        address_components = place_details_cache[place_id].get("address_components", [])
                    
                    area_name = _extract_area_from_address_components(address, address_components)
                    
                    # Get coordinates for map display
                    location = place.get("geometry", {}).get("location", {})
                    lat = location.get("lat")
                    lng = location.get("lng")
                    
                    # Get photo reference for restaurant image
                    photo_url = None
                    # First try from Place Details (more reliable)
                    photos = place_details.get("photos", [])
                    if not photos:
                        # Fallback to Nearby Search photos
                        photos = place.get("photos", [])
                    
                    if photos and len(photos) > 0:
                        # Get the first photo reference
                        photo_reference = photos[0].get("photo_reference")
                        if photo_reference and GOOGLE_PLACES_API_KEY:
                            # Build photo URL (maxwidth 400px for good quality but reasonable size)
                            photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference={photo_reference}&key={GOOGLE_PLACES_API_KEY}"
                    
                    # Build Google Maps link
                    maps_link = f"https://www.google.com/maps/place/?q=place_id:{place_id}" if place_id else f"https://www.google.com/maps/search/?api=1&query={place.get('name', '').replace(' ', '+')}+Seattle"
                    
                    all_food_joints.append({
                        "name": place.get("name", "Unknown"),
                        "area": area_name,
                        "cuisine": cuisine_type,
                        "price_range": price_range_str,
                        "address": address,
                        "rating": rating,
                        "user_ratings_total": user_ratings_total,
                        "google_maps_link": maps_link,
                        "lat": lat,
                        "lng": lng,
                        "photo_url": photo_url
                    })
            elif data.get("status") != "OK":
                print(f"Google Places API error: {data.get('status')} - {data.get('error_message', '')}")
        except Exception as e:
            print(f"Error fetching from Google Places API: {e}")
        
        # Remove duplicates based on place name and address
        seen = set()
        unique_food_joints = []
        for joint in all_food_joints:
            key = (joint["name"].lower(), joint["address"].lower())
            if key not in seen:
                seen.add(key)
                unique_food_joints.append(joint)
        
        # If no results from API, fall back to placeholder data
        if not unique_food_joints:
            print("No results from Google Places API, using placeholder data")
            all_joints = _get_placeholder_food_joints(area, cuisine, price_range)
            return all_joints[:20]
        
        # Sort by rating (descending)
        unique_food_joints.sort(key=lambda x: x.get("rating", 0), reverse=True)
        
        # Apply simple filters: single area, single cuisine, price range
        filtered = unique_food_joints.copy()
        
        # Filter by area (single selection)
        # CRITICAL: When we search from an area's coordinates, the search location IS the filter
        # We should NOT filter by extracted area names - just trust the search results
        if area and area in SEATTLE_AREAS:
            # Since we already searched from this area's coordinates with 20km radius,
            # ALL results are already in/near that area. Don't filter by area name.
            # The search location is the primary and most accurate filter.
            print(f"Area filter '{area}': Using all {len(unique_food_joints)} results from area search (search location is the filter)")
            # No additional filtering needed - all results are from the area search
            filtered = unique_food_joints.copy()
        elif area:
            # If area is specified but not in our list, try name-based matching
            area_lower = area.lower().strip()
            filtered_results = []
            for joint in filtered:
                joint_area = joint.get("area", "").lower().strip()
                joint_address = joint.get("address", "").lower()
                
                if (area_lower == joint_area or 
                    area_lower in joint_area or 
                    area_lower in joint_address):
                    filtered_results.append(joint)
            filtered = filtered_results
            print(f"Area filter '{area}': {len(filtered)} restaurants found (from {len(unique_food_joints)} total)")
        
        # Filter by cuisine (single selection)
        if cuisine:
            cuisine_lower = cuisine.lower().strip()
            filtered_results = []
            for joint in filtered:
                joint_cuisine = joint.get("cuisine", "").lower().strip()
                joint_name = joint.get("name", "").lower()
                
                # Exact match
                if cuisine_lower == joint_cuisine:
                    filtered_results.append(joint)
                    continue
                
                # If cuisine is "Restaurant", try matching by name
                if joint_cuisine == "restaurant":
                    cuisine_keywords = {
                        "japanese": ["japanese", "sushi", "ramen", "izakaya", "teriyaki"],
                        "chinese": ["chinese", "dim sum", "peking", "szechuan"],
                        "korean": ["korean", "kbbq", "bibimbap", "kimchi"],
                        "italian": ["italian", "pizza", "pasta", "trattoria"],
                        "mexican": ["mexican", "taco", "burrito", "taqueria"],
                        "thai": ["thai", "pad thai"],
                        "vietnamese": ["vietnamese", "pho", "banh mi"],
                        "indian": ["indian", "curry", "tandoor"],
                        "french": ["french", "bistro"],
                        "mediterranean": ["mediterranean", "greek", "falafel"],
                        "seafood": ["seafood", "fish", "oyster", "crab", "lobster", "sushi"],
                        "american": ["american", "burger", "bbq", "grill"],
                        "coffee": ["coffee", "cafe", "espresso"],
                        "bars": ["bar", "pub", "brewery"],
                    }
                    keywords = cuisine_keywords.get(cuisine_lower, [])
                    if any(keyword in joint_name for keyword in keywords):
                        filtered_results.append(joint)
            
            filtered = filtered_results
        
        # Filter by price range
        if price_range:
            filtered = [joint for joint in filtered if joint.get("price_range") == price_range]
        
        # Return all filtered results (no limit - show as many as Google Places API allows, up to 180)
        food_joints = filtered
        print(f"Returning {len(food_joints)} food joints (filtered from {len(unique_food_joints)} total)")
        
        return food_joints
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching food from Google Places API: {e}")
        all_joints = _get_placeholder_food_joints(area, cuisine, price_range)
        return all_joints[:20]
    except Exception as e:
        print(f"Unexpected error in get_seattle_food_joints: {e}")
        all_joints = _get_placeholder_food_joints(area, cuisine, price_range)
        return all_joints[:20]


def _extract_cuisine_from_place_details(types: List[str], name: str = "", editorial_summary: str = "") -> str:
    """Extract place type from Google Places API - returns Cafe, Bar, or Restaurant."""
    import re
    
    # Map Google's types to our 3 simple classifications
    cafe_types = ["cafe", "coffee_shop", "bakery"]
    bar_types = ["bar", "night_club", "lounge", "pub", "brewery", "sports_bar", "cocktail_bar", "wine_bar"]
    restaurant_types = [
        "restaurant", "food", "meal_takeaway", "meal_delivery",
        "japanese_restaurant", "chinese_restaurant", "korean_restaurant",
        "italian_restaurant", "mexican_restaurant", "thai_restaurant",
        "vietnamese_restaurant", "indian_restaurant", "french_restaurant",
        "mediterranean_restaurant", "american_restaurant", "seafood_restaurant",
        "sushi_bar", "pizza_restaurant", "steak_house", "barbecue_restaurant",
        "fast_food_restaurant", "brunch_restaurant", "breakfast_restaurant"
    ]
    
    # PRIORITY 1: Check Google's types array directly
    for place_type in types:
        type_lower = place_type.lower()
        
        # Check for cafe types first
        if type_lower in cafe_types:
            return "Cafe"
        
        # Check for bar types
        if type_lower in bar_types:
            return "Bar"
        
        # Check for restaurant types (including all cuisine-specific restaurants)
        if type_lower in restaurant_types or type_lower.endswith("_restaurant"):
            return "Restaurant"
    
    # PRIORITY 2: Fallback to name-based matching
    if name:
        name_lower = name.lower()
        
        # Check for cafe keywords
        cafe_keywords = ["cafe", "coffee", "espresso", "latte", "cappuccino", "roastery", "roast", "barista"]
        for keyword in cafe_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', name_lower):
                return "Cafe"
        
        # Check for bar keywords
        bar_keywords = ["bar", "pub", "brewery", "tavern", "cocktail", "lounge", "nightclub", "speakeasy", "whiskey", "wine bar", "beer", "taproom"]
        for keyword in bar_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', name_lower):
                return "Bar"
    
    # Default to "Restaurant" for all other places
    return "Restaurant"


def _price_level_to_range(price_level: Optional[int]) -> str:
    """Convert Google price level (0-4) to $ format."""
    if price_level is None:
        return "$$"
    price_map = {0: "$", 1: "$", 2: "$$", 3: "$$$", 4: "$$$$"}
    return price_map.get(price_level, "$$")


def _extract_area_from_address_components(address: str, address_components: Optional[List[Dict]] = None) -> str:
    """Extract area/neighborhood from address using Google Places API address components."""
    # First try to use address_components if available (more accurate)
    if address_components:
        # Look for neighborhood, sublocality, or locality_level_1
        for component in address_components:
            types = component.get("types", [])
            long_name = component.get("long_name", "")
            
            # Check for neighborhood (most specific)
            if "neighborhood" in types or "sublocality" in types or "sublocality_level_1" in types:
                # Map common neighborhood names to our area names
                area_mapping = {
                    "capitol hill": "Capitol Hill",
                    "downtown": "Downtown",
                    "fremont": "Fremont",
                    "queen anne": "Queen Anne",
                    "ballard": "Ballard",
                    "wallingford": "Wallingford",
                    "ravenna": "Ravenna",
                    "west seattle": "West Seattle",
                    "pioneer square": "Downtown",
                    "belltown": "Downtown",
                    "south lake union": "Downtown",
                    "university district": "Ravenna",
                    "udistrict": "Ravenna",
                }
                
                long_name_lower = long_name.lower()
                for key, area in area_mapping.items():
                    if key in long_name_lower:
                        return area
                
                # If it matches one of our areas directly, return it
                for area in SEATTLE_AREAS.keys():
                    if area.lower() in long_name_lower:
                        return area
    
    # Fallback: parse from formatted address
    address_lower = address.lower()
    
    # Check for area names in address (order matters - check specific first)
    area_mapping = {
        "fremont": "Fremont",
        "wallingford": "Wallingford",
        "ballard": "Ballard",
        "capitol hill": "Capitol Hill",
        "queen anne": "Queen Anne",
        "ravenna": "Ravenna",
        "west seattle": "West Seattle",
        # Downtown variations (check after specific areas)
        "pioneer square": "Downtown",
        "belltown": "Downtown",
        "south lake union": "Downtown",
        "downtown": "Downtown",
        "university district": "Ravenna",
        "udistrict": "Ravenna",
    }
    
    # Check for area names in address (use word boundaries for better accuracy)
    for key, area in area_mapping.items():
        # Use word boundary matching for better accuracy
        pattern = r'\b' + re.escape(key) + r'\b'
        if re.search(pattern, address_lower):
            return area
    
    # Direct match with our areas (case-insensitive)
    for area in SEATTLE_AREAS.keys():
        pattern = r'\b' + re.escape(area.lower()) + r'\b'
        if re.search(pattern, address_lower):
            return area
    
    # If no match, try to extract from common address patterns
    # Many Seattle addresses have format: "Street, Neighborhood, Seattle, WA"
    parts = address.split(',')
    if len(parts) >= 2:
        # Check the part before "Seattle" (usually the neighborhood)
        for part in parts:
            part_lower = part.strip().lower()
            for key, area in area_mapping.items():
                if key in part_lower:
                    return area
    
    return "Seattle"  # Default fallback


def _filter_food_joints_by_multiple(
    food_joints: List[Dict],
    areas: Optional[List[str]] = None,
    cuisines: Optional[List[str]] = None,
    price_range: Optional[str] = None
) -> List[Dict]:
    """
    Filter food joints by multiple areas, cuisines, and price range.
    Returns joints that match ANY of the selected areas AND ANY of the selected cuisines.
    """
    filtered = food_joints.copy()
    
    # Filter by multiple areas (OR logic - match any selected area)
    if areas and len(areas) > 0:
        areas_normalized = [a.lower().strip() for a in areas]
        filtered_results = []
        for joint in filtered:
            joint_area = joint.get("area", "").lower().strip()
            matches = False
            
            # If joint area is "Seattle" (default), include it for any area filter
            # This handles cases where area extraction didn't find a specific match
            if joint_area == "seattle":
                matches = True
            else:
                # Check for exact or partial match
                for area_norm in areas_normalized:
                    if area_norm == joint_area:
                        matches = True
                        break
                    elif area_norm in joint_area or joint_area in area_norm:
                        matches = True
                        break
            
            if matches:
                filtered_results.append(joint)
        filtered = filtered_results
        print(f"After area filtering ({areas}): {len(filtered)} results")
    
    # Filter by multiple cuisines (OR logic - match any selected cuisine)
    if cuisines and len(cuisines) > 0:
        cuisines_normalized = [c.lower().strip() for c in cuisines]
        filtered_results = []
        for joint in filtered:
            joint_cuisine = joint.get("cuisine", "").lower().strip()
            matches = False
            
            # If joint cuisine is "Restaurant" (default), still try to match based on name
            # This handles cases where cuisine extraction didn't find a specific match
            if joint_cuisine == "restaurant":
                # Try to extract cuisine from name as fallback
                joint_name = joint.get("name", "").lower()
                # Check if cuisine keyword appears in the restaurant name
                cuisine_keywords_in_name = {
                    "japanese": ["japanese", "sushi", "ramen", "izakaya", "teriyaki", "sashimi", "tempura"],
                    "chinese": ["chinese", "dim sum", "peking", "szechuan", "cantonese", "mandarin"],
                    "korean": ["korean", "kbbq", "bibimbap", "kimchi", "bulgogi"],
                    "italian": ["italian", "pizza", "pasta", "trattoria", "ristorante", "gelato"],
                    "mexican": ["mexican", "taco", "burrito", "taqueria", "mexico", "quesadilla"],
                    "thai": ["thai", "pad thai", "curry", "tom yum"],
                    "vietnamese": ["vietnamese", "pho", "banh mi", "vietnam"],
                    "indian": ["indian", "curry", "tandoor", "masala", "naan", "biryani"],
                    "french": ["french", "bistro", "brasserie", "crepe", "croissant"],
                    "mediterranean": ["mediterranean", "greek", "falafel", "hummus", "gyro"],
                    "seafood": ["seafood", "fish", "oyster", "crab", "lobster", "shrimp", "salmon", "sushi"],
                    "american": ["american", "burger", "bbq", "grill", "steak", "diner"],
                    "coffee": ["coffee", "cafe", "espresso", "latte", "cappuccino", "roastery"],
                    "bars": ["bar", "pub", "tavern", "cocktail", "brewery", "lounge"],
                }
                for cuisine_norm in cuisines_normalized:
                    keywords = cuisine_keywords_in_name.get(cuisine_norm, [cuisine_norm])
                    if any(keyword in joint_name for keyword in keywords):
                        matches = True
                        break
            else:
                # Normal matching for specific cuisines
                for cuisine_norm in cuisines_normalized:
                    # Exact match (preferred) - must match exactly
                    if cuisine_norm == joint_cuisine:
                        matches = True
                        break
                    # Substring match (for variations like "Korean Fusion" matching "Korean")
                    # But be careful - only match if the cuisine name is long enough to avoid false matches
                    elif len(cuisine_norm) >= 4 and (cuisine_norm in joint_cuisine or joint_cuisine in cuisine_norm):
                        matches = True
                        break
            
            if matches:
                filtered_results.append(joint)
        filtered = filtered_results
        
        # Debug: print how many results after cuisine filtering
        print(f"After cuisine filtering ({cuisines}): {len(filtered)} results")
        if filtered:
            print(f"Sample cuisines in filtered results: {[j.get('cuisine') for j in filtered[:5]]}")
        elif not filtered and len(food_joints) > 0:
            # Show what cuisines were available before filtering
            available_before = [j.get('cuisine') for j in food_joints[:20]]
            print(f"WARNING: No cuisine matches found. Available cuisines before filtering: {set(available_before)}")
    
    # Filter by price range (single selection)
    if price_range:
        filtered = [joint for joint in filtered if joint.get("price_range") == price_range]
    
    return filtered


def _get_placeholder_food_joints(area: Optional[str] = None, cuisine: Optional[str] = None, price_range: Optional[str] = None) -> List[Dict]:
    """Fallback placeholder food joints when API is unavailable. Filters by single area, single cuisine, and price range."""
    # Popular Seattle food joints by area
    all_food_joints = [
        {
            "name": "Pike Place Chowder",
            "area": "Downtown",
            "cuisine": "Seafood",
            "price_range": "$$",
            "address": "1530 Post Alley, Seattle, WA 98101",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Pike+Place+Chowder+Seattle",
            "lat": 47.6085,
            "lng": -122.3403
        },
        {
            "name": "Canlis",
            "area": "Queen Anne",
            "cuisine": "American",
            "price_range": "$$$$",
            "address": "2576 Aurora Ave N, Seattle, WA 98109",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Canlis+Seattle",
            "lat": 47.6375,
            "lng": -122.3467
        },
        {
            "name": "Tilikum Place Cafe",
            "area": "Queen Anne",
            "cuisine": "American",
            "price_range": "$$",
            "address": "407 Cedar St, Seattle, WA 98121",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Tilikum+Place+Cafe+Seattle",
            "lat": 47.6200,
            "lng": -122.3500
        },
        {
            "name": "Mamnoon",
            "area": "Capitol Hill",
            "cuisine": "Mediterranean",
            "price_range": "$$$",
            "address": "1508 Melrose Ave, Seattle, WA 98122",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Mamnoon+Seattle",
            "lat": 47.6145,
            "lng": -122.3200
        },
        {
            "name": "Stateside",
            "area": "Capitol Hill",
            "cuisine": "Vietnamese",
            "price_range": "$$",
            "address": "300 E Pike St, Seattle, WA 98122",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Stateside+Seattle",
            "lat": 47.6140,
            "lng": -122.3250
        },
        {
            "name": "Revel",
            "area": "Fremont",
            "cuisine": "Korean",
            "price_range": "$$",
            "address": "403 N 36th St, Seattle, WA 98103",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Revel+Fremont+Seattle",
            "lat": 47.6530,
            "lng": -122.3500
        },
        {
            "name": "The Walrus and the Carpenter",
            "area": "Ballard",
            "cuisine": "Seafood",
            "price_range": "$$$",
            "address": "4743 Ballard Ave NW, Seattle, WA 98107",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=The+Walrus+and+the+Carpenter+Seattle",
            "lat": 47.6680,
            "lng": -122.3840
        },
        {
            "name": "Toulouse Petit",
            "area": "Queen Anne",
            "cuisine": "French",
            "price_range": "$$$",
            "address": "601 Queen Anne Ave N, Seattle, WA 98109",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Toulouse+Petit+Seattle",
            "lat": 47.6250,
            "lng": -122.3560
        },
        {
            "name": "Din Tai Fung",
            "area": "Downtown",
            "cuisine": "Chinese",
            "price_range": "$$",
            "address": "700 Bellevue Way NE, Bellevue, WA 98004",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Din+Tai+Fung+Seattle",
            "lat": 47.6100,
            "lng": -122.3400
        },
        {
            "name": "Joule",
            "area": "Wallingford",
            "cuisine": "Korean",
            "price_range": "$$$",
            "address": "3506 Stone Way N, Seattle, WA 98103",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Joule+Seattle",
            "lat": 47.6560,
            "lng": -122.3360
        },
        {
            "name": "Terra Plata",
            "area": "Capitol Hill",
            "cuisine": "Mediterranean",
            "price_range": "$$$",
            "address": "1501 Melrose Ave, Seattle, WA 98122",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Terra+Plata+Seattle",
            "lat": 47.6145,
            "lng": -122.3200
        },
        {
            "name": "The Pink Door",
            "area": "Downtown",
            "cuisine": "Italian",
            "price_range": "$$$",
            "address": "1919 Post Alley, Seattle, WA 98101",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=The+Pink+Door+Seattle",
            "lat": 47.6085,
            "lng": -122.3403
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
    
    # Return up to 20 results
    return filtered[:20]


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
        "Vietnamese",
        "Coffee",
        "Bars"
    ]


def get_price_ranges() -> List[str]:
    """Get list of available price ranges."""
    return ["$", "$$", "$$$", "$$$$"]

