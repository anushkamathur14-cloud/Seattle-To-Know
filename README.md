# Seattle To Know

Your daily guide to Seattle weather, events, food, and outdoor activities.

## Features

- 🌤️ **Weather & Air Quality**: Real-time weather and air quality data
- 🍕 **Food**: Find restaurants by area, cuisine, and price range using Google Maps
- 🎉 **Events**: Discover events happening today or this week
- 🏃 **Outdoor Activities**: Find pickleball courts, tennis courts, hiking trails, and more

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file or export these environment variables:

```bash
# Required for weather and air quality
export OPENWEATHER_API_KEY="your_openweather_api_key"

# Required for events (primary source)
export EVENTBRITE_API_KEY="your_eventbrite_api_key"

# Optional: Additional event sources (aggregates results from all available APIs)
export TICKETMASTER_API_KEY="your_ticketmaster_api_key"
export SEATGEEK_CLIENT_ID="your_seatgeek_client_id"
export SEATGEEK_CLIENT_SECRET="your_seatgeek_client_secret"

# Required for food (Google Places API)
export GOOGLE_PLACES_API_KEY="your_google_places_api_key"
```

### 3. Get API Keys

#### OpenWeatherMap API
1. Sign up at [OpenWeatherMap](https://openweathermap.org/api)
2. Get your free API key
3. Set as `OPENWEATHER_API_KEY`

#### Eventbrite API (Primary)
1. Sign up at [Eventbrite Developer Portal](https://www.eventbrite.com/platform/api/)
2. Create an application to get your API key
3. Set as `EVENTBRITE_API_KEY`

#### Ticketmaster Discovery API (Optional - Additional Source)
1. Sign up at [Ticketmaster Developer Portal](https://developer.ticketmaster.com/)
2. Create an application to get your API key
3. Set as `TICKETMASTER_API_KEY`
4. Great for concerts, sports, and theater events

#### SeatGeek API (Optional - Additional Source)
1. Sign up at [SeatGeek Developer Portal](https://platform.seatgeek.com/)
2. Create an application to get Client ID and Secret
3. Set as `SEATGEEK_CLIENT_ID` and `SEATGEEK_CLIENT_SECRET`
4. Great for sports and concert events

#### Google Places API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable "Places API" in APIs & Services > Library
4. Create an API key in Credentials
5. Set as `GOOGLE_PLACES_API_KEY`

### 4. Run the Application

```bash
uvicorn app.main:app --reload
```

Then open your browser to:
- **Main App**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Testing the API

### Test Food API with Google Places

Once you've set `GOOGLE_PLACES_API_KEY`, test it:

```bash
# Test food endpoint
curl "http://localhost:8000/api/food?area=Capitol%20Hill&cuisine=Italian&price_range=$$"

# Test with different filters
curl "http://localhost:8000/api/food?cuisine=Japanese&price_range=$"
```

### Verify API is Working

1. **Start the server**: `uvicorn app.main:app --reload`
2. **Open browser**: http://localhost:8000
3. **Click "Food" tab**
4. **Try different filters**:
   - Select an area (e.g., "Capitol Hill")
   - Select a cuisine (e.g., "Italian")
   - Select a price range (e.g., "$$")
5. **Check results**: You should see real restaurants from Google Maps with ratings

## API Endpoints

- `GET /api/overview` - Weather, air quality, and daily advice
- `GET /api/food?area=...&cuisine=...&price_range=...` - Restaurants with filters
- `GET /api/events?event_type=...&time_range=today|week` - Events
- `GET /api/outdoor?activity_type=...` - Outdoor activities

## Notes

- Weather and air quality data is cached for 10 minutes to reduce API calls
- If Google Places API key is not set, the app falls back to placeholder data
- All filters can be combined (area + cuisine + price range)
- **Events are aggregated from multiple sources**: Eventbrite (primary), Ticketmaster, and SeatGeek
  - If multiple API keys are set, events from all sources are combined and deduplicated
  - This provides broader event coverage for Seattle

