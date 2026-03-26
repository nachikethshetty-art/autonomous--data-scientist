# 🌐 LOCALHOST TEST LINKS - Open These in Your Browser

## ✅ Services Ready to Test

Once you run the services below, use these exact links:

### 🎯 **MAIN SERVICES** (Start These First)

#### 1️⃣ **Streamlit Dashboard** - Interactive Web UI
```
http://localhost:8501
```
**What to expect:** 
- Upload CSV files
- Ask business questions
- See ML results, visualizations, and metrics
- Interactive charts and predictions

**To start:**
```bash
cd /Users/amshumathshetty/Desktop/autonomous-ai-data-scientist
source venv/bin/activate
streamlit run dashboard/app.py
```

---

#### 2️⃣ **FastAPI REST API** - Backend API with Auto Documentation
```
http://localhost:8000/docs
```
**What to expect:**
- Interactive API documentation (Swagger UI)
- 17 endpoints to test
- Try API calls directly in browser
- See request/response schemas

**Alternative (plain API):**
```
http://localhost:8000
```

**To start (new terminal):**
```bash
cd /Users/amshumathshetty/Desktop/autonomous-ai-data-scientist
source venv/bin/activate
python api/main.py
```

---

### 📊 **MONITORING & METRICS** (Optional - with Docker Compose)

#### 3️⃣ **Prometheus** - Metrics Collection
```
http://localhost:9090
```
**What to expect:**
- Real-time metrics graphs
- Query metrics (CPU, memory, requests)
- Alert rules configuration

**To start (requires Docker Compose):**
```bash
cd /Users/amshumathshetty/Desktop/autonomous-ai-data-scientist
docker-compose -f k8s/docker-compose.yml up -d
```

---

#### 4️⃣ **Grafana** - Visual Dashboards
```
http://localhost:3000
```
**Credentials:**
- Username: `admin`
- Password: `admin`

**What to expect:**
- Beautiful monitoring dashboards
- Pre-built panels for ML metrics
- Real-time data visualization

---

## 🚀 QUICK START (3 Steps to Test Everything)

### Step 1: Open Terminal 1 - Start Streamlit Dashboard
```bash
cd /Users/amshumathshetty/Desktop/autonomous-ai-data-scientist
source venv/bin/activate
streamlit run dashboard/app.py
```
**Wait for:** "You can now view your Streamlit app in your browser"
**Then open:** http://localhost:8501

---

### Step 2: Open Terminal 2 - Start FastAPI
```bash
cd /Users/amshumathshetty/Desktop/autonomous-ai-data-scientist
source venv/bin/activate
python api/main.py
```
**Wait for:** "Uvicorn running on http://0.0.0.0:8000"
**Then open:** http://localhost:8000/docs

---

### Step 3: Test All Services
Open these links in your browser:

| Service | URL | Purpose |
|---------|-----|---------|
| **Streamlit** | http://localhost:8501 | 🎨 Upload data & get predictions |
| **FastAPI Docs** | http://localhost:8000/docs | 📚 Test API endpoints |
| **API Health** | http://localhost:8000/health | ✅ Check API status |

---

## 📋 WHAT TO TEST ON EACH SERVICE

### On Streamlit (http://localhost:8501)
1. ✅ Page loads
2. ✅ Can see upload interface
3. ✅ Can select example datasets
4. ✅ Can input business question
5. ✅ Can view generated predictions

### On FastAPI (http://localhost:8000/docs)
1. ✅ Swagger UI loads
2. ✅ Can see all 17 endpoints
3. ✅ Can test GET /health endpoint
4. ✅ Can try POST /predict endpoint
5. ✅ Can see request/response schemas

### On Prometheus (http://localhost:9090) - Optional
1. ✅ Metrics dashboard loads
2. ✅ Can view system metrics
3. ✅ Can query metrics with PromQL

### On Grafana (http://localhost:3000) - Optional
1. ✅ Login with admin/admin
2. ✅ Can see dashboards
3. ✅ Can view real-time graphs

---

## 🔗 DIRECT LINKS (Copy-Paste Ready)

### Primary Links (Must Have)
```
Streamlit Dashboard:
http://localhost:8501

FastAPI Swagger UI:
http://localhost:8000/docs

FastAPI Plain:
http://localhost:8000
```

### Health Check Links
```
FastAPI Health:
http://localhost:8000/health

API Metadata:
http://localhost:8000/metadata
```

### Monitoring Links (Optional)
```
Prometheus:
http://localhost:9090

Grafana:
http://localhost:3000

Prometheus Targets:
http://localhost:9090/targets

Grafana Dashboards:
http://localhost:3000/d/ml-monitoring
```

---

## ⚡ FULL DOCKER COMPOSE SETUP (All Services)

If you want to start all 8 services at once:

```bash
cd /Users/amshumathshetty/Desktop/autonomous-ai-data-scientist
docker-compose -f k8s/docker-compose.yml up -d
```

**Services Started:**
```
✅ Streamlit:    http://localhost:8501
✅ FastAPI:      http://localhost:8000
✅ Prometheus:   http://localhost:9090
✅ Grafana:      http://localhost:3000
✅ PostgreSQL:   localhost:5432
✅ Redis:        localhost:6379
✅ Ollama:       http://localhost:11434
✅ Airflow:      http://localhost:8080
```

**To stop all services:**
```bash
docker-compose -f k8s/docker-compose.yml down
```

---

## 🎯 TEST WORKFLOW

### Best Way to Test Locally:

**Terminal 1 - Streamlit:**
```bash
source venv/bin/activate
streamlit run dashboard/app.py
```
Open: http://localhost:8501

**Terminal 2 - FastAPI:**
```bash
source venv/bin/activate
python api/main.py
```
Open: http://localhost:8000/docs

**Then:**
1. Upload a CSV in Streamlit
2. Ask a business question
3. See predictions generated
4. Test API endpoints in FastAPI Swagger UI

---

## 📝 EXAMPLE TEST DATA

Sample datasets are in:
```
data/examples/
├── house_prices.csv
└── simple_classification.csv
```

Use these for testing in Streamlit.

---

## ✅ CHECKLIST - EVERYTHING WORKING

After starting services, verify:

- [ ] http://localhost:8501 loads (Streamlit)
- [ ] http://localhost:8000/docs loads (FastAPI)
- [ ] http://localhost:8000/health returns `{"status": "ok"}`
- [ ] Can upload CSV in Streamlit
- [ ] Can see API endpoints in Swagger UI
- [ ] Tests pass: `pytest tests/ -v`

---

## 🚨 TROUBLESHOOTING

**Port Already in Use?**
```bash
# Find process using port 8501
lsof -i :8501

# Kill it if needed
kill -9 <PID>

# Or use different port
streamlit run dashboard/app.py --server.port 8502
```

**Streamlit Not Connecting?**
```bash
# Restart Streamlit
streamlit run dashboard/app.py --logger.level=debug
```

**FastAPI Not Starting?**
```bash
# Check if port 8000 is free
lsof -i :8000

# Try different port
python api/main.py --port 8001
```

**Virtual Environment Issues?**
```bash
# Reactivate venv
source venv/bin/activate

# Install dependencies again
pip install -r requirements.txt
```

---

## 🎉 ONCE EVERYTHING WORKS

All localhost tests pass ✅ 
→ Ready for next step: **Add Gemini API integration**

---

**Current Status: Ready to Test! Open the links above in your browser now.** 🚀
