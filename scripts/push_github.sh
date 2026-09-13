#!/bin/bash
set -e
cd "$(dirname "$0")/.."

REPO="rpolicarpo100/APP_Teste"
BRANCH="main"

echo "🚀 Push para GitHub $REPO"

if [ -z "$GITHUB_TOKEN" ]; then
  echo "❌ GITHUB_TOKEN não definido"
  echo "Cria em https://github.com/settings/tokens/new (scope repo)"
  echo "Depois: export GITHUB_TOKEN=ghp_xxx"
  echo "Ou passa como arg: ./scripts/push_github.sh ghp_xxx"
  if [ ! -z "$1" ]; then
    GITHUB_TOKEN=$1
  else
    exit 1
  fi
fi

# Configura remote
git remote remove origin 2>/dev/null || true
git remote add origin https://$GITHUB_TOKEN@github.com/$REPO.git

# Garante branch main
git branch -M main

echo "📤 A fazer push para $REPO:$BRANCH..."
git push -u origin main -f

echo "✅ Push OK → https://github.com/$REPO"
echo "📦 Agora configura Fly.io secret:"
echo "  1. flyctl auth login"
echo "  2. flyctl tokens create deploy -x 999h"
echo "  3. Copia token → GitHub → $REPO → Settings → Secrets → FLY_API_TOKEN"
