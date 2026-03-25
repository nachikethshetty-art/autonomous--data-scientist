# 🤖 Autonomous AI Data Scientist

> **Production-grade AutoML system that behaves like a senior data scientist + ML engineer**

User uploads CSV → answers one business question → system automatically detects the problem, cleans data, engineers features, trains models, explains predictions, detects drift, and deploys.

**[Live Demo](https://your-deployment-url)** | **[Documentation](./docs/)** | **[Quick Start](#-quick-start)**

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Production%20Ready-green?style=flat-square)](https://fastapi.tiangolo.com)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-k3d-326CE5?style=flat-square)](https://k3d.io)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-In%20Development-yellow?style=flat-square)]()

---

## 📊 Architecture at a Glance

```
CSV Upload
    ↓
Data Validation & Ingestion (FastAPI async)
    ↓
Business Context Prompt (Streamlit)
    ↓
Auto Problem Detection Agent (LangGraph)
    ↓
Airflow DAG Orchestration
    ↓
Cleaning Agent → EDA → Features → AutoML (4 models, 20 trials)
    ↓
Evaluation → SHAP Explainability → Multi-Agent Insights
    ↓
Drift Detection → Report → Deployment (FastAPI endpoint)
    ↓
Chat With Data (RAG + Gemini/Ollama)
```

---

## ✨ Key Features

| Feature | Details |
|---------|---------|
| **🤖 Multi-Agent System** | Problem detection, cleaning, insights, critique agents (LangGraph) |
| **🔍 Auto Problem Detection** | Heuristics + LLM identifies classification/regression + target column |
| **🧹 Intelligent Cleaning** | Missing values, outliers, scaling with full audit log |
| **📊 EDA Automation** | 8 auto-generated plots + statistical analysis |
| **⚙️ AutoML** | 4 models + Optuna 20 trials, 2-3 min training |
| **📈 Deep Evaluation** | Accuracy, F1, ROC-AUC, calibration curves, residual plots |
| **💡 Explainability** | SHAP + plain-English explanations via Gemini/Ollama |
| **🎯 Validated Insights** | Insight + Critique agents with feedback loops |
| **💬 Chat With Data** | RAG-based QA on your dataset (ChromaDB + LLM) |
| **⚠️ Drift Detection** | Evidently AI monitors data/model drift automatically |
| **🚀 Async Pipeline** | Job queue with real-time progress tracking |
| **🐳 Kubernetes Ready** | k3d manifests for production deployment |
| **🛠️ Provider Agnostic** | Swap Ollama ↔ Gemini with one env var |

---

## 🚀 Quick Start

### Option 1: Local Development (Ollama)

**Prerequisites:**
- Python 3.11+
- Ollama running locally
- M2/M3 Mac or Linux with 8GB+ RAM

**Setup:**
```bash
# Clone & setup
git clone https://github.com/yourusername/autonomous-ai-data-scientist.git
cd autonomous-ai-data-scientist

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Ollama
ollama serve
# In another terminal: ollama pull mistral

# Copy local env
cp .env.local .env

# Start services
# Terminal 1: API
python api/main.py

# Terminal 2: Dashboard
streamlit run dashboard/app.py

# Terminal 3: MLflow
mlflow ui

# Upload CSV at http://localhost:8501
```

### Option 2: Docker Compose

```bash
docker-compose up -d
# Access:
# Dashboard: http://localhost:8501
# API: http://localhost:8000
# MLflow: http://localhost:5000
# Airflow: http://localhost:8080
```

### Option 3: Kubernetes (Production)

```bash
# Install k3d
curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash

# Create cluster
k3d cluster create autonomous-ds --agents 2

# Deploy
kubectl apply -f k8s/

# Port forward
kubectl port-forward svc/api 8000:8000
kubectl port-forward svc/streamlit 8501:8501
kubectl port-forward svc/mlflow 5000:5000
```

---

## 📁 Project Structure

```
autonomous-ai-data-scientist/
├── data/
│   ├── raw/
│   ├── processed/
│   └── examples/               # Demo datasets
├── src/
│   ├── ingestion/              # Module 1: Data ingestion & validation
│   ├── agents/                 # Modules 3,5,11,12: Problem detection, cleaning, insights
│   ├── eda/                    # Module 6: EDA engine
│   ├── features/               # Module 7: Feature engineering
│   ├── models/                 # Module 8,9: AutoML trainer & evaluator
│   ├── explainability/         # Module 10: SHAP explainability
│   ├── llm/                    # Module 20: Provider-agnostic LLM wrapper
│   ├── drift/                  # Module 13: Drift detection
│   ├── reporting/              # Module 17: PDF report generation
│   └── pipeline/               # Orchestration helpers
├── airflow/dags/               # Module 4: Airflow DAG
├── api/                        # Module 18: FastAPI endpoints
├── dashboard/                  # Module 21: Streamlit dashboard
├── k8s/                        # Module 22: Kubernetes manifests
├── tests/                      # Module 22: Pytest suite
├── docker-compose.yml          # Local dev orchestration
├── Dockerfile                  # Container image
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

---

## 🧠 22 Modules Overview

| # | Module | Status | Week |
|---|--------|--------|------|
| 1 | Data Ingestion & Validation | ⏳ | W1 |
| 2 | Business Context Prompt | ⏳ | W1 |
| 3 | Auto Problem Detection Agent | ⏳ | W1 |
| 4 | Airflow Pipeline Orchestration | ⏳ | W1 |
| 5 | Cleaning Agent (LangGraph) | ⏳ | W2 |
| 6 | EDA Engine | ⏳ | W2 |
| 7 | Feature Engineering | ⏳ | W2 |
| 8 | AutoML Trainer | ⏳ | W2 |
| 9 | Deep Evaluation | ⏳ | W3 |
| 10 | SHAP Explainability | ⏳ | W3 |
| 11 | Insight Agent (LangGraph) | ⏳ | W3 |
| 12 | Critique Agent (LangGraph) | ⏳ | W3 |
| 13 | Drift Detection | ⏳ | W3 |
| 14 | Chat With Data (RAG) | ⏳ | W3 |
| 15 | MLflow Experiment Tracking | ⏳ | W4 |
| 16 | DVC Data Versioning | ⏳ | W4 |
| 17 | Async Job Queue | ⏳ | W4 |
| 18 | PDF Report Generation | ⏳ | W4 |
| 19 | FastAPI Endpoints | ⏳ | W4 |
| 20 | Provider-Agnostic LLM Wrapper | ⏳ | W1 |
| 21 | Streamlit Dashboard | ⏳ | W4 |
| 22 | Docker + K8s + Tests + CI | ⏳ | W4 |

---

## 🎯 For AI Product Companies

**Key Selling Points:**
- ✅ Multi-agent orchestration (LangGraph)
- ✅ Real-time streaming responses
- ✅ Provider-agnostic LLM wrapper
- ✅ Kubernetes-ready production architecture
- ✅ Explainable AI (SHAP + plain English)

**What we emphasize:**
- Agent loops and feedback mechanisms
- Production readiness
- Scalability (M2 → Cloud)

---

## ⚡ For Energy Sector

**Key Selling Points:**
- ✅ Drift detection for compliance
- ✅ Time-series forecasting (demand/price)
- ✅ Explainable predictions (stakeholder trust)
- ✅ Automated retraining triggers
- ✅ Full audit trails

**What we emphasize:**
- Regulatory compliance features
- Domain-specific insights
- Reliability and monitoring

---

## 🗓️ Build Timeline

| Week | Modules | Deliverable |
|------|---------|-------------|
| **Week 1** | 1-4, 20 | Data pipeline + Problem detection + Airflow DAG |
| **Week 2** | 5-8 | Cleaning + EDA + Features + AutoML (trains in 2-3 min) |
| **Week 3** | 9-14 | Evaluation + SHAP + Insights + Drift + Chat |
| **Week 4** | 15-22 | MLflow + DVC + API + Dashboard + K8s + Tests |

---

## 📚 Documentation

- [Architecture Design](./docs/ARCHITECTURE.md) - Coming soon
- [Module Specifications](./docs/MODULES.md) - Coming soon
- [API Reference](./docs/API.md) - Coming soon
- [Deployment Guide](./docs/DEPLOYMENT.md) - Coming soon

---

## 🤝 Contributing

Contributions welcome! Please see [CONTRIBUTING.md](./CONTRIBUTING.md)

---

## 📄 License

MIT License - See [LICENSE](./LICENSE)

---

## 👨‍💻 Author

Built by Nachiketh Shetty as a comprehensive AutoML demonstration for ML engineering interviews.

**Status:** 🚀 In Active Development (Week 1/4)
