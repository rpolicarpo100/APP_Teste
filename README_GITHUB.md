# APP_Teste — AI Brain GOD Cerebro Core

> GOD Cerebro Core + Local AI Brain — 8 agentes + 21 tools + Dashboard | Chat | Negócios | Definições

**Repo:** https://github.com/rpolicarpo100/APP_Teste

## 🚀 Deploy Live

- **Fly.io:** https://ai-brain-god.fly.dev/dashboard/ (após deploy)
- **Local:** http://localhost:8000/dashboard/
- **Swagger:** /docs

## 📦 Stack

- Python 3.11, FastAPI, SQLite, Ollama opcional
- 8 agentes: research, coding_qa, design, business, browser, automation, monitor, builder
- 21 tools: filesystem, web, python, scheduler, browser, site.builder, news.*, crypto.*, stocks.*, dashboard.*
- Frontend: 1 HTML 35KB, sem Node

## 🛠️ Teste rápido

```bash
docker-compose up --build
# http://localhost:8000/dashboard/
./scripts/test_deploy.sh http://localhost:8000
```

## 🌐 Fly.io Deploy (1 comando)

```bash
fly auth login
fly volumes create ai_brain_data --region mad --size 1
fly deploy
fly open
```

GitHub Actions auto-deploy configurado em `.github/workflows/fly-deploy.yml` — precisa secret `FLY_API_TOKEN`.

## 🔑 Secrets necessários (GitHub → Settings → Secrets)

- `FLY_API_TOKEN` — pega em https://fly.io/dashboard → Tokens

## 📊 Endpoints

- `/` — info
- `/health` — health
- `/system/status` — 8 agentes + 21 tools
- `/system/network` — grafo rede interna + KPIs + latência APIs externas REAL
- `/system/workspace-list` — ficheiros workspace
- `/businesses` — portfolio negócios
- `/dashboard/` — app leve
- `/docs` — Swagger

## 📁 Estrutura

```
app/
  api/ — system, chat, tasks, agents, memory, market, businesses
  brain/ — orchestrator, planner, scheduler, executor, router
  tools/ — registry + filesystem, web, python, scheduler, browser, site_builder, news, market_data
frontend/index.html — DASHBOARD | CHAT | NEGÓCIOS | DEFINIÇÕES
data/ — brain.db + workspace/
```

## 🔒 Chave deploy gerada

Chave SSH para deploy key em `deploy_key.pub` — adiciona em GitHub → Settings → Deploy keys

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILdrfjEZGo/w2M8fOpz4ZKJM0Hb1YSEoIIaQ6NYJnWx6 rpolicarpo100@ai-brain-deploy
```

## 📝 Licença

MIT — Local AI Brain, sem cloud, sem tokens pagos.
