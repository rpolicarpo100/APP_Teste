#!/bin/bash
set -e
cd "$(dirname "$0")/.."
echo "🚀 Deploy local — AI Brain GOD"
echo "=============================="

if [ ! -d ".venv" ]; then
  echo "Criando venv..."
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install -q -r requirements.txt

echo "✅ Deps OK"
echo "📁 Pastas..."
mkdir -p data/workspace data/documents data/logs data/memory

echo "🔍 Testes rápidos..."
python -m pytest tests/ -q || echo "⚠️ Alguns testes falharam, mas continua"

echo "🧠 A iniciar servidor em http://localhost:8000"
echo "📊 Dashboard: http://localhost:8000/dashboard/"
echo "📚 Docs: http://localhost:8000/docs"
echo "🌐 Network: http://localhost:8000/system/network"
echo ""
python -m app.main
