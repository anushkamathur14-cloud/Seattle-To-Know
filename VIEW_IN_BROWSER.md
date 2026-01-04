# How to View Your App in Browser

## Quick Start

### Step 1: Start the Server

Open your terminal in Cursor (`` Ctrl + ` ``) or use your system terminal, then run:

```bash
cd "/Users/anushkamathur/Desktop/Seattle to know"
uvicorn app.main:app --reload
```

You should see output like:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 2: Open in Browser

Once the server is running, open your browser and go to:

**Main Application:**
```
http://localhost:8000
```
or
```
http://127.0.0.1:8000
```

**API Documentation (Interactive):**
```
http://localhost:8000/docs
```

**Alternative API Docs:**
```
http://localhost:8000/redoc
```

### Step 3: Test the Application

1. **Main Page**: You'll see your Seattle To Know application
2. **API Endpoints**: Test these URLs:
   - `http://localhost:8000/api/overview` - Overview data
   - `http://localhost:8000/api/food` - Food joints
   - `http://localhost:8000/api/events` - Events
   - `http://localhost:8000/api/outdoor` - Outdoor activities

---

## Using Cursor's Terminal

### Option 1: Integrated Terminal
1. Press `` Ctrl + ` `` (backtick) to open terminal
2. Run: `uvicorn app.main:app --reload`
3. Click the URL in the terminal output, or manually open `http://localhost:8000`

### Option 2: External Terminal
1. Open Terminal app (macOS)
2. Navigate to project: `cd "/Users/anushkamathur/Desktop/Seattle to know"`
3. Run: `uvicorn app.main:app --reload`
4. Open browser to `http://localhost:8000`

---

## Important Notes

### Before Starting Server

Make sure you have environment variables set (or the app will use fallback data):

```bash
# Set API keys (optional for testing, app has fallbacks)
export OPENWEATHER_API_KEY="your_key"
export EVENTBRITE_API_KEY="your_key"
export GOOGLE_PLACES_API_KEY="your_key"
```

Or create a `.env` file in the project root (but don't commit it!):
```
OPENWEATHER_API_KEY=your_key
EVENTBRITE_API_KEY=your_key
GOOGLE_PLACES_API_KEY=your_key
```

### If Dependencies Are Missing

If you get errors about missing packages:

```bash
pip3 install -r requirements.txt
```

### Stop the Server

Press `Ctrl + C` in the terminal to stop the server.

---

## Troubleshooting

### "Port 8000 already in use"
**Solution**: Use a different port:
```bash
uvicorn app.main:app --reload --port 8001
```
Then open: `http://localhost:8001`

### "Module not found" errors
**Solution**: Install dependencies:
```bash
pip3 install -r requirements.txt
```

### "API key not set" warnings
**Solution**: The app will work with fallback data, but set environment variables for real data:
```bash
export OPENWEATHER_API_KEY="your_key"
```

### Browser shows "Cannot connect"
**Solution**: 
- Make sure server is running (check terminal)
- Verify you're using `http://localhost:8000` (not `https://`)
- Check if firewall is blocking the connection

---

## Quick Reference

| URL | What It Shows |
|-----|---------------|
| `http://localhost:8000` | Main application (your frontend) |
| `http://localhost:8000/docs` | Interactive API documentation |
| `http://localhost:8000/redoc` | Alternative API docs |
| `http://localhost:8000/api/overview` | JSON: Overview data |
| `http://localhost:8000/api/food` | JSON: Food joints |
| `http://localhost:8000/api/events` | JSON: Events |
| `http://localhost:8000/api/outdoor` | JSON: Outdoor activities |

---

## Pro Tips

1. **Auto-reload**: The `--reload` flag automatically restarts the server when you change code
2. **API Testing**: Use `/docs` to test API endpoints interactively
3. **Browser DevTools**: Press `F12` to see console logs and network requests
4. **Multiple Tabs**: You can have multiple browser tabs open to test different endpoints

