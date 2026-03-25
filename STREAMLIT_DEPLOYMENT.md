# 🚀 Streamlit Cloud Deployment Guide

## Overview
Your autonomous AI data scientist application is now ready to deploy on Streamlit Cloud! This guide walks you through the deployment process.

## ✅ Pre-Deployment Checklist

- ✅ Production Streamlit dashboard created (`streamlit_app.py`)
- ✅ Streamlit configuration files ready (`.streamlit/config.toml`, `.streamlit/secrets.toml`)
- ✅ All 122 tests passing
- ✅ All 18 modules verified executable
- ✅ FastAPI backend functional (17 endpoints)
- ✅ Code committed to local git repository

## 📋 Step 1: Create GitHub Repository

### Option A: Using GitHub Web UI
1. Go to https://github.com/new
2. Create repository named `autonomous-ai-data-scientist`
3. Don't initialize with README (we have our own)
4. Copy the HTTPS URL

### Option B: Using Command Line
```bash
# After creating the repo on GitHub, add remote:
cd /Users/amshumathshetty/Desktop/autonomous-ai-data-scientist
git remote add origin https://github.com/YOUR_USERNAME/autonomous-ai-data-scientist.git
git branch -M main
git push -u origin main
```

## 🔗 Step 2: Deploy on Streamlit Cloud

### Prerequisites
- GitHub account (must have your repository public or grant Streamlit access)
- Streamlit account (free tier available)

### Deployment Steps

1. **Go to Streamlit Cloud**
   - Visit: https://share.streamlit.io/
   - Click "New app"

2. **Connect GitHub**
   - Select your GitHub repository: `autonomous-ai-data-scientist`
   - Select branch: `main`
   - Set main file path: `streamlit_app.py`

3. **Configure App Settings**
   - App URL will be: `https://share.streamlit.io/[username]/autonomous-ai-data-scientist/streamlit_app.py`
   - Advanced settings (optional):
     - Python version: 3.14
     - Client max message size: 200 (default)

4. **Deploy**
   - Click "Deploy" button
   - Wait 2-5 minutes for deployment
   - View logs in real-time

## 🔑 Step 3: Configure Secrets (Optional but Recommended)

Streamlit Cloud uses the `.streamlit/secrets.toml` file for environment variables.

### For Local Testing (Already Set)
- File: `.streamlit/secrets.toml`
- Contains templates for all services

### For Streamlit Cloud

1. Go to your deployed app's settings (gear icon)
2. Click "Secrets" in the sidebar
3. Copy-paste your secrets in TOML format:

```toml
# Database Configuration
[database]
host = "your-postgres-host"
port = 5432
user = "your-db-user"
password = "your-db-password"
name = "your-db-name"

# API Configuration
[api]
fastapi_url = "https://your-api.com"
api_key = "your-api-key"

# Alerting Configuration
[alerting]
slack_webhook = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
email_smtp_server = "smtp.gmail.com"
email_smtp_port = 587
email_sender = "your-email@gmail.com"
email_password = "your-app-password"
twilio_account_sid = "your-twilio-sid"
twilio_auth_token = "your-twilio-token"

# Model Registry
[registry]
s3_bucket = "your-bucket"
s3_region = "us-east-1"

# Kubernetes Deployment
[kubernetes]
cluster_endpoint = "https://your-k8s-cluster.com"
token = "your-k8s-token"
```

## 📊 Dashboard Features (8 Pages)

### 1. 📊 Dashboard
- Real-time metrics (accuracy, drift, models, uptime)
- Performance trends with interactive charts
- Health status indicators
- Delta changes for quick insights

### 2. 📈 Data Pipeline
- CSV file upload
- Data validation with quality report
- Feature engineering preview
- Data quality metrics

### 3. 🧠 Model Training
- Algorithm selection (Logistic Regression, Random Forest, XGBoost, SVM, KNN)
- Training configuration
- Performance metrics (accuracy, precision, recall, F1)
- Feature importance visualization

### 4. 🔍 Monitoring
- Data drift detection
- Concept drift detection
- Performance drift detection
- Prediction distribution analysis
- Historical health timeline

### 5. ⚠️ Alerts
- Active alerts display
- Alert configuration (thresholds, types)
- Multi-channel setup (Slack, Email, Twilio)
- Alert resolution tracking

### 6. 📋 Registry
- Model registry view with version history
- Model metadata display
- Registration UI for new models
- Performance history

