# 🎯 DEPLOYMENT QUICK REFERENCE CARD

```
═══════════════════════════════════════════════════════════════════════════════
                    STREAMLIT CLOUD DEPLOYMENT - QUICK GUIDE
═══════════════════════════════════════════════════════════════════════════════

YOUR GITHUB REPO:
  Repository: nachikethshetty-art/autonomous--data-scientist
  Branch: main
  Status: ✅ READY TO DEPLOY


STEP 1: DEPLOY BACKEND API (FastAPI)
─────────────────────────────────────────────────────────────────────────────
  
  Platform: Render.com (FREE tier available)
  URL: https://render.com
  
  Steps:
    1. Sign in with GitHub
    2. Click "New +" → "Web Service"
    3. Select repo: autonomous--data-scientist
    4. Build Command: pip install -r requirements.txt
    5. Start Command: uvicorn api.main:app --host 0.0.0.0 --port $PORT
    6. Click "Create Web Service"
  
  ⏱️  Wait 2-3 minutes
  
  RESULT: https://[your-service].onrender.com
           └─→ SAVE THIS URL


STEP 2: DEPLOY FRONTEND (Streamlit)
─────────────────────────────────────────────────────────────────────────────
  
  Platform: Streamlit Cloud
  URL: https://share.streamlit.io
  
  Steps:
    1. Click "Create app"
    2. GitHub Repo: nachikethshetty-art/autonomous--data-scientist
    3. Branch: main
    4. Main file path: dashboard/app.py
    5. Click "Deploy"
  
  ⏱️  Wait 1-2 minutes
  
  RESULT: https://[username]-autonomous-ai-data-scientist.streamlit.app
          └─→ THIS IS YOUR PUBLIC DASHBOARD URL


STEP 3: ADD SECRETS
─────────────────────────────────────────────────────────────────────────────
  
  In your deployed Streamlit app:
    1. Click ⋮ menu (top right) → Settings → Secrets
    2. Paste this:
    
       API_URL = "https://[your-service].onrender.com"
       GOOGLE_API_KEY = "your-google-api-key"
    
    3. Click "Save"
  
  App auto-restarts with secrets loaded ✅


═══════════════════════════════════════════════════════════════════════════════
                               FINAL RESULT
═══════════════════════════════════════════════════════════════════════════════

  📍 FRONTEND:  https://[username]-autonomous-ai-data-scientist.streamlit.app
  📍 BACKEND:   https://[your-service].onrender.com
  📍 API DOCS:  https://[your-service].onrender.com/docs


═══════════════════════════════════════════════════════════════════════════════
                            FILES PROVIDED
═══════════════════════════════════════════════════════════════════════════════

  📄 DEPLOYMENT_SUMMARY.md
     └─→ Full overview and checklist

  📄 STREAMLIT_DEPLOYMENT_GUIDE.md
     └─→ Detailed 5-step guide with troubleshooting

  📄 STREAMLIT_CLOUD_QUICK_START.md
     └─→ Quick reference

  📄 STREAMLIT_SECRETS_SETUP.md
     └─→ Secrets management

  ✅ dashboard/app.py
     └─→ Updated with environment variables

  ✅ .streamlit/config.toml
     └─→ Ready for production

  ✅ .streamlit/secrets.toml.example
     └─→ Template (don't commit real secrets)


═══════════════════════════════════════════════════════════════════════════════
                            TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════════════

  ❌ "API Connection Error"
     ✅ Check API_URL in secrets matches your Render URL
     ✅ Visit https://[backend-url]/docs to verify API is running

  ❌ "ModuleNotFoundError"
     ✅ Make sure requirements.txt is in root directory
     ✅ Try: pip install -r requirements.txt locally

  ❌ "Timeout on first load"
     ✅ Free tier Render instances take 30-60 seconds to start
     ✅ Refresh page after 1 minute

  ❌ "CORS Error" or "403 Forbidden"
     ✅ Backend CORS is already configured ✅
     ✅ Not needed


═══════════════════════════════════════════════════════════════════════════════
                             HELPFUL LINKS
═══════════════════════════════════════════════════════════════════════════════

  🔗 Streamlit Cloud:        https://share.streamlit.io
  🔗 Render.com:             https://render.com
  🔗 Google API Keys:        https://makersuite.google.com/app/apikey
  🔗 Streamlit Docs:         https://docs.streamlit.io/deploy/streamlit-cloud
  🔗 Render FastAPI Docs:    https://render.com/docs/deploy-fastapi


═══════════════════════════════════════════════════════════════════════════════

✅ YOUR PROJECT IS 100% READY TO DEPLOY!

Just follow the 3 steps above and you'll be live in ~5-10 minutes.

═══════════════════════════════════════════════════════════════════════════════
```

---

## 🔑 COPY-PASTE SECRETS (after you have backend URL)

Replace `https://your-service.onrender.com` with your actual Render URL:

```toml
API_URL = "https://your-service.onrender.com"
GOOGLE_API_KEY = "AIza..."
ENABLE_PROBLEM_DETECTION = true
ENABLE_CHAT = true
ENABLE_REPORTS = true
```

---

## 📝 NOTES

- **Render** deploys both frontend and backend
- **Streamlit Cloud** is just for the frontend (dashboard)
- **Free tier** on Render works great for testing
- **API_URL** is the most important secret to add
- All files are **committed to GitHub** ✅

---

## 🚀 START HERE

1. Go to https://render.com (deploy backend)
2. Go to https://share.streamlit.io (deploy frontend)
3. Add secrets in Streamlit Cloud dashboard
4. Test at your new dashboard URL

Done! ✅
