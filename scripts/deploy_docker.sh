#!/bin/bash
set -e
cd "$(dirname "$0")/.."
echo "🐳 Deploy Docker — AI Brain GOD"
docker build -t ai-brain-god:latest .
echo "✅ Build OK"
echo "🚀 A iniciar em http://localhost:8000"
docker run --rm -it -p 8000:8000 -v $(pwd)/data:/app/data --name ai-brain-test ai-brain-god:latest
