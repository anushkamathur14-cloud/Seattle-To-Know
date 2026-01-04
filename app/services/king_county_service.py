import os
import requests
from datetime import datetime
from typing import List, Optional

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

def get_king_county_updates() -> List[str]:
    """
    Fetch King County updates including transit alerts, news, and advisories.
    Returns a list of update messages.
    Filters out office closure alerts and keeps only relevant transportation/delay information.
    """
    updates = []
    
    try:
        # Try to fetch King County Metro service alerts
        # Note: King County Metro doesn't have a public REST API, so we'll use their alerts page
        metro_updates = _get_metro_alerts()
        updates.extend(metro_updates)
        
        # Try to fetch King County news/alerts
        county_news = _get_county_news()
        updates.extend(county_news)
        
    except Exception as e:
        print(f"Error fetching King County updates: {e}")
        # Return default advice if API fails
        updates.append("Check Metro service advisories if commuting")
    
    # Filter out office closure alerts and keep only relevant transportation info
    updates = _filter_relevant_updates(updates)
    
    # Always include default if no updates found
    if not updates:
        updates.append("Check Metro service advisories if commuting")
    
    return updates


def _filter_relevant_updates(updates: List[str]) -> List[str]:
    """
    Filter to keep only live traffic updates. Excludes Metro alerts, office closures, and generic notices.
    """
    if not updates:
        return updates
    
    filtered = []
    
    # Keywords that indicate Metro/transit alerts (to exclude)
    metro_keywords = [
        'metro',
        'metro alert',
        'transit',
        'bus',
        'light rail',
        'link',
        'ferry',
        'service change',
        'service changes',
        'route',
        'routes',
        'schedule',
        'schedules'
    ]
    
    # Keywords that indicate office closures (to exclude)
    office_closure_keywords = [
        'offices will be closed',
        'offices are closed',
        'office closure',
        'office will be closed',
        'our offices',
        'county offices',
        'government offices',
        'administrative offices',
        'office hours',
        'holiday closure',
        'holiday schedule'
    ]
    
    # Generic holiday schedule phrases (to exclude - too vague)
    generic_schedule_phrases = [
        'schedules may be different',
        'schedule may be different',
        'schedules will be different',
        'schedule will be different',
        'service schedules may be different',
        'transit and service schedules may be different'
    ]
    
    # Holiday names (often in generic office closure notices)
    holiday_names = [
        "new year's day",
        "new years day",
        "christmas",
        "thanksgiving",
        "independence day",
        "memorial day",
        "labor day",
        "presidents day",
        "columbus day",
        "veterans day",
        "martin luther king",
        "mlk day"
    ]
    
    # Keywords that indicate TRAFFIC-specific information (to keep)
    traffic_keywords = [
        'traffic',
        'highway',
        'highways',
        'i-5',
        'i-90',
        'i-405',
        'sr-520',
        'sr-99',
        'bridge',
        'tunnel',
        'lane closure',
        'road closure',
        'ramp closure',
        'express lane',
        'hov',
        'carpool',
        'accident',
        'incident',
        'construction',
        'delay',
        'delays',
        'delayed',
        'detour',
        'detours',
        'closed',
        'closure',
        'closures',
        'backup',
        'congestion',
        'blocked'
    ]
    
    for update in updates:
        update_lower = update.lower()
        
        # Exclude Metro/transit alerts
        is_metro_alert = any(keyword in update_lower for keyword in metro_keywords)
        
        # Check if it's a generic holiday office closure notice
        is_holiday_notice = any(holiday in update_lower for holiday in holiday_names)
        is_office_closure = any(keyword in update_lower for keyword in office_closure_keywords)
        is_generic_schedule = any(phrase in update_lower for phrase in generic_schedule_phrases)
        
        # Check if it contains TRAFFIC-specific keywords
        has_traffic_info = any(keyword in update_lower for keyword in traffic_keywords)
        
        # Exclude Metro alerts
        if is_metro_alert:
            continue
        
        # Exclude generic holiday notices that only mention "schedules may be different"
        if is_holiday_notice and is_office_closure and is_generic_schedule and not has_traffic_info:
            continue
        
        # Exclude pure office closures without traffic info
        if is_office_closure and not has_traffic_info:
            continue
        
        # Keep only if it has specific traffic information
        if has_traffic_info:
            filtered.append(update)
    
    return filtered


def _get_metro_alerts() -> List[str]:
    """
    Fetch King County Metro transit alerts.
    Scrapes the Metro alerts page for service advisories.
    """
    alerts = []
    
    if not HAS_BS4:
        return alerts
    
    try:
        # King County Metro service alerts page
        url = "https://kingcounty.gov/depts/transportation/metro/alerts-updates/service-advisories.aspx"
        
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for alert/advisory content
        # This is a simplified parser - adjust based on actual page structure
        alert_elements = soup.find_all(['div', 'article', 'li'], class_=lambda x: x and (
            'alert' in x.lower() or 
            'advisory' in x.lower() or 
            'service' in x.lower()
        ))
        
        for element in alert_elements[:3]:  # Limit to 3 most recent
            text = element.get_text(strip=True)
            if text and len(text) > 20 and len(text) < 200:
                alerts.append(f"Metro Alert: {text}")
        
        # Alternative: Check for any recent updates in the page
        if not alerts:
            # Look for date-based content indicating recent updates
            page_text = soup.get_text()
            if any(keyword in page_text.lower() for keyword in ['delay', 'detour', 'closure', 'service change']):
                alerts.append("Metro service changes may be in effect - check routes before traveling")
        
    except Exception as e:
        print(f"Error fetching Metro alerts: {e}")
    
    return alerts


def _get_county_news() -> List[str]:
    """
    Fetch King County news and announcements.
    """
    news_items = []
    
    if not HAS_BS4:
        return news_items
    
    try:
        # King County news page
        url = "https://kingcounty.gov/About/news.aspx"
        
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for recent news items
        news_elements = soup.find_all(['article', 'div', 'li'], class_=lambda x: x and (
            'news' in x.lower() or 
            'announcement' in x.lower() or
            'update' in x.lower()
        ))
        
        for element in news_elements[:2]:  # Limit to 2 most recent
            text = element.get_text(strip=True)
            if text and len(text) > 30 and len(text) < 150:
                # Truncate if too long
                if len(text) > 120:
                    text = text[:120] + "..."
                news_items.append(f"King County: {text}")
        
    except Exception as e:
        print(f"Error fetching County news: {e}")
    
    return news_items


def get_transit_advisory() -> str:
    """
    Get a general transit advisory message.
    This is a fallback when we can't fetch live data.
    """
    return "Check Metro service advisories if commuting"

