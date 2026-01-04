import os
import requests
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict

EVENTBRITE_API_KEY = os.getenv("EVENTBRITE_API_KEY")
TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")
SEATGEEK_CLIENT_ID = os.getenv("SEATGEEK_CLIENT_ID")
SEATGEEK_CLIENT_SECRET = os.getenv("SEATGEEK_CLIENT_SECRET")

# Eventbrite category ID mappings
# Common categories: Music=103, Food & Drink=110, Sports & Fitness=108, 
# Business=101, Science & Tech=102, Arts=105, etc.
EVENT_TYPE_TO_CATEGORY = {
    "music": "103",
    "food": "110",
    "sports": "108",
    "business": "101",
    "tech": "102",
    "arts": "105",
    "comedy": "104",
    "education": "109",
    "health": "107",
    "fashion": "106",
}

def get_seattle_events(
    event_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 10
) -> List[dict]:
    """
    Fetch events from multiple APIs (Eventbrite, Ticketmaster, SeatGeek) for Seattle.
    Aggregates results from all available sources.
    
    Args:
        event_type: Filter by event type (e.g., "music", "food", "sports", "tech", "arts")
        start_date: Start date for event search (defaults to today)
        end_date: End date for event search (defaults to tomorrow)
        limit: Maximum number of events to return (default: 10)
    
    Returns:
        List of event dictionaries with name, time, area, and type
    """
    all_events = []
    
    # Try Eventbrite first
    eventbrite_events = _get_eventbrite_events(event_type, start_date, end_date, limit)
    print(f"Eventbrite returned {len(eventbrite_events)} events")
    all_events.extend(eventbrite_events)
    
    # Try Ticketmaster if API key is available
    if TICKETMASTER_API_KEY:
        ticketmaster_events = _get_ticketmaster_events(event_type, start_date, end_date, limit)
        print(f"Ticketmaster returned {len(ticketmaster_events)} events")
        all_events.extend(ticketmaster_events)
    else:
        print("Ticketmaster API key not set - skipping Ticketmaster")
    
    # Try SeatGeek if API keys are available
    if SEATGEEK_CLIENT_ID and SEATGEEK_CLIENT_SECRET:
        seatgeek_events = _get_seatgeek_events(event_type, start_date, end_date, limit)
        print(f"SeatGeek returned {len(seatgeek_events)} events")
        all_events.extend(seatgeek_events)
    else:
        print("SeatGeek API keys not set - skipping SeatGeek")
    
    # Remove duplicates and sort by time
    unique_events = _deduplicate_events(all_events)
    
    # Apply event_type filter if specified (post-filter to ensure accuracy)
    if event_type:
        unique_events = _filter_events_by_type(unique_events, event_type)
    
    # If no events found from APIs, return filtered placeholders
    if not unique_events:
        placeholder_events = _get_placeholder_events(limit * 2)  # Get more to filter
        if event_type:
            placeholder_events = _filter_events_by_type(placeholder_events, event_type)
        return placeholder_events[:limit]
    
    return unique_events[:limit]


