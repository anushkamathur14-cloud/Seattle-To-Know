# Deploying to Render - Complete Guide

## ⚠️ Important: Environment Variables in Render

**DO NOT commit `.env` files to Git!** Instead, set environment variables in Render's dashboard.

---

## Step-by-Step: Deploy to Render

### Step 1: Push Your Code to GitHub

Make sure your code is on GitHub:

```bash
cd "/Users/anushkamathur/Desktop/Seattle to know"
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### Step 2: Create Render Account & Service

1. **Sign up** at [render.com](https://render.com)
2. **Click "New +"** → **"Web Service"**
3. **Connect GitHub**:
   - Click "Connect GitHub" (if not already connected)
   - Authorize Render to access your repositories
   - Select your repository: `YOUR_USERNAME/seattle-to-know`

### Step 3: Configure Build Settings

Fill in these settings:

- **Name**: `seattle-to-know` (or your choice)
- **Environment**: **Python 3**
- **Region**: Choose closest to you (e.g., Oregon)
- **Branch**: `main` (or your default branch)
- **Root Directory**: Leave empty (or `/` if needed)
- **Runtime**: `Python 3`
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

### Step 4: Set Environment Variables in Render Dashboard ⭐

**This is where you set your API keys!**

1. **Scroll down** to **"Environment Variables"** section
2. **Click "Add Environment Variable"** for each key:

#### Required Environment Variables:

Click "Add Environment Variable" and add these one by one:

| Variable Name | Value | Description |
|--------------|-------|-------------|
| `OPENWEATHER_API_KEY` | `your_openweather_key` | OpenWeatherMap API key |
| `EVENTBRITE_API_KEY` | `your_eventbrite_key` | Eventbrite API key |
| `GOOGLE_PLACES_API_KEY` | `your_google_places_key` | Google Places API key |

#### Optional Environment Variables:

| Variable Name | Value | Description |
|--------------|-------|-------------|
| `TICKETMASTER_API_KEY` | `your_ticketmaster_key` | Ticketmaster API key (optional) |
| `SEATGEEK_CLIENT_ID` | `your_seatgeek_client_id` | SeatGeek Client ID (optional) |
| `SEATGEEK_CLIENT_SECRET` | `your_seatgeek_client_secret` | SeatGeek Client Secret (optional) |

#### Optional: CORS Configuration

If you want to restrict CORS to specific domains:

| Variable Name | Value | Description |
|--------------|-------|-------------|
| `ALLOWED_ORIGINS` | `https://your-frontend.com` | Comma-separated list of allowed origins |

**Example:**
```
ALLOWED_ORIGINS=https://your-app.onrender.com,https://yourdomain.com
```

### Step 5: Deploy

1. **Click "Create Web Service"** at the bottom
2. **Render will:**
   - Clone your repository
   - Install dependencies (`pip install -r requirements.txt`)
   - Start your application
   - Provide a live URL

3. **Wait for deployment** (usually 2-5 minutes)
4. **Check build logs** if there are any issues

### Step 6: Get Your Live URL

Once deployed, Render provides a URL like:
```
https://seattle-to-know.onrender.com
```

Or if you set a custom name:
```
https://your-app-name.onrender.com
```

---

## 📍 Where to Set Environment Variables in Render

### Method 1: During Service Creation

1. When creating the web service
2. Scroll to **"Environment Variables"** section
3. Click **"Add Environment Variable"**
4. Enter variable name and value
5. Click **"Add"**

### Method 2: After Service Creation

1. Go to your **Render Dashboard**
2. Click on your **Web Service**
3. Go to **"Environment"** tab (left sidebar)
4. Click **"Add Environment Variable"**
5. Enter name and value
6. Click **"Save Changes"**
7. **Redeploy** if needed (Render may auto-redeploy)

### Method 3: Using Render CLI (Advanced)

```bash
# Install Render CLI
npm install -g render-cli

# Set environment variable
render env:set OPENWEATHER_API_KEY=your_key
```

---

## 🔒 Security Best Practices

### ✅ DO:
- ✅ Set environment variables in Render dashboard
- ✅ Use Render's secure environment variable storage
- ✅ Keep `.env` files in `.gitignore` (already done)
- ✅ Use different keys for development and production

