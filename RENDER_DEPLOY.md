# Render Deploy — APP_Teste (AI Brain GOD) — 1 clique

**Repo:** https://github.com/rpolicarpo100/APP_Teste

## 🚀 Deploy 1-clique (recomendado)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/rpolicarpo100/APP_Teste)

Clica no botão acima → faz login GitHub → Render cria serviço automaticamente usando `render.yaml`.

**O que o `render.yaml` faz:**
- Região: Frankfurt (perto de Lisboa, baixa latência)
- Build: `pip install -r requirements.txt`
- Start: `python -m app.main` (lê PORT=10000 automaticamente)
- Healthcheck: `/health`
- Disk persistente: 1GB em `/opt/render/project/src/data` para `brain.db` + `workspace/`
- Env: `APP_ENV=production`, `PYTHON_VERSION=3.11.0`

## 📋 Passo-a-passo manual (se botão não funcionar)

1. Vai a https://dashboard.render.com → **New + → Web Service**
2. **Connect** GitHub → seleciona `rpolicarpo100/APP_Teste` → Connect
3. Config:
   - Name: `ai-brain-god`
   - Region: Frankfurt
   - Branch: main
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python -m app.main`
   - Plan: Starter (free 750h/mês) ou Free
4. **Environment Variables:**
   - `APP_ENV=production`
   - `APP_HOST=0.0.0.0`
   - `PORT=10000` (Render já define, mas confirma)
   - `PYTHON_VERSION=3.11.0`
   - `AUTONOMY_LEVEL=2`
5. **Disk (importante para não perder dados):**
   - Add Disk → Name: `ai-brain-data` → Mount Path: `/opt/render/project/src/data` → Size: 1GB
6. **Create Web Service** → aguarda build ~3-5 min
7. URL final: `https://ai-brain-god-xxxx.onrender.com`

## 🔍 Testar deploy Render

Após deploy, testa:

```bash
# Substitui pela tua URL Render
export RENDER_URL=https://ai-brain-god-xxxx.onrender.com

./scripts/test_deploy.sh $RENDER_URL
```

Deve dar:
```
→ Root... ✅ 200
→ Health... ✅ 200
→ System Status... ✅ 200 (8 agentes 21 tools)
→ Network... ✅ 200
→ Negócios... ✅ 200
→ Dashboard HTML... ✅ 200
Agentes: 8 ✅ Tools: 21 ✅
```

Abre no browser:
- Dashboard: `$RENDER_URL/dashboard/`
- Docs: `$RENDER_URL/docs`
- Health: `$RENDER_URL/health`
- Network: `$RENDER_URL/system/network`

## 🛠️ Troubleshooting Render

**Build falha:**
- Verifica `requirements.txt` — já tem fastapi, uvicorn, etc.
- Logs: Render Dashboard → Logs

**App crash no start:**
- Verifica Start Command é `python -m app.main`
- Verifica PORT env — app lê `PORT` ou `APP_PORT` (já corrigido com `effective_port`)

**DB perde dados a cada deploy:**
- Sem disk, Render apaga `data/` a cada deploy. Solução: Add Disk como acima.

**Free tier dorme:**
- Render free dorme após 15 min inativo → primeiro request demora 30s a acordar. Normal.

## 💾 Persistência

Com disk configurado, `data/brain.db` persiste entre deploys. Sem disk, perde tudo.

Para backup:
```bash
curl https://sua-url.onrender.com/system/export-all -o backup.json
```

## 🔄 Auto deploy

A cada `git push` para `main`, Render faz deploy automático (se ligado GitHub).

Desliga em Render → Settings → Auto-Deploy: No (se quiser manual).

## 📊 Diferença vs Fly.io

- Render: Frankfurt, 750h free, disk 1GB free, dorme após 15 min
- Fly.io: Madrid, 3 VMs free, volume 1GB, não dorme se min_machines_running=1
- Para teste, Render é mais simples (sem flyctl)

## ✅ Checklist pós-deploy

- [ ] `/health` retorna `{"status":"ok"}`
- [ ] `/system/network` → 8 agentes + 21 tools + 4/4 external OK
- [ ] `/dashboard/` carrega sem erro JS
- [ ] NEGÓCIOS só 2 cards (Modelo + Missões)
- [ ] DEFINIÇÕES → Network → grafo visual 🕸️ aparece
- [ ] DEFINIÇÕES → Dados → workspace files + actualizar funciona

Pronto para testar melhor!
