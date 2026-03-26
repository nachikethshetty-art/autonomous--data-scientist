# 🚀 Streamlit Cloud Deployment Guide

## Step 1: Prepare Your Repository

Your project is already ready for deployment! We've configured:
- ✅ `requirements.txt` - All dependencies listed
- ✅ `dashboard/app.py` - Uses environment variables for API URL
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ `.streamlit/secrets.toml.example` - Secrets template

## Step 2: Push Code to GitHub

Make sure your code is pushed to GitHub:

```bash
cd /Users/amshumathshetty/Desktop/autonomous-ai-data-scientist
git add -A
git commit -m "feat: Prepare for Streamlit Cloud deployment"
git push origin main
```

## Step 3: Create Streamlit Cloud Account & Deploy

### 3a. Sign Up/Login to Streamlit Cloud
🔗 **Go to**: https://share.streamlit.io

- Click "Sign in with GitHub"
- Authorize Streamlit
- Click "Create app"

### 3b. Deploy Your App

**Fill in the deployment form:**
- **Repository**: `nachikethshetty-art/autonomous--data-scientist` (your GitHub username/repo)
- **Branch**: `main`
- **Main file path**: `dashboard/app.py`

**Click "Deploy!"** ✅

---

## Step 4: Add Secrets in Streamlit Cloud

Once your app is deployed, you need to add secrets:

### 4a. Access Secrets Dashboard
1. Go to your deployed app URL
2. Click the **☰ menu** (hamburger) in top-right
3. Select **Settings** → **Secrets**

### 4b. Add Your Secrets

**Paste this into the secrets editor:**

```toml
# API Configuration - IMPORTANT: Update with your deployed API URL
API_URL = "https://your-api-deployment-url.com"

# LLM Configuration (optional)
OLLAMA_BASE_URL = "http://localhost:11434"
GOOGLE_API_KEY = "your-google-api-key-here"

# Database Configuration
DATABASE_URL = "sqlite:///jobs.db"

# Feature Flags
ENABLE_PROBLEM_DETECTION = true
ENABLE_CHAT = true
ENABLE_REPORTS = true
```

**Click "Save"** ✅

---

## Step 5: Update API_URL (CRITICAL)

You have **two options**:

### Option A: Deploy Your FastAPI Backend to Render/Railway/Heroku

1. **Render.com (Recommended - FREE tier available)**
   - Go to: https://render.com
   - Connect GitHub repo
   - Create Web Service
   - Deploy `api/main.py` with Uvicorn
   - Get your API URL: `https://your-api-service.onrender.com`

2. **Railway.app**
   - Go to: https://railway.app
   - Connect GitHub
   - Deploy FastAPI service
   - Get public URL

3. **Heroku (Paid - $7+/month)**
   - Traditional option, slightly more expensive

### Option B: Use Streamlit Community Cloud (Simpler but API still needed)

- Deploy both frontend and backend separately
- Frontend (dashboard) → Streamlit Cloud
- Backend (API) → Render or Railway

---

## 📋 Checklist Before Deployment

- [ ] Code pushed to GitHub
- [ ] `requirements.txt` has all dependencies
- [ ] `dashboard/app.py` main file exists
- [ ] API_URL uses environment variable (✅ Already done)
- [ ] Secrets are configured in Streamlit Cloud
- [ ] Backend API is deployed (if using remote API)

---

## 🔗 Deployment URLs

### Frontend (Dashboard)
After deploying on Streamlit Cloud, you'll get URL like:
```
https://[your-username]-autonomous-ai-data-scientist.streamlit.app
```

### Backend (API)
After deploying on Render/Railway:
```
https://[your-api-service].onrender.com
```
OR
```
https://[your-railway-service].railway.app
```

---

## 🆘 Troubleshooting

### "ModuleNotFoundError"
- Check `requirements.txt` has all imports
- Run locally: `pip install -r requirements.txt`

### "API Connection Error"
- Verify `API_URL` is correct in Streamlit Cloud secrets
- Check backend is deployed and running
- Test API directly: `https://your-api-url/docs`

### "Timeout Loading Page"
- Backend may be slow starting (cold start)
- Free tier services have startup delays
- Consider paid tier for production

### "403 Forbidden / CORS Error"
- Add CORS configuration to FastAPI backend:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Be more specific in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 After Deployment

### Monitor Your App
- Streamlit Cloud dashboard shows logs
- Check backend logs on Render/Railway
- Use Streamlit's built-in error reporting

### Update Your App
- Push changes to GitHub
- Streamlit Cloud auto-redeploys
- No manual steps needed!

---

## 🎯 Next Steps (After Successful Deployment)

1. ✅ Test dashboard at new URL
2. ✅ Verify API connection works
3. ✅ Test all features (upload, detection, reports)
4. ✅ Share link with team
5. ✅ Monitor performance
6. ✅ Plan CI/CD integration

---

## 💡 Pro Tips

**Local Testing Before Deployment:**
```bash
# Test locally with production settings
export API_URL="https://your-api-deployment-url.com"
streamlit run dashboard/app.py
```

**Git Ignore Secrets:**
```bash
# .gitignore should have:
.streamlit/secrets.toml  # ✅ Already in .gitignore
```

**Environment Variables:**
- Streamlit Cloud automatically loads from `.streamlit/secrets.toml`
- Local dev uses `.streamlit/secrets.toml` (git-ignored)
- Production uses Streamlit Cloud dashboard

---

## 📞 Support Links

- Streamlit Cloud Docs: https://docs.streamlit.io/deploy/streamlit-cloud
- Streamlit Cloud Dashboard: https://share.streamlit.io
- Render Deployment: https://render.com/docs
- Railway Deployment: https://docs.railway.app
