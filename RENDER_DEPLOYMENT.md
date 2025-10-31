# How to Deploy SaarthiAI Backend to Render

This guide will walk you through deploying your Flask backend to Render.

## Prerequisites

- [ ] GitHub account with your code pushed to a repository
- [ ] Render account (free) - [Sign up here](https://render.com)
- [ ] Google Gemini API key - [Get one here](https://makersuite.google.com/app/apikey)

---

## Method 1: Using render.yaml (Recommended - Automatic Setup)

### Step 1: Prepare Your Code

1. **Ensure your code is on GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Verify `render.yaml` is in the root of your repository** (✅ Already done!)

### Step 2: Create Render Blueprint

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** button (top right)
3. Select **"Blueprint"** from the dropdown
4. Click **"Connect account"** to connect your GitHub account (if not already connected)
5. Select your repository from the list
6. Click **"Apply"**

### Step 3: Review Configuration

Render will automatically detect your `render.yaml` file and show:
- Service name: `saarthi-backend`
- Environment: Python
- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`

### Step 4: Set Environment Variables

Before deploying, you need to set your environment variables:

1. In the Render dashboard, you'll see a section for **Environment Variables**
2. Click **"Add Environment Variable"** and add:

   **Variable 1: GEMINI_API_KEY**
   - Key: `GEMINI_API_KEY`
   - Value: Your actual Gemini API key (e.g., `AIzaSyC1yEnlXvWwXPapThk76MgN47ZLRwfvMLY`)
   - Click **"Save"**

   **Variable 2: ALLOWED_ORIGINS** (Optional for now)
   - Key: `ALLOWED_ORIGINS`
   - Value: Leave empty for now, or add `http://localhost:3000` for local testing
   - You'll update this later with your Vercel frontend URL
   - Click **"Save"**

   **Variable 3: PORT** (Optional - already in render.yaml)
   - Key: `PORT`
   - Value: `10000` (Render sets this automatically, but good to have as backup)

### Step 5: Deploy

1. Click **"Apply"** or **"Create Blueprint"** button
2. Render will start the deployment process
3. You'll see a deployment log showing:
   - Building dependencies
   - Installing packages
   - Starting the service

### Step 6: Wait for Deployment

- First deployment takes **5-10 minutes**
- Watch the logs in real-time
- You'll see messages like:
  ```
  Building...
  Installing dependencies...
  Starting service...
  ```

### Step 7: Get Your Backend URL

Once deployment completes:
- Your service will have a URL like: `https://saarthi-backend-xxxx.onrender.com`
- **Note this URL** - you'll need it for the frontend deployment!

### Step 8: Test Your Deployment

1. **Health Check:**
   Open in browser: `https://your-service-name.onrender.com/health`
   Should return: `{"status": "healthy", ...}`

2. **API Info:**
   Open: `https://your-service-name.onrender.com/`
   Should show API information

---

## Method 2: Manual Setup (Alternative)

If you prefer manual setup instead of using the blueprint:

### Step 1: Create Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository

### Step 2: Configure Service

Fill in these details:

| Setting | Value |
|---------|-------|
| **Name** | `saarthi-backend` |
| **Environment** | `Python 3` |
| **Region** | Choose closest to your users (e.g., `Oregon (US West)`) |
| **Branch** | `main` (or your default branch) |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120` |

### Step 3: Set Environment Variables

Go to the **"Environment"** tab and add:

1. **GEMINI_API_KEY**
   ```
   Key: GEMINI_API_KEY
   Value: your_actual_gemini_api_key
   ```

2. **ALLOWED_ORIGINS**
   ```
   Key: ALLOWED_ORIGINS
   Value: (leave empty for now or use http://localhost:3000)
   ```

3. **PORT** (optional)
   ```
   Key: PORT
   Value: 10000
   ```

### Step 4: Create Service

1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes)
3. Get your backend URL

---

## Important Notes

### ⚠️ Free Tier Limitations

Render's free tier has some limitations:

1. **Spins Down After 15 Minutes of Inactivity**
   - After 15 minutes without requests, the service goes to sleep
   - First request after sleep takes **30-60 seconds** (cold start)
   - Subsequent requests are fast

2. **Solution Options:**
   - **Option A**: Upgrade to paid plan ($7/month) - service stays always on
   - **Option B**: Use a free cron job service (like cron-job.org) to ping your service every 10 minutes
   - **Option C**: Accept the cold start delay (not ideal for production)

### 🔍 Monitoring Your Deployment

1. **View Logs:**
   - Go to your service in Render dashboard
   - Click **"Logs"** tab
   - See real-time logs and errors

2. **Check Health:**
   - Use the `/health` endpoint
   - Should return: `{"status": "healthy"}`

3. **Test Query Endpoint:**
   ```bash
   curl -X POST https://your-service.onrender.com/query \
     -H "Content-Type: application/json" \
     -d '{"question": "What is rice production in India?"}'
   ```

### 🔧 Troubleshooting

**Problem: Deployment fails**
- Check logs in Render dashboard
- Verify `requirements.txt` is in `backend` folder
- Ensure `app.py` exists in `backend` folder

**Problem: Service won't start**
- Check if `GEMINI_API_KEY` is set correctly
- Verify gunicorn is in `requirements.txt` ✅ (it is!)
- Check logs for specific error messages

**Problem: 503/504 errors**
- Service might be spinning up (free tier)
- Wait 30-60 seconds and try again
- Check if service is awake in Render dashboard

**Problem: CORS errors**
- Verify `ALLOWED_ORIGINS` includes your frontend URL
- No trailing slash in URLs
- Check backend logs for CORS-related messages

**Problem: Vector database not loading**
- Verify `vector_database.pkl` is in `backend` directory
- Check file size limits (Render free tier has size limits)
- Check logs for file loading errors

### 📝 After Deployment Checklist

- [ ] Service deployed successfully
- [ ] Health endpoint works: `/health`
- [ ] API endpoint works: `/query`
- [ ] Backend URL noted: `https://__________.onrender.com`
- [ ] Environment variables set:
  - [ ] `GEMINI_API_KEY` ✅
  - [ ] `ALLOWED_ORIGINS` (update later with frontend URL)
- [ ] Logs show no errors

### 🔗 Next Steps

After your backend is deployed:

1. **Deploy Frontend to Vercel** (see `DEPLOYMENT.md`)
2. **Update CORS** in Render with your Vercel frontend URL
3. **Test the full application**

---

## Quick Reference

**Backend URL Format:**
```
https://saarthi-backend-xxxx.onrender.com
```

**Endpoints:**
- Health: `GET /health`
- Query: `POST /query`
- Stats: `GET /stats`
- Home: `GET /`

**Environment Variables:**
- `GEMINI_API_KEY` (required)
- `ALLOWED_ORIGINS` (required for CORS)
- `PORT` (auto-set by Render)

**Start Command:**
```bash
gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

---

**Need help?** Check the logs in Render dashboard or refer to `DEPLOYMENT.md` for complete deployment guide including frontend.

