# Deploy — AI Brain GOD Cerebro Core

Guia rápido para testar melhor fora do sandbox Arena.

## 1. Preview Atual (já a funcionar)
O servidor já está em deploy de teste:
- **Porta 8000** → https://8000-xxx.e2b.app (preview Arena)
- Endpoints: `/dashboard/`, `/health`, `/system/network`, `/businesses`, `/docs`

Faz `Ctrl+Shift+R` para ver última versão com rede visual + dados reais.

## 2. Docker Local (recomendado para teste rápido)

```bash
cd ai-brain
docker-compose up --build
# abre http://localhost:8000/dashboard/
# API docs http://localhost:8000/docs
```

Testar saúde:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/system/network | jq
```

## 3. Docker puro

```bash
docker build -t ai-brain-god .
docker run -p 8000:8000 -v $(pwd)/data:/app/data ai-brain-god
```

## 4. Fly.io (deploy público barato, região Madrid)

```bash
# Instala flyctl https://fly.io/docs/hands-on/install-flyctl/
fly auth login
fly launch --no-deploy # usa fly.toml já criado
fly volumes create ai_brain_data --region mad --size 1
fly deploy
fly open
```

URL final: `https://ai-brain-god.fly.dev/dashboard/`

## 5. Render (1 clique, free tier)

1. Push para GitHub
2. Vai a https://dashboard.render.com → New Web Service
3. Conecta repo, usa `render.yaml` (auto detectado)
4. Deploy → URL: `https://ai-brain-god.onrender.com/dashboard/`

Ou usa botão:
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## 6. Railway

```bash
railway init
railway up
```

## 7. Teste local sem Docker

```bash
python -m venv .venv
source .venv/bin/activate # ou .venv\Scripts\activate no Windows
pip install -r requirements.txt
python -m app.main
# abre http://localhost:8000/dashboard/
```

## 8. Variáveis .env para produção

Copia `.env.example` para `.env`:

```
APP_ENV=production
APP_HOST=0.0.0.0
APP_PORT=8000
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=qwen3:8b
AUTONOMY_LEVEL=2
SECRET_KEY=gera-uma-chave-forte-aqui
CORS_ORIGINS=*
```

## 9. Checklist deploy

- [ ] `/health` retorna `{"status":"ok"}`
- [ ] `/system/network` mostra 8 agentes + 21 tools
- [ ] `/dashboard/` carrega sem erros JS (F12 console)
- [ ] NEGÓCIOS só tem 2 cards (Modelo + Missões) — sem calculadora
- [ ] DEFINIÇÕES → Network + KPIs mostra grafo visual 🕸️
- [ ] DEFINIÇÕES → Dados mostra workspace files + botão actualizar
- [ ] `/businesses` retorna 4 negócios teste
- [ ] `/docs` Swagger funciona

## 10. Debug

```bash
# Logs Docker
docker logs -f ai-brain-god

# Logs Fly
fly logs

# Test endpoints
./scripts/test_deploy.sh https://sua-url.fly.dev
```

## 11. Segurança produção

- Muda `SECRET_KEY`
- `ALLOW_PYTHON_EXEC=false` (default)
- `AUTONOMY_LEVEL=2` para testes, `1` para produção restrita
- `CORS_ORIGINS=https://teu-dominio.com` em vez de `*`
- Volume `data/` persistente — senão perdes brain.db a cada deploy
