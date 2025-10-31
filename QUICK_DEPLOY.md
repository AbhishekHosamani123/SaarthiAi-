# Quick Deployment Checklist

Follow this checklist for a quick deployment setup.

## Pre-Deployment

- [ ] Code is pushed to GitHub repository
- [ ] Google Gemini API key is ready
- [ ] Render account created
- [ ] Vercel account created

## Backend Deployment (Render)

1. **Create Web Service**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - New + → Web Service
   - Connect GitHub repo
   - Settings:
     - Name: `saarthi-backend`
     - Root Directory: `backend`
     - Build: `pip install -r requirements.txt`
     - Start: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`

2. **Environment Variables** (in Render Dashboard)
   - `GEMINI_API_KEY` = your_api_key_here
   - `ALLOWED_ORIGINS` = (leave empty for now, update after frontend deploy)
   - `PORT` = 10000

3. **Deploy & Note URL**
   - Wait for deployment (5-10 min)
   - Backend URL: `https://__________.onrender.com`
   - Test: `https://__________.onrender.com/health`

## Frontend Deployment (Vercel)

1. **Create Project**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Add New → Project
   - Import GitHub repo
   - Settings:
     - Framework: Vite
     - Root Directory: `frontend`
     - Build: `npm run build`
     - Output: `dist`

2. **Environment Variables** (in Vercel Dashboard)
   - `VITE_API_BASE_URL` = `https://__________.onrender.com` (your Render backend URL)

3. **Deploy & Note URL**
   - Wait for deployment (2-5 min)
   - Frontend URL: `https://__________.vercel.app`

## Final Configuration

1. **Update CORS in Render**
   - Go back to Render → Your Service → Environment
   - Update `ALLOWED_ORIGINS` = `https://__________.vercel.app` (your Vercel frontend URL)
   - Save (auto-redeploys)

2. **Test**
   - Visit frontend URL
   - Try asking a question
   - Check browser console for errors

## URLs Summary

- **Backend**: https://__________.onrender.com
- **Frontend**: https://__________.vercel.app

---

**Need detailed instructions?** See `DEPLOYMENT.md` for comprehensive guide.

