# Deploying to Lovable

This guide will help you deploy your Seattle To Know application to Lovable.

## Prerequisites

1. **Lovable Account**: Sign up at [Lovable](https://lovable.dev) if you haven't already
2. **API Keys**: Make sure you have all required API keys (see README.md)

## Deployment Steps

### 1. Prepare Your Project

Your project structure is already set up correctly:
- ✅ `requirements.txt` with all dependencies
- ✅ FastAPI application in `app/main.py`
- ✅ Static files in `static/` directory
- ✅ API routes properly configured

### 2. Set Environment Variables in Lovable

In your Lovable project settings, add these environment variables:

**Required:**
- `OPENWEATHER_API_KEY` - Your OpenWeatherMap API key
- `EVENTBRITE_API_KEY` - Your Eventbrite API key
- `GOOGLE_PLACES_API_KEY` - Your Google Places API key

**Optional (for additional event sources):**
- `TICKETMASTER_API_KEY` - Ticketmaster API key
- `SEATGEEK_CLIENT_ID` - SeatGeek Client ID
- `SEATGEEK_CLIENT_SECRET` - SeatGeek Client Secret

### 3. Deploy to Lovable

1. **Connect your repository** to Lovable (if using Git)
   - Or upload your project files directly

2. **Configure the build**:
   - **Runtime**: Python 3.9+
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Build Command**: `pip install -r requirements.txt`

3. **Set the root path**:
   - Make sure Lovable knows to serve from the root (`/`)
   - The FastAPI app already handles this with the `@app.get("/")` route

### 4. Verify Deployment

Once deployed, test these endpoints:
- `https://your-app.lovable.dev/` - Main application
- `https://your-app.lovable.dev/api/overview` - API overview
- `https://your-app.lovable.dev/api/food` - Food API
- `https://your-app.lovable.dev/api/events` - Events API
- `https://your-app.lovable.dev/api/outdoor` - Outdoor activities API

## Important Notes

### CORS Configuration
The app currently allows all origins (`allow_origins=["*"]`). For production, you may want to restrict this to your Lovable domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-app.lovable.dev"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Static Files
The app serves static files from the `static/` directory. Make sure this directory is included in your deployment.

### Port Configuration
Lovable typically provides a `$PORT` environment variable. The start command above uses this. If Lovable uses a different variable, adjust accordingly.

## Troubleshooting

### API Keys Not Working
- Verify all environment variables are set correctly in Lovable
- Check that API keys are active and have proper permissions
- Review API quotas/limits

### Static Files Not Loading
- Ensure `static/` directory is included in deployment
- Check file paths are correct
- Verify static file serving is enabled

### CORS Errors
- Update CORS settings to include your Lovable domain
- Check browser console for specific error messages

## Support

If you encounter issues:
1. Check Lovable deployment logs
2. Verify all environment variables are set
3. Test API endpoints individually
4. Review the README.md for local setup verification

