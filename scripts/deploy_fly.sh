#!/bin/bash
set -e
cd "$(dirname "$0")/.."
export FLYCTL_INSTALL="/home/user/.fly"
export PATH="$FLYCTL_INSTALL/bin:$PATH"

if [ -z "$FLY_API_TOKEN" ]; then
  echo "❌ FLY_API_TOKEN não definido"
  echo "Cria em https://fly.io/dashboard → Tokens"
  echo "export FLY_API_TOKEN=fo1_xxx"
  echo "Ou faz login: flyctl auth login"
fi

echo "🚀 Deploy Fly.io — ai-brain-god"
echo "================================"

# Verifica se app existe, se não cria
flyctl apps list | grep ai-brain-god || flyctl apps create ai-brain-god --org personal || true

# Cria volume se não existe
flyctl volumes list | grep ai_brain_data || flyctl volumes create ai_brain_data --region mad --size 1 -y || true

# Deploy
flyctl deploy --remote-only

echo "✅ Deploy OK"
flyctl status
flyctl open || echo "Abre https://ai-brain-god.fly.dev/dashboard/"
