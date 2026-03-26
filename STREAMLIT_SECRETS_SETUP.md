# 🔑 STREAMLIT CLOUD SECRETS - ADD THIS TO YOUR ACCOUNT

## How to Add Secrets to Streamlit Cloud:

1. Go to your deployed app: https://share.streamlit.io
2. Find your app "autonomous-ai-data-scientist"
3. Click the **⋮ (three dots)** menu → **Settings**
4. Click **Secrets** tab
5. **Copy & paste everything below** into the text area
6. Click **Save**

---

## PASTE THIS INTO STREAMLIT CLOUD SECRETS:

```toml
# === API Configuration ===
# Change this to your deployed backend API URL after deployment
API_URL = "https://your-api-service.onrender.com"

# === Optional: Google Generative AI ===
# Only needed if using Google's LLM for problem detection
# Get key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY = "your-google-api-key-here"

# === Optional: Ollama Configuration ===
# Only if you're running Ollama separately
OLLAMA_BASE_URL = "http://localhost:11434"

# === Optional: Database ===
# Default is SQLite, can be changed if needed
DATABASE_URL = "sqlite:///jobs.db"

# === Feature Flags ===
# Enable/disable features as needed
ENABLE_PROBLEM_DETECTION = true
ENABLE_CHAT = true
ENABLE_REPORTS = true
```

---

## 🔐 SECURITY BEST PRACTICES

✅ **DO:**
- Use Streamlit Cloud's secrets manager for sensitive keys
- Use environment-specific values (dev vs production)
- Rotate API keys regularly
- Keep API URLs out of source code

❌ **DON'T:**
- Commit `.streamlit/secrets.toml` to Git
- Share API keys in messages or emails
- Use the same key for dev and production
- Hardcode secrets in code

---

## 📝 STEP-BY-STEP GUIDE TO ADD SECRETS:

### Step 1: Go to Settings
```
Your App → ⋮ Menu → Settings → Secrets
```

### Step 2: Update API_URL
Replace `https://your-api-service.onrender.com` with:
```toml
API_URL = "https://[your-actual-backend-url].onrender.com"
```

### Step 3: Add API Keys (if needed)
```toml
GOOGLE_API_KEY = "AIza..."  # Get from https://makersuite.google.com/app/apikey
```

### Step 4: Click Save
✅ App will auto-reload with new secrets

---

## 🧪 VERIFY SECRETS ARE LOADED

Check if secrets loaded correctly by adding this to `dashboard/app.py`:

```python
import streamlit as st
import os

# In your dashboard
if st.checkbox("Debug: Show Secrets"):
    st.write("API_URL:", os.getenv("API_URL", "NOT SET"))
    st.write("Secrets loaded:", bool(st.secrets.get("API_URL", None)))
```

---

## 🚀 AFTER ADDING SECRETS

1. **Verify connection**: 
   - Upload a file in dashboard
   - Check it connects to backend API

2. **Monitor logs**: 
   - Click **Manage app** → **Logs**
   - Look for API connection messages

3. **Test features**:
   - Problem detection
   - Reports generation
   - Chat functionality

---

## 📞 HELP

- Streamlit Secrets Docs: https://docs.streamlit.io/deploy/streamlit-cloud/manage-your-app/secrets-management
- Issue deploying? Check: `STREAMLIT_DEPLOYMENT_GUIDE.md`