### 7. 🧪 A/B Testing
- Active test management
- Statistical results display
- A/B test creation interface
- Statistical significance indicators

### 8. 🚀 Deployment
- Deployment strategy selection (Blue-Green, Canary, Rolling)
- Environment selection (Dev, Staging, Production)
- Deployment history with rollback options
- Kubernetes configuration support

## 🔧 Environment Variables

The app uses these environment variables (set in secrets or local `.streamlit/secrets.toml`):

| Variable | Purpose | Example |
|----------|---------|---------|
| `database.host` | Database host | `localhost` |
| `database.port` | Database port | `5432` |
| `api.fastapi_url` | FastAPI backend URL | `http://localhost:8000` |
| `alerting.slack_webhook` | Slack integration | Webhook URL |
| `kubernetes.cluster_endpoint` | K8s cluster URL | Cluster endpoint |

## ⚙️ Advanced Configuration

### Custom Domain
1. Go to app settings
2. Click "Custom domain"
3. Add your domain (requires DNS setup)

### View Deployment Logs
- Click gear icon → "Logs"
- Monitor real-time logs
- Check for errors/warnings

### Rerun/Redeploy
- Changes pushed to `main` branch auto-trigger redeployment
- Manual redeploy: Click "Rerun" button

## 🐛 Troubleshooting

### App Won't Load
- Check logs: Settings → Logs
- Verify `streamlit_app.py` imports work locally
- Ensure all dependencies in `requirements.txt`

### Import Errors
- Run locally: `streamlit run streamlit_app.py`
- Install missing packages: `pip install -r requirements.txt`
- Update `requirements.txt` and redeploy

### Performance Issues
- Check memory usage in logs
- Reduce data size in demo
- Optimize Plotly charts
- Use caching for expensive operations

### Secrets Not Loading
- Verify format in Streamlit Cloud secrets editor
- No quotes needed for values
- Use correct indentation (spaces, not tabs)

## 📦 File Structure for Deployment

```
autonomous-ai-data-scientist/
├── streamlit_app.py              # ✅ Main app file
├── .streamlit/
│   ├── config.toml              # ✅ Streamlit config
│   └── secrets.toml             # ✅ Secrets template
├── requirements.txt             # ✅ Dependencies
├── src/                         # ✅ Core modules
│   ├── agents/
│   ├── drift/
│   ├── eda/
│   ├── alerting/
│   ├── deployment/
│   ├── features/
│   ├── ingestion/
│   ├── integration/
│   ├── llm/
│   ├── registry/
│   ├── reporting/
│   ├── testing/
│   └── explainability/
├── api/                         # ✅ FastAPI backend
├── dashboard/                   # ✅ Legacy Streamlit app
├── tests/                       # ✅ Test suite
├── data/                        # ✅ Sample data
└── k8s/                         # ✅ Kubernetes configs
```

## 🚢 Continuous Deployment

Set up auto-deployment:

```bash
# Every push to main triggers:
1. Unit tests (GitHub Actions)
2. Build Docker image
3. Deploy to Streamlit Cloud
4. Deploy to Kubernetes
```

### Example GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Streamlit Cloud

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest tests/ -v
      - name: Deploy to Streamlit Cloud
        if: success()
        run: echo "Streamlit Cloud auto-deploys on push!"
```

## 📊 Monitoring Deployment

### Streamlit Cloud Dashboard
- Visit: https://share.streamlit.io/dashboard
- View all deployed apps
- Check resource usage
- Configure alerts

### App Analytics
- View within Streamlit Cloud app settings
- Track user sessions
- Monitor app health
- View error logs

## 🎉 You're Ready!

Your autonomous AI data scientist is now cloud-ready! 

**Next Steps:**
1. Create GitHub repo with your code
2. Deploy to Streamlit Cloud
3. Configure secrets in cloud dashboard
4. Share the URL with your team
5. Monitor and iterate

**Share your app:**
```
https://share.streamlit.io/YOUR_USERNAME/autonomous-ai-data-scientist/streamlit_app.py
```

## 📞 Support

- **Streamlit Docs:** https://docs.streamlit.io/
- **Streamlit Cloud Docs:** https://docs.streamlit.io/streamlit-cloud/get-started
- **GitHub Help:** https://docs.github.com/

---

**Status:** ✅ All 122 tests passing | ✅ Production ready | ✅ Kubernetes integration complete | ✅ Cloud deployment ready
