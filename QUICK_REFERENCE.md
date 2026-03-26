# 🚀 QUICK REFERENCE CARD - Localhost Links

## ⚡ TL;DR - Copy-Paste These Links

### Open in Browser (after starting services):

```
🎨 Streamlit Dashboard:
http://localhost:8501

📚 FastAPI API Docs:
http://localhost:8000/docs

✅ API Health Check:
http://localhost:8000/health

📊 Grafana Dashboards (optional):
http://localhost:3000
```

---

## ⚡ TL;DR - Copy-Paste These Commands

### Terminal 1 - Streamlit (then open http://localhost:8501):
```bash
cd /Users/amshumathshetty/Desktop/autonomous-ai-data-scientist
source venv/bin/activate
streamlit run dashboard/app.py
```

### Terminal 2 - FastAPI (then open http://localhost:8000/docs):
```bash
cd /Users/amshumathshetty/Desktop/autonomous-ai-data-scientist
source venv/bin/activate
python api/main.py
```

### All Services at Once (optional):
```bash
docker-compose -f /Users/amshumathshetty/Desktop/autonomous-ai-data-scientist/k8s/docker-compose.yml up -d
```

---

## 📋 What Each Link Does

| Link | Purpose | Command to Start |
|------|---------|------------------|
| `http://localhost:8501` | 🎨 Upload CSV, get predictions | `streamlit run dashboard/app.py` |
| `http://localhost:8000/docs` | 📚 Test API endpoints | `python api/main.py` |
| `http://localhost:8000/health` | ✅ Check API status | `python api/main.py` |
| `http://localhost:3000` | 📊 View dashboards | `docker-compose up -d` |

---

## ✅ Quick Test Checklist

After starting services, verify:

- [ ] http://localhost:8501 loads
- [ ] http://localhost:8000/docs loads
- [ ] http://localhost:8000/health returns `{"status": "ok"}`
- [ ] Can upload CSV in Streamlit
- [ ] Can see API endpoints in Swagger UI

---

## 🎯 Next Steps (After Testing)

1. ✅ Test locally (you're doing this now)
2. 📤 Push to GitHub `git push -u origin main`
3. 🔑 Add Gemini API integration
4. 🚀 Deploy to Streamlit Cloud

---

## 📚 Documentation Files

- `LOCALHOST_TEST_LINKS.md` ← Full testing guide
- `README.md` ← Project overview
- `GITHUB_PUSH_INSTRUCTIONS.md` ← How to push
- `DELIVERY_SUMMARY.md` ← What was delivered

---

**Current Status: Ready to Test! 🎉**