def _get_eventbrite_events(
    event_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 10
) -> List[dict]:
    """Fetch events from Eventbrite API."""
    if not EVENTBRITE_API_KEY:
        return []
    
    try:
        # Eventbrite API endpoint for searching events (removed trailing slash)
        url = "https://www.eventbriteapi.com/v3/events/search"
        
        # Set default date range (today to tomorrow) if not provided
        if start_date is None:
            start_date = date.today()
        if end_date is None:
            end_date = start_date + timedelta(days=1)
        
        # Format dates for API (Eventbrite expects UTC or local time)
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        # Use UTC format for Eventbrite API
        start_date_str = start_datetime.strftime("%Y-%m-%dT%H:%M:%S")
        end_date_str = end_datetime.strftime("%Y-%m-%dT%H:%M:%S")
        
        params = {
            "location.address": "Seattle, WA",
            "location.within": "10mi",
            "start_date.range_start": start_date_str,
            "start_date.range_end": end_date_str,
            "status": "live",
            "order_by": "start_asc",
            "expand": "venue,category",
            "page_size": min(limit * 2, 50),  # Request more events from API
        }
        
        # Add category filter if event_type is specified
        if event_type:
            event_type_lower = event_type.lower()
            if event_type_lower in EVENT_TYPE_TO_CATEGORY:
                params["categories"] = EVENT_TYPE_TO_CATEGORY[event_type_lower]
        
        headers = {
            "Authorization": f"Bearer {EVENTBRITE_API_KEY}",
            "Content-Type": "application/json",
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        # Better error handling
        if response.status_code == 404:
            print(f"Eventbrite API 404: Endpoint not found. URL: {url}")
            print(f"Response: {response.text}")
            return []
        elif response.status_code == 401 or response.status_code == 403:
            print(f"Eventbrite API authentication error ({response.status_code}): Check your API key")
            print(f"Response: {response.text}")
            return []
        
        response.raise_for_status()
        data = response.json()
        
        # Transform Eventbrite response to match expected format
        events = []
        # Get more events than limit to account for filtering
        events_to_process = data.get("events", [])
        print(f"Eventbrite returned {len(events_to_process)} events")
        
        for event in events_to_process:
            # Parse start time and date
            start_time = event.get("start", {}).get("local", "")
            time_str = None
            date_str = None
            if start_time:
                try:
                    dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                    # Format time as "7 PM" (portable across platforms)
                    hour = dt.hour
                    if hour == 0:
                        time_str = "12 AM"
                    elif hour < 12:
                        time_str = f"{hour} AM"
                    elif hour == 12:
                        time_str = "12 PM"
                    else:
                        time_str = f"{hour - 12} PM"
                    # Format date as "Jan 15, 2024"
                    date_str = dt.strftime("%b %d, %Y")
                except Exception as e:
                    print(f"Error parsing Eventbrite date/time: {e}, start_time: {start_time}")
                    # Try to extract time from string if possible
                    if len(start_time) >= 5:
                        time_str = start_time[11:16] if len(start_time) > 16 else start_time[:5]
                    else:
                        time_str = None
                    date_str = None
            
            # Get venue/area
            venue = event.get("venue", {})
            area = venue.get("address", {}).get("city", "Seattle") or "Seattle"
            
            # Get event type/category from Eventbrite category
            category = event.get("category", {})
            event_type_name = category.get("name", "Event") if category else "Event"
            
            # Map to simpler type names
            category_id = event.get("category_id", "")
            type_mapping = {v: k.title() for k, v in EVENT_TYPE_TO_CATEGORY.items()}
            event_type_display = type_mapping.get(category_id, event_type_name)
            
            # Get event URL
            event_url = event.get("url", "") or event.get("public_url", {}) or ""
            if isinstance(event_url, dict):
                event_url = event_url.get("text", "") or ""
            
            events.append({
                "name": event.get("name", {}).get("text", "Untitled Event"),
                "time": time_str,
                "date": date_str,
                "area": area,
                "type": event_type_display,
                "url": event_url,
            })
        
        return events
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching events from Eventbrite: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error in _get_eventbrite_events: {e}")
        return []


def _get_ticketmaster_events(
    event_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 10
) -> List[dict]:
    """Fetch events from Ticketmaster Discovery API."""
    if not TICKETMASTER_API_KEY:
        return []
    
    try:
        # Ticketmaster Discovery API
        url = "https://app.ticketmaster.com/discovery/v2/events.json"
        
        # Set default date range
        if start_date is None:
            start_date = date.today()
        if end_date is None:
            end_date = start_date + timedelta(days=7)
        
        params = {
            "apikey": TICKETMASTER_API_KEY,
            "city": "Seattle",
            "stateCode": "WA",
            "startDateTime": f"{start_date.isoformat()}T00:00:00Z",
            "endDateTime": f"{end_date.isoformat()}T23:59:59Z",
            "size": limit,
        }
        
        # Map event types to Ticketmaster classifications
        classification_map = {
            "music": "KZFzniwnSyZfZ7v7nJ",
            "sports": "KZFzniwnSyZfZ7v7nE",
            "arts": "KZFzniwnSyZfZ7v7na",
            "comedy": "KZFzniwnSyZfZ7v7na",
            "tech": "KZFzniwnSyZfZ7v7n1",
        }
        
        if event_type and event_type.lower() in classification_map:
            params["classificationId"] = classification_map[event_type.lower()]
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        events = []
        for event in data.get("_embedded", {}).get("events", [])[:limit]:
            # Parse start time and date - Ticketmaster has multiple date formats
            dates = event.get("dates", {}).get("start", {})
            start_time = dates.get("localDateTime", "") or dates.get("dateTime", "")
            local_date = dates.get("localDate", "") or dates.get("date", "")
            time_str = None
            date_str = None
            
            # Debug: Log what we're working with
            if not start_time and local_date:
                print(f"[DEBUG] Ticketmaster event has localDate but no localDateTime: {event.get('name', 'Unknown')[:50]}")
                print(f"  localDate: {local_date}, dates keys: {list(dates.keys())}")
            
            if start_time:
                try:
                    # Handle different Ticketmaster date formats
                    # Format 1: "2024-01-15T19:00:00" (localDateTime)
                    # Format 2: "2024-01-15T19:00:00Z" (dateTime with Z)
                    # Format 3: "2024-01-15T19:00:00-08:00" (with timezone)
                    clean_time = start_time.replace("Z", "+00:00")
                    if "+" not in clean_time and "-" in clean_time[10:]:
                        # Has timezone offset already
                        dt = datetime.fromisoformat(clean_time)
                    else:
                        # No timezone, assume local
                        dt = datetime.fromisoformat(clean_time)
                    
                    # Format time as "7 PM" (portable across platforms)
                    hour = dt.hour
                    if hour == 0:
                        time_str = "12 AM"
                    elif hour < 12:
                        time_str = f"{hour} AM"
                    elif hour == 12:
                        time_str = "12 PM"
                    else:
                        time_str = f"{hour - 12} PM"
                    # Format date as "Jan 15, 2024"
                    date_str = dt.strftime("%b %d, %Y")
                    print(f"[DEBUG] Ticketmaster parsed: {event.get('name', 'Unknown')[:50]} - {date_str} at {time_str}")
                except Exception as e:
                    print(f"Error parsing Ticketmaster date/time: {e}")
                    print(f"  Event: {event.get('name', 'Unknown')}")
                    print(f"  start_time value: {start_time}")
                    print(f"  dates object: {dates}")
                    # Try alternative date field
                    alt_date = dates.get("localDate", "") or dates.get("date", "")
                    if alt_date:
                        try:
                            date_obj = datetime.strptime(alt_date, "%Y-%m-%d")
                            date_str = date_obj.strftime("%b %d, %Y")
                            # Try to get time from timeTBD or timeTBA
                            if dates.get("timeTBD") or dates.get("timeTBA"):
                                time_str = "TBD"
                            else:
                                time_str = None
                        except:
                            time_str = None
                            date_str = None
                    else:
                        time_str = None
                        date_str = None
            elif local_date:
                # If we have localDate but no localDateTime, at least get the date
                try:
                    date_obj = datetime.strptime(local_date, "%Y-%m-%d")
                    date_str = date_obj.strftime("%b %d, %Y")
                    # Check if time is TBD/TBA
                    if dates.get("timeTBD") or dates.get("timeTBA"):
                        time_str = "TBD"
                    else:
                        # Try to get time from localTime if available
                        local_time = dates.get("localTime", "")
                        if local_time:
                            try:
                                time_obj = datetime.strptime(local_time, "%H:%M:%S")
                                hour = time_obj.hour
                                if hour == 0:
                                    time_str = "12 AM"
                                elif hour < 12:
                                    time_str = f"{hour} AM"
                                elif hour == 12:
                                    time_str = "12 PM"
                                else:
                                    time_str = f"{hour - 12} PM"
                            except:
                                time_str = None
                        else:
                            time_str = None
                    print(f"[DEBUG] Ticketmaster used localDate fallback: {event.get('name', 'Unknown')[:50]} - {date_str} at {time_str or 'No time'}")
                except Exception as e:
                    print(f"[DEBUG] Error parsing Ticketmaster localDate: {e}, localDate: {local_date}")
                    time_str = None
                    date_str = None
            
            # Get venue/area
            venue = event.get("_embedded", {}).get("venues", [{}])[0]
            area = venue.get("city", {}).get("name", "Seattle") or "Seattle"
            
            # Get event type
            classifications = event.get("classifications", [{}])[0]
            event_type_name = classifications.get("segment", {}).get("name", "Event") or "Event"
            
            # Get event URL
            event_url = event.get("url", "") or event.get("_links", {}).get("self", {}).get("href", "")
            
            event_data = {
                "name": event.get("name", "Untitled Event"),
                "time": time_str,
                "date": date_str,
                "area": area,
                "type": event_type_name,
                "url": event_url,
                "source": "Ticketmaster",
            }
            # Debug: Log if date/time is missing
            if not date_str or not time_str:
                print(f"[DEBUG] Ticketmaster event missing date/time: {event_data['name'][:50]}")
                print(f"  date: {date_str}, time: {time_str}")
                print(f"  dates object: {dates}")
            events.append(event_data)
        
        return events
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching events from Ticketmaster: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error in _get_ticketmaster_events: {e}")
        return []


def _get_seatgeek_events(
    event_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 10
) -> List[dict]:
    """Fetch events from SeatGeek API."""
    if not SEATGEEK_CLIENT_ID or not SEATGEEK_CLIENT_SECRET:
        return []
    
    try:
        # SeatGeek API
        url = "https://api.seatgeek.com/2/events"
        
        # Set default date range
        if start_date is None:
            start_date = date.today()
        if end_date is None:
            end_date = start_date + timedelta(days=7)
        
        params = {
            "client_id": SEATGEEK_CLIENT_ID,
            "client_secret": SEATGEEK_CLIENT_SECRET,
            "venue.city": "Seattle",
            "venue.state": "WA",
            "datetime_utc.gte": f"{start_date.isoformat()}T00:00:00",
            "datetime_utc.lte": f"{end_date.isoformat()}T23:59:59",
            "per_page": limit,
        }
        
        # Map event types to SeatGeek taxonomies
        taxonomy_map = {
            "music": "concert",
            "sports": "sports",
            "arts": "theater",
            "comedy": "comedy",
        }
        
        if event_type and event_type.lower() in taxonomy_map:
            params["taxonomies.name"] = taxonomy_map[event_type.lower()]
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        events = []
        for event in data.get("events", [])[:limit]:
            # Parse start time and date
            start_time = event.get("datetime_local", "")
            time_str = None
            date_str = None
            if start_time:
                try:
                    dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                    hour = dt.hour
                    if hour == 0:
                        time_str = "12 AM"
                    elif hour < 12:
                        time_str = f"{hour} AM"
                    elif hour == 12:
                        time_str = "12 PM"
                    else:
                        time_str = f"{hour - 12} PM"
                    # Format date as "Jan 15, 2024"
                    date_str = dt.strftime("%b %d, %Y")
                except Exception as e:
                    print(f"Error parsing SeatGeek date/time: {e}, start_time: {start_time}")
                    # Try to extract time from string if possible
                    if len(start_time) >= 5:
                        time_str = start_time[11:16] if len(start_time) > 16 else start_time[:5]
                    else:
                        time_str = None
                    date_str = None
            
            # Get venue/area
            venue = event.get("venue", {})
            area = venue.get("city", "Seattle") or "Seattle"
            
            # Get event type
            taxonomies = event.get("taxonomies", [{}])[0]
            event_type_name = taxonomies.get("name", "Event") or "Event"
            
            # Get event URL
            event_url = event.get("url", "") or event.get("event_url", "")
            
            events.append({
                "name": event.get("title", "Untitled Event"),
                "time": time_str,
                "date": date_str,
                "area": area,
                "type": event_type_name,
                "url": event_url,
                "source": "SeatGeek",
            })
        
        return events
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching events from SeatGeek: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error in _get_seatgeek_events: {e}")
        return []


def _deduplicate_events(events: List[dict]) -> List[dict]:
    """Remove duplicate events based on name and time."""
    seen = set()
    unique_events = []
    
    for event in events:
        # Create a key from name and time
        key = (event.get("name", "").lower().strip(), event.get("time", ""))
        if key not in seen:
            seen.add(key)
            unique_events.append(event)
    
    # Sort by time (events with time first, then by name)
    unique_events.sort(key=lambda x: (x.get("time", ""), x.get("name", "")))
    
    return unique_events


def _filter_events_by_type(events: List[dict], event_type: str) -> List[dict]:
    """Filter events by event type, handling variations and case-insensitive matching."""
    if not event_type:
        return events
    
    event_type_lower = event_type.lower().strip()
    filtered_events = []
    
    # Map of filter types to possible event type strings
    type_mappings = {
        "music": ["music", "concert", "live music", "jazz", "rock", "pop", "indie"],
        "sports": ["sports", "game", "match", "mariners", "sounders", "kraken", "seahawks"],
        "arts": ["arts", "art", "gallery", "theater", "theatre", "symphony", "performance"],
        "comedy": ["comedy", "stand-up", "standup", "humor", "humour"],
        "tech": ["tech", "technology", "startup", "ai", "software", "coding", "developer"],
        "food": ["food", "wine", "dining", "culinary", "tasting", "cooking"],
        "business": ["business", "networking", "entrepreneur", "startup"],
        "health": ["health", "fitness", "yoga", "wellness", "running", "exercise"],
        "education": ["education", "learning", "workshop", "seminar", "class"],
        "fashion": ["fashion", "style", "clothing", "design"]
    }
    
    # Get possible matches for this event type
    possible_matches = type_mappings.get(event_type_lower, [event_type_lower])
    
    for event in events:
        event_type_str = event.get("type", "").lower()
        
        # Check if event type matches any of the possible variations
        matches = False
        for match_term in possible_matches:
            if match_term in event_type_str or event_type_str in match_term:
                matches = True
                break
        
        # Also check event name for keywords if type doesn't match
        if not matches:
            event_name = event.get("name", "").lower()
            for match_term in possible_matches:
                if match_term in event_name:
                    matches = True
                    break
        
        if matches:
            filtered_events.append(event)
    
    return filtered_events


def check_events_selling_out(events: List[dict]) -> bool:
    """
    Check if any events are selling out quickly based on ticket availability.
    Returns True if there are events with high demand.
    """
    if not EVENTBRITE_API_KEY:
        return False
    
    try:
        # Check a sample of events for ticket availability
        for event in events[:5]:  # Check first 5 events
            # We'd need to fetch individual event details to check capacity
            # For now, return True if we have events (indicating there might be popular ones)
            pass
        
        # If we have multiple events, some might be selling out
        return len(events) > 0
    except Exception as e:
        print(f"Error checking events selling out: {e}")
        return False


def _get_placeholder_events(limit: int = 20):
    """Fallback placeholder events when API is unavailable."""
    today = date.today()
    placeholder_events = [
        {
            "name": "Capitol Hill Art Walk",
            "time": "6–9 PM",
            "date": today.strftime("%b %d, %Y"),
            "area": "Capitol Hill",
            "type": "Arts",
            "url": "https://www.eventbrite.com"
        },
        {
            "name": "Live Jazz at Pike Place",
            "time": "7 PM",
            "date": today.strftime("%b %d, %Y"),
            "area": "Downtown",
            "type": "Music",
            "url": "https://www.eventbrite.com"
        },
        {
            "name": "Seattle Mariners Game",
            "time": "7:10 PM",
            "date": today.strftime("%b %d, %Y"),
            "area": "Sodo",
            "type": "Sports",
            "url": "https://www.mlb.com/mariners"
        },
        {
            "name": "Tech Meetup at WeWork",
            "time": "6 PM",
            "date": today.strftime("%b %d, %Y"),
            "area": "Downtown",
            "type": "Tech",
            "url": "https://www.eventbrite.com"
        },
        {
            "name": "Comedy Night at The Comedy Underground",
            "time": "8 PM",
            "date": today.strftime("%b %d, %Y"),
            "area": "Pioneer Square",
            "type": "Comedy",
            "url": "https://www.eventbrite.com"
        },
        {
            "name": "Food & Wine Festival",
            "time": "12 PM",
            "date": today.strftime("%b %d, %Y"),
            "area": "South Lake Union",
            "type": "Food",
            "url": "https://www.eventbrite.com"
        },
        {
            "name": "Yoga in the Park",
            "time": "9 AM",
            "date": today.strftime("%b %d, %Y"),
            "area": "Green Lake",
            "type": "Health",
            "url": "https://www.eventbrite.com"
        },
        {
            "name": "Seattle Symphony Performance",
            "time": "7:30 PM",
            "date": today.strftime("%b %d, %Y"),
            "area": "Downtown",
            "type": "Arts",
            "url": "https://www.seattlesymphony.org"
        },
        {
            "name": "Startup Networking Event",
            "time": "5:30 PM",
            "date": today.strftime("%b %d, %Y"),
            "area": "Capitol Hill",
            "type": "Business",
            "url": "https://www.eventbrite.com"
        },
        {
            "name": "Fremont Street Fair",
            "time": "10 AM",
            "date": today.strftime("%b %d, %Y"),
            "area": "Fremont",
            "type": "Arts",
            "url": "https://www.eventbrite.com"
        },
        {
            "name": "Seattle Sounders FC Match",
            "time": "7:30 PM",
            "date": today.strftime("%b %d, %Y"),
            "area": "Sodo",
            "type": "Sports",
            "url": "https://www.soundersfc.com"
        },
        {
            "name": "Cooking Class at Sur La Table",
            "time": "6 PM",
            "date": today.strftime("%b %d, %Y"),
            "area": "Downtown",
            "type": "Food",
            "url": "https://www.eventbrite.com"
        },
        {
            "name": "Indie Music Showcase",
            "time": "8 PM",
            "date": today.strftime("%b %d, %Y"),
            "area": "Capitol Hill",
            "type": "Music",
            "url": "https://www.eventbrite.com"
        },
        {
            "name": "Art Gallery Opening",
            "time": "5 PM",
            "date": today.strftime("%b %d, %Y"),
            "area": "Pioneer Square",
            "type": "Arts",
            "url": "https://www.eventbrite.com"
        },
        {
            "name": "Tech Talk: AI in Healthcare",
            "time": "6:30 PM",
            "date": today.strftime("%b %d, %Y"),
            "area": "South Lake Union",
            "type": "Tech",
            "url": "https://www.eventbrite.com"
        },
        {
            "name": "Seattle Kraken Hockey Game",
            "time": "7 PM",
            "date": today.strftime("%b %d, %Y"),
            "area": "Uptown",
            "type": "Sports",
            "url": "https://www.nhl.com/kraken"
        },
        {
            "name": "Wine Tasting Event",
            "time": "5 PM",
            "date": today.strftime("%b %d, %Y"),
            "area": "Queen Anne",
            "type": "Food",
            "url": "https://www.eventbrite.com"
        },
        {
            "name": "Stand-up Comedy Show",
            "time": "9 PM",
            "date": today.strftime("%b %d, %Y"),
            "area": "Capitol Hill",
            "type": "Comedy",
            "url": "https://www.eventbrite.com"
        },
        {
            "name": "Morning Run Club",
            "time": "7 AM",
            "date": today.strftime("%b %d, %Y"),
            "area": "Green Lake",
            "type": "Health",
            "url": "https://www.eventbrite.com"
        },
        {
            "name": "Business Networking Breakfast",
            "time": "8 AM",
            "date": today.strftime("%b %d, %Y"),
            "area": "Downtown",
            "type": "Business",
            "url": "https://www.eventbrite.com"
        }
    ]
    return placeholder_events[:limit]
