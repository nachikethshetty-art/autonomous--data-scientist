# 🚀 Quick Start Guide

## **5-Minute Local Setup (Ollama + Python)**

### Step 1: Clone & Install

```bash
cd /Users/amshumathshetty/Desktop/autonomous-ai-data-scientist

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Start Ollama

```bash
# Terminal 1: Start Ollama service
ollama serve

# Terminal 2: Pull Mistral model (first time only, ~4GB)
ollama pull mistral
```

Check it's working:
```bash
curl http://localhost:11434/api/tags
```

### Step 3: Start API & Dashboard

```bash
# Terminal 3: Start FastAPI backend
python api/main.py

# Terminal 4: Start Streamlit dashboard
streamlit run dashboard/app.py
```

### Access Points

- **Dashboard:** http://localhost:8501
- **API Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/health

### Step 4: Test Upload

**Via Dashboard:**
1. Go to http://localhost:8501
2. Upload any CSV file
3. System detects problem type automatically

**Via API:**
```bash
curl -X POST -F "file=@data/examples/iris.csv" \
  http://localhost:8000/api/v1/upload
```

Expected response:
```json
{
  "job_id": "a1b2c3d4",
  "filename": "iris.csv",
  "rows": 150,
  "cols": 5,
  "schema": {
    "sepal_length": {
      "detected_type": "numeric",
      "null_percentage": 0.0,
      "unique_values": 35
    }
  },
  "metadata": {
    "numeric_columns": ["sepal_length", "sepal_width"]
  }
}
```

---

## **Next Steps**

**Week 1 (Current):**
- ✅ Module 1: Data Ingestion (DONE)
- ✅ Module 3: Problem Detection (DONE)
- ⏳ Module 2: Business Context UI
- ⏳ Module 4: Airflow DAG integration

**Week 2:**
- Data Cleaning Agent
- EDA Engine (8 plots)
- Feature Engineering
- AutoML (4 models, 20 trials)

---

## **Troubleshooting**

### "Connection refused: http://localhost:11434"
```bash
# Make sure Ollama is running
ollama serve
# In another terminal:
ollama pull mistral
```

### "ModuleNotFoundError: No module named 'pandas'"
```bash
pip install -r requirements.txt
```

### "Port 8501 already in use"
```bash
streamlit run dashboard/app.py --server.port 8502
```

### Out of RAM?
- Close other applications
- M2 Air 8GB should be sufficient
- If issues: reduce Optuna trials in `.env`

---

## **Development Tips**

### Run Tests
```bash
pytest tests/ -v
```

### Check Logs
```bash
# API logs
tail -f api.log

# Streamlit logs
# Check terminal where streamlit is running
```

### Reset Everything
```bash
# Clear processed data
rm -rf data/processed/*

# Restart from scratch
rm data/jobs.db
```

### Use Gemini Instead (Production)
```bash
# Copy env template
cp .env.example .env

# Edit .env with your Gemini API key
export LLM_PROVIDER=gemini
python api/main.py
```

---

## **Architecture Overview**

```
User Upload CSV
    ↓
FastAPI /api/v1/upload
    ↓
DataValidator (SQLite job tracking)
    ↓
Schema Detection + Data Quality Checks
    ↓
LangGraph Problem Detection Agent
    ↓
Return: job_id + detected_problem_type + target_column
    ↓
Ready for Next Module (Week 2)
```

---

## **What's Each Module?**

| Week | Module | What It Does |
|------|--------|-------------|
| W1 | 1 | 📤 Upload CSV, validate, store metadata |
| W1 | 3 | 🤖 Auto-detect target column & problem type |
| W1 | 20 | 🔌 LLM provider wrapper (Ollama/Gemini) |
| W2 | 5 | 🧹 Clean data (nulls, outliers, scale) |
| W2 | 6 | 📊 Generate 8 EDA plots |
| W2 | 7 | ⚙️ Auto feature engineering |
| W2 | 8 | 🏆 Train 4 models with Optuna |
| W3 | 9 | 📈 Evaluate + ROC/F1/calibration curves |
| W3 | 10 | 💡 SHAP explainability |
| W3 | 14 | 💬 Chat with data (RAG) |
| W4 | 18 | 📄 Deploy + PDF report |
| W4 | 21 | 🎨 Streamlit 7-page dashboard |

---

## **Key Features Now (Week 1)**

✅ **Async CSV Upload** - Job queue system with unique IDs
✅ **Schema Detection** - Auto-infer data types
✅ **Problem Detection** - 2-stage (heuristics + LLM)
✅ **Data Validation** - 5 quality checks
✅ **SQLite Tracking** - Audit trail for every upload
✅ **API-First Design** - RESTful endpoints
✅ **LLM Agnostic** - Swap Ollama ↔ Gemini with env var

---

**Questions?** Check `/docs/ARCHITECTURE.md` (coming soon)
