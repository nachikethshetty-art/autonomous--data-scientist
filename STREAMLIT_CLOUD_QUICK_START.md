# 🚀 STREAMLIT CLOUD DEPLOYMENT - QUICK START

## 📍 What You Need

1. **GitHub Account** ✅ (You have: nachikethshetty-art)
2. **Streamlit Cloud Account** → Create at: https://share.streamlit.io
3. **Deployed Backend API** → Deploy FastAPI to Render/Railway
4. **API Key/URL** → Will get from backend deployment

---

## 🎯 3-STEP DEPLOYMENT PROCESS

### STEP 1: Deploy Backend API (FastAPI)
**Where**: https://render.com (FREE tier available)

1. Go to Render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repo
4. Select repository: `autonomous--data-scientist`
5. **Build Command**: `pip install -r requirements.txt`
6. **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
7. **Environment Variables**:
   - Add any needed (GOOGLE_API_KEY, etc.)
8. Click "Create Web Service"
9. **Wait ~2-3 minutes for deployment**
10. **Copy the URL** (looks like: `https://your-service.onrender.com`)

---

### STEP 2: Deploy Frontend (Streamlit Dashboard)
**Where**: https://share.streamlit.io

1. Go to https://share.streamlit.io
2. Click "Create app"
3. **Repository**: `nachikethshetty-art/autonomous--data-scientist`
4. **Branch**: `main`
5. **Main file path**: `dashboard/app.py`
6. Click "Deploy!" ✅

---

### STEP 3: Add Secrets in Streamlit Cloud
**After dashboard deploys:**

1. Click **☰ menu** (top-right)
2. Click **Settings** → **Secrets**
3. **Paste this**:
```toml
API_URL = "https://your-service.onrender.com"
GOOGLE_API_KEY = "your-api-key"
```
4. Click "Save" ✅

---

## 🔗 YOUR DEPLOYMENT LINKS (After Deploy)

| Service | Link | Status |
|---------|------|--------|
| Frontend Dashboard | https://[you]-autonomous-ai-data-scientist.streamlit.app | Will get after deploy |
| Backend API | https://[your-service].onrender.com | Will get after deploy |
| API Docs | https://[your-service].onrender.com/docs | Test endpoint here |

---

## ✅ Verification Checklist

After deployment:
- [ ] Frontend loads at Streamlit URL
- [ ] Backend API responds to: `https://your-api-url/docs`
- [ ] Dashboard can connect to API (check in secrets)
- [ ] Can upload CSV file
- [ ] Problem detection works
- [ ] Reports generate

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Frontend won't load | Check `requirements.txt` has `streamlit>=1.40.0` |
| "API Connection Error" | Verify `API_URL` in Streamlit Cloud secrets |
| Backend returns 404 | Check backend deployed at Render and running |
| CORS Error | Backend needs CORS middleware (will add if needed) |
| Cold start timeout | Render free tier is slow, give it 30 seconds |

---

## 📋 FILES READY FOR DEPLOYMENT

✅ `requirements.txt` - All dependencies
✅ `dashboard/app.py` - Main dashboard (updated with env vars)
✅ `api/main.py` - FastAPI backend
✅ `.streamlit/config.toml` - Streamlit config
✅ `.streamlit/secrets.toml.example` - Secrets template
✅ `STREAMLIT_DEPLOYMENT_GUIDE.md` - Full guide

---

## 🎓 Key Concepts

**API_URL**: 
- Local dev: `http://localhost:8000`
- Cloud deployment: `https://your-service.onrender.com`
- Streamlit Cloud uses secrets for production URL

**Secrets**:
- Local: `.streamlit/secrets.toml` (git-ignored)
- Cloud: Added via Streamlit Cloud dashboard
- Access in code: `st.secrets.get("API_URL")`

---

## 📞 NEED HELP?

- Streamlit Docs: https://docs.streamlit.io/deploy/streamlit-cloud
- Render Docs: https://render.com/docs
- Railway Docs: https://docs.railway.app/deploy/fastapi

---

**Status**: ✅ YOUR PROJECT IS READY TO DEPLOY!
