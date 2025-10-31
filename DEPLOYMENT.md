# Deployment Guide: SaarthiAI on Render & Vercel

This guide will help you deploy SaarthiAI with the backend on Render and the frontend on Vercel.

## Architecture Overview

- **Backend**: Flask API deployed on Render
- **Frontend**: React + Vite deployed on Vercel
- **Database**: Vector database (pickle file included in backend)

## Prerequisites

1. GitHub account (recommended) or Git repository
2. Render account (free tier available) - [Sign up here](https://render.com)
3. Vercel account (free tier available) - [Sign up here](https://vercel.com)
4. Google Gemini API key - [Get one here](https://makersuite.google.com/app/apikey)

---

## Step 1: Deploy Backend to Render

### 1.1 Prepare Your Repository

1. Push your code to GitHub (if not already done):
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

### 1.2 Create Render Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository (or use Public Git repository)
4. Fill in the following details:
   - **Name**: `saarthi-backend` (or your preferred name)
   - **Environment**: `Python 3`
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`

### 1.3 Set Environment Variables in Render

In the Render dashboard, go to **Environment** tab and add:

| Key | Value | Notes |
|-----|-------|-------|
| `GEMINI_API_KEY` | `your_actual_api_key` | Your Google Gemini API key |
| `ALLOWED_ORIGINS` | `https://your-frontend.vercel.app` | We'll update this after Vercel deployment |
| `PORT` | `10000` | Render sets this automatically, but set as backup |

**Note**: Keep `ALLOWED_ORIGINS` flexible for now. You can add multiple origins separated by commas:
```
https://your-app.vercel.app,https://your-custom-domain.com
```

### 1.4 Deploy and Get Backend URL

1. Click **"Create Web Service"**
2. Wait for the deployment to complete (may take 5-10 minutes)
3. Once deployed, note your backend URL: `https://your-backend-name.onrender.com`
4. Test the health endpoint: `https://your-backend-name.onrender.com/health`

### 1.5 Using render.yaml (Alternative Method)

If you prefer using the `render.yaml` file:

1. Ensure `render.yaml` is in the root of your repository
2. In Render dashboard, click **"New +"** → **"Blueprint"**
3. Connect your repository
4. Render will automatically detect and use `render.yaml`
5. Still need to set `GEMINI_API_KEY` manually in the Environment tab

---

## Step 2: Deploy Frontend to Vercel

### 2.1 Install Vercel CLI (Optional but Recommended)

```bash
npm install -g vercel
```

### 2.2 Deploy via Vercel Dashboard

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Configure the project:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (should auto-detect)
   - **Output Directory**: `dist` (should auto-detect)
   - **Install Command**: `npm install` (should auto-detect)

### 2.3 Set Environment Variables in Vercel

In the Vercel project settings, go to **Environment Variables** and add:

| Key | Value |
|-----|-------|
| `VITE_API_BASE_URL` | `https://your-backend-name.onrender.com` |

**Important**: 
- Replace `your-backend-name.onrender.com` with your actual Render backend URL
- Vercel automatically prefixes `VITE_` environment variables for Vite apps
- After adding, you'll need to redeploy for changes to take effect

### 2.4 Deploy and Get Frontend URL

1. Click **"Deploy"**
2. Wait for deployment (usually 2-5 minutes)
3. Once deployed, note your frontend URL: `https://your-app-name.vercel.app`

---

## Step 3: Update CORS Settings

### 3.1 Update Backend CORS

1. Go back to Render dashboard
2. Navigate to your backend service
3. Go to **Environment** tab
4. Update `ALLOWED_ORIGINS`:
   ```
   https://your-app-name.vercel.app
   ```
   Or if you have multiple origins:
   ```
   https://your-app-name.vercel.app,https://your-custom-domain.com
   ```
5. Click **"Save Changes"**
6. Render will automatically redeploy

### 3.2 Verify CORS Configuration

Test that CORS is working:
```bash
curl -H "Origin: https://your-app-name.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://your-backend-name.onrender.com/query
```

You should see CORS headers in the response.

---

## Step 4: Test the Deployment

1. **Test Backend**: 
   - Visit: `https://your-backend-name.onrender.com/health`
   - Should return: `{"status": "healthy", ...}`

2. **Test Frontend**:
   - Visit: `https://your-app-name.vercel.app`
   - Try asking a question
   - Check browser console for any CORS errors

3. **Common Issues**:
   - **CORS Error**: Make sure `ALLOWED_ORIGINS` in Render includes your exact Vercel URL (no trailing slash)
   - **API Not Found**: Verify `VITE_API_BASE_URL` in Vercel matches your Render backend URL
   - **502/503 Errors**: Render free tier spins down after inactivity. First request may take 30-60 seconds

---

## Step 5: (Optional) Custom Domain

### 5.1 Vercel Custom Domain

1. In Vercel project settings, go to **Domains**
2. Add your custom domain
3. Follow DNS configuration instructions
4. Update `ALLOWED_ORIGINS` in Render to include your custom domain

### 5.2 Render Custom Domain

1. In Render service settings, go to **Custom Domains**
2. Add your custom domain
3. Update DNS records as instructed

---

## Important Notes

### Render Free Tier Limitations

- **Spins down after 15 minutes of inactivity**
- First request after spin-down takes 30-60 seconds (cold start)
- **Solution**: Use Render's "Always On" feature (paid) or a cron job to ping your service

### Environment Variables Security

- ✅ Never commit API keys to Git
- ✅ Use environment variables in Render/Vercel dashboards
- ✅ Use `.env.example` files for documentation

### File Size Considerations

- Large pickle files (vector_database.pkl) are included in the repo
- Render may have limits on deployment size
- If issues occur, consider using external storage (S3, etc.)

### Performance Optimization

1. **Backend**: 
   - Consider upgrading Render plan for better performance
   - Monitor logs in Render dashboard

2. **Frontend**:
   - Vite build optimizes automatically
   - Vercel CDN provides fast global delivery

---

## Troubleshooting

### Backend Issues

**Problem**: Backend returns 500 error
- **Solution**: Check Render logs, verify `GEMINI_API_KEY` is set correctly

**Problem**: Backend times out
- **Solution**: Increase timeout in gunicorn command: `--timeout 180`

**Problem**: Vector database not loading
- **Solution**: Ensure `vector_database.pkl` is in the `backend` directory

### Frontend Issues

**Problem**: API calls fail with CORS error
- **Solution**: 
  1. Verify `ALLOWED_ORIGINS` in Render includes exact frontend URL
  2. Check for trailing slashes
  3. Clear browser cache

**Problem**: API calls go to localhost
- **Solution**: 
  1. Verify `VITE_API_BASE_URL` is set in Vercel
  2. Redeploy frontend after setting environment variable
  3. Clear browser cache

**Problem**: Build fails on Vercel
- **Solution**: 
  1. Check build logs
  2. Ensure `package.json` is in `frontend` directory
  3. Verify all dependencies are listed

---

## Quick Reference

### Backend (Render)
- **URL**: `https://your-backend-name.onrender.com`
- **Health Check**: `https://your-backend-name.onrender.com/health`
- **Main Endpoint**: `https://your-backend-name.onrender.com/query`

### Frontend (Vercel)
- **URL**: `https://your-app-name.vercel.app`
- **Build**: Automatic on Git push
- **Environment**: Set `VITE_API_BASE_URL`

### Environment Variables Checklist

**Render (Backend)**:
- [ ] `GEMINI_API_KEY` - Your Gemini API key
- [ ] `ALLOWED_ORIGINS` - Your Vercel frontend URL
- [ ] `PORT` - Auto-set by Render (10000 as backup)

**Vercel (Frontend)**:
- [ ] `VITE_API_BASE_URL` - Your Render backend URL

---

## Support

If you encounter issues:
1. Check Render logs: Dashboard → Your Service → Logs
2. Check Vercel logs: Dashboard → Your Project → Deployments → Click on deployment → View Function Logs
3. Check browser console for frontend errors
4. Verify all environment variables are set correctly

Good luck with your deployment! 🚀