### ❌ DON'T:
- ❌ Commit `.env` files to Git
- ❌ Hardcode API keys in your code
- ❌ Share API keys in screenshots or documentation
- ❌ Use production keys in local development

---

## 🔄 Updating Environment Variables

### To Update Existing Variables:

1. Go to **Render Dashboard**
2. Select your **Web Service**
3. Go to **"Environment"** tab
4. Find the variable you want to update
5. Click **"Edit"** (pencil icon)
6. Update the value
7. Click **"Save Changes"**
8. Render will automatically redeploy

### To Add New Variables:

1. Go to **"Environment"** tab
2. Click **"Add Environment Variable"**
3. Enter name and value
4. Click **"Add"**
5. Service will redeploy automatically

---

## 🧪 Testing Your Deployment

Once deployed, test these URLs:

1. **Main Application:**
   ```
   https://your-app.onrender.com/
   ```

2. **API Overview:**
   ```
   https://your-app.onrender.com/api/overview
   ```

3. **API Documentation:**
   ```
   https://your-app.onrender.com/docs
   ```

4. **Food API:**
   ```
   https://your-app.onrender.com/api/food
   ```

5. **Events API:**
   ```
   https://your-app.onrender.com/api/events
   ```

---

## 🐛 Troubleshooting

### "API key not found" errors

**Solution:**
1. Go to Render Dashboard → Your Service → Environment tab
2. Verify all environment variables are set correctly
3. Check variable names are exact (case-sensitive):
   - `OPENWEATHER_API_KEY` (not `openweather_api_key`)
   - `EVENTBRITE_API_KEY` (not `eventbrite_api_key`)
4. Redeploy the service

### Build fails

**Solution:**
1. Check build logs in Render dashboard
2. Verify `requirements.txt` is correct
3. Ensure Python version is 3.9+
4. Check for any missing dependencies

### Service won't start

**Solution:**
1. Verify start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
2. Check that `app/main.py` exists
3. Review deployment logs for errors
4. Ensure all environment variables are set

### CORS errors

**Solution:**
1. Set `ALLOWED_ORIGINS` environment variable in Render
2. Include your frontend domain(s)
3. Redeploy after updating

---

## 📋 Environment Variables Checklist

Before deploying, make sure you have:

- [ ] `OPENWEATHER_API_KEY` - Required
- [ ] `EVENTBRITE_API_KEY` - Required
- [ ] `GOOGLE_PLACES_API_KEY` - Required
- [ ] `TICKETMASTER_API_KEY` - Optional
- [ ] `SEATGEEK_CLIENT_ID` - Optional
- [ ] `SEATGEEK_CLIENT_SECRET` - Optional
- [ ] `ALLOWED_ORIGINS` - Optional (for CORS)

---

## 🔄 Auto-Deploy on Git Push

Render automatically deploys when you push to your connected branch:

1. **Make changes** in your code
2. **Commit and push** to GitHub:
   ```bash
   git add .
   git commit -m "Update code"
   git push origin main
   ```
3. **Render detects the push**
4. **Automatically rebuilds and redeploys**
5. **Your changes go live** in a few minutes

---

## 💡 Pro Tips

1. **Free Tier Note**: Render's free tier spins down after 15 minutes of inactivity. First request after spin-down takes ~30 seconds.

2. **Upgrade for Production**: For production apps, consider Render's paid plans for:
   - No spin-down
   - Better performance
   - More resources

3. **Monitor Logs**: Check Render dashboard logs to debug issues

4. **Environment Variables**: You can have different values for different environments (staging, production)

---

## 📝 Summary

**Where to set environment variables in Render:**
1. **Render Dashboard** → Your Web Service → **"Environment"** tab
2. Click **"Add Environment Variable"**
3. Enter name and value
4. Save and redeploy

**Never commit `.env` files to Git!** Always use Render's environment variables dashboard.

---

## Need Help?

- Check Render documentation: [render.com/docs](https://render.com/docs)
- Review your deployment logs
- Verify all environment variables are set
- Test API endpoints individually

