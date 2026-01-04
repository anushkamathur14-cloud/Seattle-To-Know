# How to Set Eventbrite API Key

## Quick Setup Guide

### Option 1: Local Development (.env file) - Recommended

#### Step 1: Create or Edit .env File

In Cursor's terminal (`` Ctrl + ` ``) or your system terminal:

```bash
cd "/Users/anushkamathur/Desktop/Seattle to know"
nano .env
```

Or if the file already exists:
```bash
nano .env
```

#### Step 2: Add Your Eventbrite API Key

Add this line to the file:
```
EVENTBRITE_API_KEY=your_actual_eventbrite_key_here
```

**Example:**
```
EVENTBRITE_API_KEY=ABC123XYZ456DEF789
```

#### Step 3: Save and Exit

- **Nano editor**: Press `Ctrl + X`, then `Y`, then `Enter`
- **VS Code/Cursor**: Just save the file (`Cmd + S`)

#### Step 4: Verify It's Set

```bash
# Check if the key is in the file
cat .env | grep EVENTBRITE
```

#### Step 5: Restart Your Server

If your server is running, stop it (`Ctrl + C`) and restart:

```bash
uvicorn app.main:app --reload
```

Now your app will use real Eventbrite events!

---

### Option 2: Export in Terminal (Temporary)

This only works for the current terminal session:

```bash
export EVENTBRITE_API_KEY="your_actual_eventbrite_key_here"
```

Then start your server:
```bash
uvicorn app.main:app --reload
```

**Note**: This is temporary - you'll need to export again if you close the terminal.

---

### Option 3: Set on Render (For Deployment)

#### Step 1: Go to Render Dashboard

1. Visit [render.com](https://render.com)
2. Log in to your account
3. Click on your **Web Service**

#### Step 2: Add Environment Variable

1. Click on **"Environment"** tab (left sidebar)
2. Click **"Add Environment Variable"**
3. Enter:
   - **Key**: `EVENTBRITE_API_KEY`
   - **Value**: `your_actual_eventbrite_key_here`
4. Click **"Add"** or **"Save Changes"**

#### Step 3: Redeploy

Render will automatically redeploy, or you can manually trigger a redeploy.

---

## ✅ Verify It's Working

### Test Locally

1. **Start server**: `uvicorn app.main:app --reload`
2. **Open browser**: `http://localhost:8000`
3. **Go to Events tab**
4. **Check events**: You should see real events from Eventbrite (not placeholders)

### Test on Render

1. **Wait for redeploy** to complete
2. **Visit your Render URL**: `https://your-app.onrender.com`
3. **Go to Events tab**
4. **Check events**: Should see real Eventbrite events

---

## 🔍 How to Check If Key Is Set

### In Python:

```python
import os
key = os.getenv("EVENTBRITE_API_KEY")
if key:
    print("✅ Eventbrite API key is SET")
    print(f"Key starts with: {key[:5]}...")  # Show first 5 chars only
else:
    print("❌ Eventbrite API key is NOT SET")
```

### In Terminal:

```bash
# Check if set in environment
echo $EVENTBRITE_API_KEY

# Check if in .env file
cat .env | grep EVENTBRITE_API_KEY
```

---

## 🐛 Troubleshooting

### "Key still not working"

**Solutions:**
1. **Restart server**: Stop (`Ctrl + C`) and restart
2. **Check .env file location**: Must be in project root
3. **Check file name**: Must be exactly `.env` (with the dot)
4. **Verify key format**: No extra spaces or quotes
5. **Check key is valid**: Test it on Eventbrite's API directly

### "Events still showing placeholders"

**Solutions:**
1. **Verify key is loaded**: Run the Python check above
2. **Check server logs**: Look for API errors
3. **Test API key**: Make sure it's valid and active
4. **Check API quotas**: Eventbrite may have rate limits

### "Key works locally but not on Render"

**Solutions:**
1. **Verify in Render dashboard**: Go to Environment tab
2. **Check variable name**: Must be exactly `EVENTBRITE_API_KEY` (case-sensitive)
3. **Redeploy**: After adding variable, trigger a redeploy
4. **Check build logs**: Look for errors in Render logs

---

## 📋 Quick Checklist

- [ ] Created `.env` file in project root
- [ ] Added `EVENTBRITE_API_KEY=your_key` to `.env`
- [ ] Saved the file
- [ ] Restarted server
- [ ] Verified events are real (not placeholders)
- [ ] Set key in Render dashboard (for deployment)
- [ ] Redeployed on Render

---

## 🔒 Security Reminders

- ✅ `.env` file is already in `.gitignore` (won't be committed)
- ✅ Never commit API keys to Git
- ✅ Use different keys for development and production
- ✅ Don't share your API key publicly

---

## 💡 Pro Tips

1. **Test locally first**: Set key in `.env`, test, then deploy to Render
2. **Keep keys secure**: Use a password manager to store keys
3. **Rotate keys**: Change keys periodically for security
4. **Monitor usage**: Check Eventbrite dashboard for API usage

---

## 🎯 Next Steps

After setting the key:

1. **Test locally** to make sure it works
2. **Set on Render** for production
3. **Verify real events** are showing
4. **Enjoy real Seattle events!** 🎉

