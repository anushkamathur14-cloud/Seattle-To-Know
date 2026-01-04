# How the App Works Without API Keys

## 🔍 What's Happening

If you see "Eventbrite key isn't set" but still see events, you're seeing **placeholder/demo data**, not real events from Eventbrite.

---

## 📊 How the Fallback System Works

### Step 1: Try Real APIs

The app tries to fetch from multiple sources:

1. **Eventbrite API** → Returns `[]` if no API key
2. **Ticketmaster API** → Tries if `TICKETMASTER_API_KEY` is set
3. **SeatGeek API** → Tries if `SEATGEEK_CLIENT_ID` and `SEATGEEK_CLIENT_SECRET` are set

### Step 2: Fallback to Placeholders

If **no real events** are found from any API, the app uses **placeholder events**:

```python
# From events_service.py, line 69-74
if not unique_events:
    placeholder_events = _get_placeholder_events(limit * 2)
    if event_type:
        placeholder_events = _filter_events_by_type(placeholder_events, event_type)
    return placeholder_events[:limit]
```

### Step 3: Return Placeholder Data

The `_get_placeholder_events()` function returns **hardcoded demo events** like:
- "Capitol Hill Art Walk"
- "Live Jazz at Pike Place"
- "Seattle Mariners Game"
- etc.

These are **not real events** - they're just examples to show the app works.

---

## 🎯 Current Status

**What you're seeing:**
- ✅ App is working (showing placeholder events)
- ⚠️ Not pulling real data from Eventbrite
- ✅ Placeholder events are filtered by type/date just like real events

**To get real events:**
1. Set `EVENTBRITE_API_KEY` in your environment variables
2. Or set `TICKETMASTER_API_KEY` for Ticketmaster events
3. Or set `SEATGEEK_CLIENT_ID` and `SEATGEEK_CLIENT_SECRET` for SeatGeek events

---

## 🔧 How to Get Real Events

### Option 1: Set Eventbrite API Key

**Locally:**
```bash
# In .env file
EVENTBRITE_API_KEY=your_actual_key_here
```

**On Render:**
1. Go to Render Dashboard
2. Your Web Service → Environment tab
3. Add `EVENTBRITE_API_KEY` with your actual key

### Option 2: Use Other Event Sources

The app will try these if Eventbrite isn't available:

**Ticketmaster:**
```bash
TICKETMASTER_API_KEY=your_ticketmaster_key
```

**SeatGeek:**
```bash
SEATGEEK_CLIENT_ID=your_client_id
SEATGEEK_CLIENT_SECRET=your_client_secret
```

---

## 📋 How to Tell If You're Seeing Real vs Placeholder Data

### Real Events (from API):
- ✅ Events have actual dates/times
- ✅ Events match your filters accurately
- ✅ Events update based on real availability
- ✅ Event URLs go to actual event pages

### Placeholder Events (fallback):
- ⚠️ Same events every time
- ⚠️ Generic Seattle events
- ⚠️ Event URLs go to generic Eventbrite homepage
- ⚠️ Don't change based on real availability

---

## 🧪 Test If API Key Is Working

### Check in Code:

Add this to test if API key is being read:

```python
import os
print("Eventbrite Key:", "SET" if os.getenv("EVENTBRITE_API_KEY") else "NOT SET")
```

### Check API Response:

If API key is working, you'll see:
- Different events each time
- Events that match current dates
- Real event details and URLs

---

## 💡 Why This Design?

The fallback system ensures:
1. **App always works** - Even without API keys, you can see the UI
2. **Easy testing** - Developers can test without setting up API keys
3. **Graceful degradation** - App doesn't crash if APIs are down
4. **Multiple sources** - Tries multiple APIs before falling back

---

## 🎯 Summary

**Current situation:**
- App is showing **placeholder/demo events**
- These are **hardcoded examples**, not real data
- App works fine, but you need API keys for real events

**To get real events:**
1. Get Eventbrite API key from [eventbrite.com/platform/api](https://www.eventbrite.com/platform/api/)
2. Set it in your environment variables (local `.env` or Render dashboard)
3. Restart/redeploy the app
4. You'll now see real events from Eventbrite!

---

## 🔄 Same Pattern for Other Services

This fallback pattern is used for:

- **Events**: Placeholder events if no API keys
- **Food**: Placeholder restaurants if `GOOGLE_PLACES_API_KEY` not set
- **Weather**: Will error if `OPENWEATHER_API_KEY` not set (no fallback)
- **Air Quality**: Will use default values if `OPENWEATHER_API_KEY` not set

---

## ✅ Next Steps

1. **Get Eventbrite API Key**: [eventbrite.com/platform/api](https://www.eventbrite.com/platform/api/)
2. **Set it locally** (for testing): Add to `.env` file
3. **Set it on Render** (for deployment): Add to Environment Variables
4. **Restart app** to load the new key
5. **Verify**: You should now see real events!

