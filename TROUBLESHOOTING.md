# Browser Troubleshooting Guide

## Quick Fixes

### 1. **Server Not Starting?**

**Check if server is running:**
```bash
cd "/Users/anushkamathur/Desktop/Seattle to know"
uvicorn app.main:app --reload
```

**Common errors:**
- **"Module not found"**: Run `pip3 install -r requirements.txt`
- **"Port 8000 already in use"**: Use different port: `uvicorn app.main:app --reload --port 8001`
- **"Address already in use"**: Kill the process using port 8000

### 2. **Browser Shows Error Page?**

**Check:**
- Are you using the correct URL? `http://localhost:8000` (not `https://`)
- Is the server actually running? (Check terminal)
- Try refreshing the page (Ctrl/Cmd + R)
- Clear browser cache

### 3. **Blank Page or Nothing Loads?**

**Check browser console:**
- Press `F12` to open Developer Tools
- Go to "Console" tab
- Look for red error messages
- Share the error message

**Check Network tab:**
- Press `F12` → "Network" tab
- Refresh page
- Look for failed requests (red)
- Check what errors appear

### 4. **API Errors?**

**Test API directly:**
```bash
# Test overview endpoint
curl http://localhost:8000/api/overview

# Test events endpoint
curl http://localhost:8000/api/events
```

**Check server logs:**
- Look at terminal where server is running
- Check for Python errors or exceptions

### 5. **Static Files Not Loading?**

**Check:**
- Is `static/index.html` file present?
- Check server logs for 404 errors
- Verify file paths are correct

---

## Step-by-Step Debugging

### Step 1: Start Server

```bash
cd "/Users/anushkamathur/Desktop/Seattle to know"
uvicorn app.main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Step 2: Open Browser

Go to: `http://localhost:8000`

### Step 3: Check for Errors

**In Browser:**
1. Press `F12` (Developer Tools)
2. Check **Console** tab for JavaScript errors
3. Check **Network** tab for failed requests

**In Terminal:**
- Look for Python errors
- Check for import errors
- Look for API errors

---

## Common Issues & Solutions

### Issue: "Cannot GET /"

**Solution:**
- Check that `static/index.html` exists
- Verify `app/main.py` has the root route configured
- Restart server

### Issue: "CORS error"

**Solution:**
- Check CORS settings in `app/main.py`
- For local development, `allow_origins=["*"]` should work

### Issue: "API endpoint returns 500"

**Solution:**
- Check server logs for Python errors
- Verify environment variables are set (if needed)
- Check API keys are valid

### Issue: "Page loads but shows errors"

**Solution:**
- Open browser console (F12)
- Check JavaScript errors
- Verify API endpoints are working
- Check network requests

### Issue: "Port already in use"

**Solution:**
```bash
# Find process using port 8000
lsof -ti:8000

# Kill it
kill -9 $(lsof -ti:8000)

# Or use different port
uvicorn app.main:app --reload --port 8001
```

---

## Quick Test Commands

### Test if server starts:
```bash
uvicorn app.main:app --reload
```

### Test API endpoints:
```bash
# Overview
curl http://localhost:8000/api/overview

# Events
curl http://localhost:8000/api/events

# Food
curl http://localhost:8000/api/food

# Outdoor
curl http://localhost:8000/api/outdoor
```

### Test if dependencies are installed:
```bash
python3 -c "import fastapi, uvicorn, requests; print('All dependencies OK')"
```

---

## Still Not Working?

**Please share:**
1. **Error message** from browser console (F12 → Console)
2. **Error message** from terminal (where server is running)
3. **What happens** when you visit `http://localhost:8000`
4. **Screenshot** if possible

This will help diagnose the exact issue!

