# Deploying from Cursor to Lovable - Complete Workflow

## Understanding the Workflow

**Cursor** = Your code editor (where you write code)  
**GitHub** = Code repository (where your code is stored)  
**Lovable** = Deployment platform (where your app goes live)

**Flow:** Cursor → GitHub → Lovable → Live URL

---

## Step-by-Step: From Cursor to Live URL

### Step 1: Code in Cursor ✅ (You're already here!)

You're writing and editing your code in Cursor. That's perfect!

### Step 2: Push Code to GitHub

In Cursor's integrated terminal (or your system terminal), run:

```bash
cd "/Users/anushkamathur/Desktop/Seattle to know"

# If not already initialized
git init
git add .
git commit -m "Initial commit"

# Connect to your GitHub repository
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

**Or use Cursor's Git integration:**
1. Open Source Control panel (Ctrl/Cmd + Shift + G)
2. Stage all changes
3. Commit with message
4. Push to GitHub

### Step 3: Connect GitHub to Lovable

1. **Go to Lovable Dashboard**
   - Visit [lovable.dev](https://lovable.dev)
   - Log in to your account

2. **Create/Select Project**
   - Click "New Project" or select existing
   - Choose "Import from GitHub"

3. **Authorize & Connect**
   - Click "Connect GitHub" or "Authorize GitHub"
   - Grant Lovable access to your repositories
   - Select your repository: `YOUR_USERNAME/seattle-to-know`

4. **Configure Build Settings**
   - **Runtime**: Python 3.9+
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `/` (root)

### Step 4: Set Environment Variables in Lovable

In Lovable's project settings → Environment Variables:

**Required:**
```
OPENWEATHER_API_KEY = your_openweather_key
EVENTBRITE_API_KEY = your_eventbrite_key
GOOGLE_PLACES_API_KEY = your_google_places_key
```

**Optional:**
```
TICKETMASTER_API_KEY = your_ticketmaster_key
SEATGEEK_CLIENT_ID = your_seatgeek_client_id
SEATGEEK_CLIENT_SECRET = your_seatgeek_client_secret
```

### Step 5: Deploy & Get Live URL

1. **Click "Deploy" or "Build"** in Lovable
2. **Wait for deployment** (usually 2-5 minutes)
3. **Get your live URL** - Lovable will provide something like:
   ```
   https://your-app-12345.lovable.dev
   ```
   or
   ```
   https://seattle-to-know.lovable.dev
   ```

### Step 6: Your App is Live! 🎉

Your application is now accessible at the Lovable URL!

---

## Future Updates Workflow

When you make changes in Cursor:

1. **Edit code in Cursor**
2. **Commit & Push to GitHub:**
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin main
   ```
3. **Lovable auto-deploys** (if auto-deploy is enabled)
   - Or manually trigger deployment in Lovable dashboard
4. **Changes go live** in a few minutes

---

## Using Cursor's Git Integration

Cursor has built-in Git support:

### Option 1: Terminal in Cursor
- Open terminal: `` Ctrl + ` `` (backtick) or View → Terminal
- Run git commands as shown above

### Option 2: Source Control Panel
1. Click Source Control icon (left sidebar) or `Ctrl/Cmd + Shift + G`
2. Stage changes (click `+` next to files)
3. Enter commit message
4. Click "Commit"
5. Click "..." menu → "Push" or "Push to..."

### Option 3: Command Palette
1. `Ctrl/Cmd + Shift + P`
2. Type "Git: Push"
3. Follow prompts

---

## Quick Checklist

- [ ] Code is ready in Cursor
- [ ] Git repository initialized
- [ ] Code pushed to GitHub
- [ ] Lovable project created
- [ ] GitHub repository connected in Lovable
- [ ] Build settings configured
- [ ] Environment variables set in Lovable
- [ ] Application deployed
- [ ] Live URL received from Lovable

---

## Troubleshooting

### "Can't push to GitHub"
- Check you're authenticated: `git config --global user.name` and `git config --global user.email`
- Verify remote: `git remote -v`
- Check GitHub authentication (may need personal access token)

### "Lovable can't find my repository"
- Make sure repository is public, or
- Grant Lovable access to private repositories in GitHub settings

### "Deployment fails"
- Check build logs in Lovable dashboard
- Verify all environment variables are set
- Ensure `requirements.txt` is correct
- Check Python version compatibility

### "API keys not working"
- Double-check environment variable names (case-sensitive)
- Verify keys are saved in Lovable
- Redeploy after adding/updating variables

---

## Important Notes

1. **Cursor is just the editor** - It doesn't deploy directly
2. **GitHub is the bridge** - Your code repository
3. **Lovable provides the live URL** - After deployment
4. **Environment variables** - Set in Lovable, not in code
5. **Auto-deploy** - Lovable can automatically deploy when you push to GitHub

---

## Summary

**You cannot deploy directly from Cursor**, but the workflow is simple:

```
Cursor (edit code) 
  ↓
GitHub (store code)
  ↓
Lovable (deploy & host)
  ↓
Live URL (your app is live!)
```

The live URL comes from **Lovable**, not Cursor. Cursor helps you write and push code, but Lovable handles deployment and provides the live URL.

