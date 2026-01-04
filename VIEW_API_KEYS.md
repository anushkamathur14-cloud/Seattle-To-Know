# Where to Find and View Your API Keys

## ⚠️ Important: Cursor Doesn't Store API Keys

**Cursor is just a code editor** - it doesn't store, display, or manage your API keys. API keys are stored elsewhere.

---

## 📍 Where Your API Keys Are Located

### 1. **Local Development (.env file)**

If you created a `.env` file for local development:

**Location:**
```
/Users/anushkamathur/Desktop/Seattle to know/.env
```

**To view:**
```bash
cd "/Users/anushkamathur/Desktop/Seattle to know"
cat .env
```

**Or in Cursor:**
- Open the `.env` file in Cursor (if it exists)
- ⚠️ **Note**: `.env` files are in `.gitignore`, so they won't be committed to Git

---

### 2. **System Environment Variables**

If you set them in your terminal:

**To view:**
```bash
# View all environment variables
env | grep API_KEY

# View specific keys
echo $OPENWEATHER_API_KEY
echo $EVENTBRITE_API_KEY
echo $GOOGLE_PLACES_API_KEY
```

---

### 3. **Render Dashboard** (For Deployment)

**To view:**
1. Go to [render.com](https://render.com)
2. Log in to your account
3. Click on your **Web Service**
4. Go to **"Environment"** tab
5. You'll see all environment variables listed (values are hidden by default)
6. Click on a variable to view/edit its value

**Note**: Render hides values by default for security. Click "Show" or "Edit" to view.

---

### 4. **Lovable Dashboard** (If Using Lovable)

**To view:**
1. Go to [lovable.dev](https://lovable.dev)
2. Log in to your account
3. Select your project
4. Go to **Settings** → **Environment Variables**
5. View your API keys there

---

### 5. **API Provider Dashboards** (Where You Got Them)

You can always get your API keys from the original providers:

#### OpenWeatherMap
- Go to [openweathermap.org/api](https://openweathermap.org/api)
- Log in → **API keys** section
- View your existing keys or create new ones

#### Eventbrite
- Go to [eventbrite.com/platform/api](https://www.eventbrite.com/platform/api/)
- Log in → **Developer Portal** → **API Keys**
- View your keys

#### Google Places API
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Select your project → **APIs & Services** → **Credentials**
- View your API keys

#### Ticketmaster
- Go to [developer.ticketmaster.com](https://developer.ticketmaster.com/)
- Log in → **My Apps** → View API keys

#### SeatGeek
- Go to [platform.seatgeek.com](https://platform.seatgeek.com/)
- Log in → **Applications** → View Client ID and Secret

---

## 🔍 How to Check If API Keys Are Set

### In Your Code (Local Development)

Your code reads API keys from environment variables. To check if they're set:

**Option 1: Test in Python**
```python
import os
print("OPENWEATHER_API_KEY:", "SET" if os.getenv("OPENWEATHER_API_KEY") else "NOT SET")
print("EVENTBRITE_API_KEY:", "SET" if os.getenv("EVENTBRITE_API_KEY") else "NOT SET")
print("GOOGLE_PLACES_API_KEY:", "SET" if os.getenv("GOOGLE_PLACES_API_KEY") else "NOT SET")
```

**Option 2: Check in Terminal**
```bash
# Check if keys are set
python3 -c "import os; print('OPENWEATHER:', 'SET' if os.getenv('OPENWEATHER_API_KEY') else 'NOT SET')"
python3 -c "import os; print('EVENTBRITE:', 'SET' if os.getenv('EVENTBRITE_API_KEY') else 'NOT SET')"
python3 -c "import os; print('GOOGLE:', 'SET' if os.getenv('GOOGLE_PLACES_API_KEY') else 'NOT SET')"
```

---

## 🛠️ Setting Up API Keys Locally (For Testing)

### Option 1: Create .env File

Create a file named `.env` in your project root:

```bash
cd "/Users/anushkamathur/Desktop/Seattle to know"
nano .env
```

Add your keys:
```
OPENWEATHER_API_KEY=your_openweather_key_here
EVENTBRITE_API_KEY=your_eventbrite_key_here
GOOGLE_PLACES_API_KEY=your_google_places_key_here
```

**Note**: The `.env` file is already in `.gitignore`, so it won't be committed.

### Option 2: Export in Terminal

```bash
export OPENWEATHER_API_KEY="your_key_here"
export EVENTBRITE_API_KEY="your_key_here"
export GOOGLE_PLACES_API_KEY="your_key_here"
```

**Note**: These only last for the current terminal session.

### Option 3: Add to Shell Profile (Permanent)

Add to `~/.zshrc` (since you're on macOS with zsh):

```bash
echo 'export OPENWEATHER_API_KEY="your_key_here"' >> ~/.zshrc
echo 'export EVENTBRITE_API_KEY="your_key_here"' >> ~/.zshrc
echo 'export GOOGLE_PLACES_API_KEY="your_key_here"' >> ~/.zshrc
source ~/.zshrc
```

---

## 🔒 Security Reminders

### ✅ Safe Practices:
- ✅ Store keys in environment variables (not in code)
- ✅ Use `.env` files locally (already in `.gitignore`)
- ✅ Set keys in deployment platform dashboards (Render, Lovable)
- ✅ Use different keys for development and production

### ❌ Never:
- ❌ Commit `.env` files to Git
- ❌ Hardcode keys in your source code
- ❌ Share keys in screenshots or documentation
- ❌ Commit keys to GitHub

---

## 📋 Quick Checklist: Where Are My Keys?

- [ ] **Local Development**: Check `.env` file or `env` command
- [ ] **Render Deployment**: Render Dashboard → Environment tab
- [ ] **Lovable Deployment**: Lovable Dashboard → Environment Variables
- [ ] **Original Source**: API provider dashboards (OpenWeatherMap, Eventbrite, etc.)

---

## 💡 Pro Tips

1. **Use a Password Manager**: Store API keys securely in a password manager (1Password, LastPass, etc.)

2. **Different Keys for Different Environments**:
   - Development keys (for local testing)
   - Production keys (for deployed apps)

3. **Rotate Keys Regularly**: Change API keys periodically for security

4. **Monitor Usage**: Check API provider dashboards to monitor key usage and set up alerts

---

## 🆘 If You Lost Your Keys

1. **Check API Provider Dashboard**: Log in and view existing keys
2. **Regenerate if Needed**: Most providers allow you to regenerate keys
3. **Update Everywhere**: After regenerating, update:
   - Local `.env` file
   - Render environment variables
   - Lovable environment variables
   - Any other deployment platforms

---

## Summary

**Cursor doesn't store API keys.** To view them:

1. **Locally**: Check `.env` file or run `env | grep API_KEY`
2. **Render**: Dashboard → Your Service → Environment tab
3. **Lovable**: Dashboard → Settings → Environment Variables
4. **Original Source**: API provider dashboards

Your keys are safe as long as:
- ✅ `.env` files are in `.gitignore` (already done)
- ✅ Keys are set in deployment platform dashboards
- ✅ Keys are never committed to Git

