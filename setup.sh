#!/bin/bash

# 🚀 Autonomous AI Data Scientist - Week 1 Setup Script
# Automates local development environment setup

set -e

echo "═══════════════════════════════════════════════════════════════"
echo "  🤖 Autonomous AI Data Scientist - Setup Script"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check Python
echo "✓ Checking Python installation..."
python3 --version || { echo "❌ Python 3 required. Install from python.org"; exit 1; }

# Check Ollama
echo "✓ Checking Ollama..."
if command -v ollama &> /dev/null; then
    echo "  ✅ Ollama found"
else
    echo "  ⚠️  Ollama not installed. Install from: https://ollama.ai"
    echo "     Then run: ollama serve (in separate terminal)"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Step 1: Create Virtual Environment"
echo "═══════════════════════════════════════════════════════════════"

if [ ! -d "venv" ]; then
    echo "Creating venv..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Step 2: Activate Virtual Environment"
echo "═══════════════════════════════════════════════════════════════"

source venv/bin/activate
echo "✅ Virtual environment activated"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Step 3: Install Dependencies"
echo "═══════════════════════════════════════════════════════════════"

pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "✅ Dependencies installed (45 packages)"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Step 4: Setup Environment"
echo "═══════════════════════════════════════════════════════════════"

if [ ! -f ".env" ]; then
    cp .env.local .env
    echo "✅ Created .env from .env.local (Ollama config)"
else
    echo "ℹ️  .env already exists"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  ✨ SETUP COMPLETE!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  🚀 Next Steps:"
echo ""
echo "  1. Terminal 1: Start Ollama"
echo "     $ ollama serve"
echo "     $ ollama pull mistral  (first time only)"
echo ""
echo "  2. Terminal 2: Start FastAPI"
echo "     $ python api/main.py"
echo "     📖 API Docs: http://localhost:8000/docs"
echo ""
echo "  3. Terminal 3: Start Streamlit"
echo "     $ streamlit run dashboard/app.py"
echo "     🎨 Dashboard: http://localhost:8501"
echo ""
echo "  4. Upload a CSV file at http://localhost:8501"
echo "     Use: data/examples/simple_classification.csv"
echo ""
echo "─────────────────────────────────────────────────────────────"
echo ""
echo "  📚 Documentation:"
echo "     • QUICKSTART.md  - 5-minute guide"
echo "     • README.md      - Full overview"
echo "     • DEVELOPMENT.md - Deep dive"
echo ""
echo "  🧪 Run tests:"
echo "     $ pytest tests/test_week1.py -v"
echo ""
echo "═══════════════════════════════════════════════════════════════"
