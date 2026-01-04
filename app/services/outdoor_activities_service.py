from typing import List, Dict

def get_seattle_outdoor_activities() -> List[Dict]:
    """
    Get Seattle outdoor activities with rules and tutorial links.
    
    Returns:
        List of outdoor activities with name, type, location, and rules/tutorial links
    """
    activities = [
        {
            "name": "Green Lake Pickleball Courts",
            "type": "Pickleball",
            "location": "Green Lake",
            "address": "7201 E Green Lake Dr N, Seattle, WA 98115",
            "rules_link": "https://usapickleball.org/what-is-pickleball/official-rules/",
            "tutorial_link": "https://www.youtube.com/results?search_query=pickleball+tutorial+for+beginners",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Green+Lake+Pickleball+Seattle"
        },
        {
            "name": "Lower Woodland Tennis Courts",
            "type": "Tennis",
            "location": "Green Lake",
            "address": "5900 W Green Lake Way N, Seattle, WA 98103",
            "rules_link": "https://www.usta.com/en/home/play/tennis-rules.html",
            "tutorial_link": "https://www.youtube.com/results?search_query=tennis+tutorial+for+beginners",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Lower+Woodland+Tennis+Seattle"
        },
        {
            "name": "Cal Anderson Park Pickleball",
            "type": "Pickleball",
            "location": "Capitol Hill",
            "address": "1635 11th Ave, Seattle, WA 98122",
            "rules_link": "https://usapickleball.org/what-is-pickleball/official-rules/",
            "tutorial_link": "https://www.youtube.com/results?search_query=pickleball+tutorial+for+beginners",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Cal+Anderson+Park+Pickleball+Seattle"
        },
        {
            "name": "Discovery Park Trails",
            "type": "Hiking",
            "location": "Magnolia",
            "address": "3801 Discovery Park Blvd, Seattle, WA 98199",
            "rules_link": "https://www.nps.gov/articles/hiking-safety.htm",
            "tutorial_link": "https://www.youtube.com/results?search_query=hiking+for+beginners+tips",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Discovery+Park+Seattle"
        },
        {
            "name": "Alki Beach Volleyball",
            "type": "Volleyball",
            "location": "West Seattle",
            "address": "1702 Alki Ave SW, Seattle, WA 98116",
            "rules_link": "https://www.volleyball.org/rules.html",
            "tutorial_link": "https://www.youtube.com/results?search_query=volleyball+tutorial+for+beginners",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Alki+Beach+Volleyball+Seattle"
        },
        {
            "name": "Seward Park Tennis Courts",
            "type": "Tennis",
            "location": "Seward Park",
            "address": "5900 Lake Washington Blvd S, Seattle, WA 98118",
            "rules_link": "https://www.usta.com/en/home/play/tennis-rules.html",
            "tutorial_link": "https://www.youtube.com/results?search_query=tennis+tutorial+for+beginners",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Seward+Park+Tennis+Seattle"
        },
        {
            "name": "Gas Works Park",
            "type": "Outdoor Recreation",
            "location": "Wallingford",
            "address": "2101 N Northlake Way, Seattle, WA 98103",
            "rules_link": "https://www.seattle.gov/parks/about-us/park-rules",
            "tutorial_link": None,
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Gas+Works+Park+Seattle"
        },
        {
            "name": "Myrtle Edwards Park",
            "type": "Running/Walking",
            "location": "Downtown",
            "address": "3130 Alaskan Way, Seattle, WA 98121",
            "rules_link": "https://www.runnersworld.com/training/a20855465/running-etiquette-rules/",
            "tutorial_link": "https://www.youtube.com/results?search_query=running+for+beginners+tutorial",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Myrtle+Edwards+Park+Seattle"
        },
        {
            "name": "Volunteer Park Tennis Courts",
            "type": "Tennis",
            "location": "Capitol Hill",
            "address": "1247 15th Ave E, Seattle, WA 98112",
            "rules_link": "https://www.usta.com/en/home/play/tennis-rules.html",
            "tutorial_link": "https://www.youtube.com/results?search_query=tennis+tutorial+for+beginners",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Volunteer+Park+Tennis+Seattle"
        },
        {
            "name": "Golden Gardens Park",
            "type": "Beach/Outdoor",
            "location": "Ballard",
            "address": "8498 Seaview Pl NW, Seattle, WA 98117",
            "rules_link": "https://www.seattle.gov/parks/about-us/park-rules",
            "tutorial_link": None,
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Golden+Gardens+Park+Seattle"
        },
        {
            "name": "Magnuson Park Pickleball",
            "type": "Pickleball",
            "location": "Sand Point",
            "address": "7400 Sand Point Way NE, Seattle, WA 98115",
            "rules_link": "https://usapickleball.org/what-is-pickleball/official-rules/",
            "tutorial_link": "https://www.youtube.com/results?search_query=pickleball+tutorial+for+beginners",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Magnuson+Park+Pickleball+Seattle"
        },
        {
            "name": "Ravenna Park Trails",
            "type": "Hiking/Walking",
            "location": "Ravenna",
            "address": "5520 Ravenna Ave NE, Seattle, WA 98105",
            "rules_link": "https://www.nps.gov/articles/hiking-safety.htm",
            "tutorial_link": "https://www.youtube.com/results?search_query=hiking+for+beginners+tips",
            "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Ravenna+Park+Seattle"
        }
    ]
    
    return activities


def get_activity_types() -> List[str]:
    """Get list of available activity types."""
    return [
        "Pickleball",
        "Tennis",
        "Hiking",
        "Volleyball",
        "Running/Walking",
        "Outdoor Recreation",
        "Beach/Outdoor"
    ]

