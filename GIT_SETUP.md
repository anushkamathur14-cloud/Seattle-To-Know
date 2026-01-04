# Connecting Your Project to GitHub

Follow these steps to connect your local project to your GitHub repository.

## Step 1: Initialize Git Repository

```bash
cd "/Users/anushkamathur/Desktop/Seattle to know"
git init
```

## Step 2: Add All Files

```bash
git add .
```

## Step 3: Create Initial Commit

```bash
git commit -m "Initial commit: Seattle To Know application"
```

## Step 4: Add Your GitHub Remote

Replace `YOUR_USERNAME`` and `YOUR_REPO_NAME` with your actual GitHub username and repository name:

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

Or if you're using SSH:

```bash
git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO_NAME.git
```

## Step 5: Push to GitHub

```bash
git branch -M main
git push -u origin main
```

## Alternative: If Repository Already Has Content

If your GitHub repository already has files (like a README), you may need to pull first:

```bash
git pull origin main --allow-unrelated-histories
```

Then resolve any conflicts and push:

```bash
git push -u origin main
```

## Verify Connection

Check that your remote is set correctly:

```bash
git remote -v
```

You should see your GitHub repository URL listed.

## Important Notes

⚠️ **Never commit `.env` files** - They contain your API keys!
- The `.gitignore` file I created will prevent this
- Make sure to set environment variables in Lovable's dashboard instead

## Next Steps

After pushing to GitHub:
1. Your code will be on GitHub
2. Lovable can automatically deploy from your GitHub repository
3. Any future changes can be pushed with `git push`

