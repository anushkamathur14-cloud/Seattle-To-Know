# Linking GitHub Repository to Lovable

This guide will help you connect your GitHub repository to Lovable and configure your API keys.

## Step 1: Connect Local Project to GitHub

### 1.1 Initialize Git (if not already done)

```bash
cd "/Users/anushkamathur/Desktop/Seattle to know"
git init
```

### 1.2 Add All Files

```bash
git add .
```

### 1.3 Create Initial Commit

```bash
git commit -m "Initial commit: Seattle To Know application"
```

### 1.4 Add GitHub Remote

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your actual GitHub username and repository name:

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

**Example:**
```bash
git remote add origin https://github.com/johndoe/seattle-to-know.git
```

### 1.5 Push to GitHub

```bash
git branch -M main
git push -u origin main
```

**If you get an error about unrelated histories:**
```bash
git pull origin main --allow-unrelated-histories
# Resolve any conflicts if needed
git push -u origin main
```

### 1.6 Verify Connection

```bash
git remote -v
```

You should see your GitHub repository URL.

---

## Step 2: Connect GitHub Repository to Lovable

### 2.1 In Lovable Dashboard

1. **Log in** to your Lovable account at [lovable.dev](https://lovable.dev)

2. **Create a New Project** or select an existing one

3. **Connect GitHub Repository:**
   - Look for "Connect Repository" or "Import from GitHub" option
   - Click "Connect GitHub" or "Import from Git"
   - Authorize Lovable to access your GitHub account (if prompted)
   - Select your repository: `YOUR_USERNAME/seattle-to-know` (or your repo name)

4. **Configure Build Settings:**
   - **Runtime**: Python 3.9 or higher
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `/` (root of repository)

---

## Step 3: Set Up API Keys in Lovable

### 3.1 Access Environment Variables

In your Lovable project dashboard:
1. Go to **Settings** or **Environment Variables**
2. Look for **"Environment Variables"** or **"Secrets"** section

### 3.2 Add Required API Keys

Add these environment variables one by one:

#### Required API Keys:

1. **OpenWeatherMap API Key**
   - **Variable Name**: `OPENWEATHER_API_KEY`
   - **Value**: Your OpenWeatherMap API key
   - **Get it from**: [OpenWeatherMap API](https://openweathermap.org/api)

2. **Eventbrite API Key**
   - **Variable Name**: `EVENTBRITE_API_KEY`
   - **Value**: Your Eventbrite API key
   - **Get it from**: [Eventbrite Developer Portal](https://www.eventbrite.com/platform/api/)

3. **Google Places API Key**
   - **Variable Name**: `GOOGLE_PLACES_API_KEY`
   - **Value**: Your Google Places API key
   - **Get it from**: [Google Cloud Console](https://console.cloud.google.com/)

#### Optional API Keys (for additional event sources):

4. **Ticketmaster API Key** (Optional)
   - **Variable Name**: `TICKETMASTER_API_KEY`
   - **Value**: Your Ticketmaster API key
   - **Get it from**: [Ticketmaster Developer Portal](https://developer.ticketmaster.com/)

5. **SeatGeek Client ID** (Optional)
   - **Variable Name**: `SEATGEEK_CLIENT_ID`
   - **Value**: Your SeatGeek Client ID

6. **SeatGeek Client Secret** (Optional)
   - **Variable Name**: `SEATGEEK_CLIENT_SECRET`
   - **Value**: Your SeatGeek Client Secret
   - **Get both from**: [SeatGeek Developer Portal](https://platform.seatgeek.com/)

### 3.3 Optional: Restrict CORS (Production)

If you want to restrict CORS to your Lovable domain:

- **Variable Name**: `ALLOWED_ORIGINS`
- **Value**: `https://your-app.lovable.dev` (replace with your actual Lovable domain)

---

## Step 4: Deploy Your Application

### 4.1 Trigger Deployment

After connecting the repository and setting environment variables:

1. **Save** all environment variables
2. **Deploy** or **Build** your application
3. Lovable will:
   - Pull code from GitHub
   - Install dependencies (`pip install -r requirements.txt`)
   - Start your FastAPI application

### 4.2 Monitor Deployment

- Check the **Build Logs** for any errors
- Wait for deployment to complete
- You'll get a URL like: `https://your-app.lovable.dev`

---

## Step 5: Verify Deployment

### 5.1 Test Your Application

Once deployed, test these endpoints:

1. **Main Application:**
   ```
   https://your-app.lovable.dev/
   ```

2. **API Overview:**
   ```
   https://your-app.lovable.dev/api/overview
   ```

3. **Food API:**
   ```
   https://your-app.lovable.dev/api/food
   ```

4. **Events API:**
   ```
   https://your-app.lovable.dev/api/events
   ```

5. **Outdoor Activities API:**
   ```
   https://your-app.lovable.dev/api/outdoor
   ```

### 5.2 Check for Errors

- Open browser console (F12) to check for JavaScript errors
- Check Lovable deployment logs for backend errors
- Verify API keys are working (if APIs fail, check environment variables)

---

## Step 6: Future Updates

### 6.1 Push Changes to GitHub

When you make changes to your code:

```bash
git add .
git commit -m "Description of changes"
git push origin main
```

### 6.2 Lovable Auto-Deploy

- Lovable will automatically detect the push
- It will rebuild and redeploy your application
- Your changes will be live in a few minutes

---

## Troubleshooting

### Issue: "API key not found" errors

**Solution:**
- Double-check environment variable names in Lovable (case-sensitive)
- Make sure you saved the environment variables
- Restart/redeploy the application after adding variables

### Issue: Build fails

**Solution:**
- Check build logs in Lovable dashboard
- Verify `requirements.txt` is correct
- Ensure Python version is 3.9+

### Issue: Application won't start

**Solution:**
- Verify start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Check that `app/main.py` exists and is correct
- Review deployment logs for specific errors

### Issue: CORS errors in browser

**Solution:**
- Set `ALLOWED_ORIGINS` environment variable to your Lovable domain
- Or temporarily allow all origins (already configured in code)

---

## Quick Reference: Environment Variables Checklist

- [ ] `OPENWEATHER_API_KEY` - Required
- [ ] `EVENTBRITE_API_KEY` - Required
- [ ] `GOOGLE_PLACES_API_KEY` - Required
- [ ] `TICKETMASTER_API_KEY` - Optional
- [ ] `SEATGEEK_CLIENT_ID` - Optional
- [ ] `SEATGEEK_CLIENT_SECRET` - Optional
- [ ] `ALLOWED_ORIGINS` - Optional (for CORS)

---

## Need Help?

- Check Lovable documentation: [Lovable Docs](https://docs.lovable.dev)
- Review your deployment logs in Lovable dashboard
- Verify all environment variables are set correctly
- Test API endpoints individually

