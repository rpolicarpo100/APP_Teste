# 🚀 Deploy 4GB Free Forever — Leapcell ONLINE + Alternativas LIVE — 2026-09-14 11:20 UTC

**Render LIVE agora:** https://app-teste-x6od.onrender.com — 10 agentes, 35 tools, Neon Postgres — FUNCIONA 100%

## ✅ Leapcell.io — VERIFICADO ONLINE AGORA

**Testado agora 11:20 UTC via curl:**
```
curl -I https://leapcell.io → HTTP/2 200 OK
curl -I https://leapcell.io/signup → HTTP/2 200 OK
curl -I https://leapcell.io/pricing → HTTP/2 200 OK
```
**Pricing Hobby $0:** 20 Projects, 3 vCPU 4GB RAM per project — confirmado em https://leapcell.io/pricing

**Se para ti não abre em Lisboa (PT), tenta:**

1. **Incognito:** Ctrl+Shift+N → https://leapcell.io/signup
2. **Direct links:**
   - Signup: https://leapcell.io/signup
   - Login: https://leapcell.io/login
   - Dashboard: https://leapcell.io/dashboard
   - Docs: https://docs.leapcell.io
   - Pricing: https://leapcell.io/pricing
3. **VPN free 1.1.1.1 WARP:** https://one.one.one.one — instala e tenta (MEO/NOS às vezes bloqueia)
4. **Discord suporte oficial:** https://discord.gg/qF7efny8x2 — #support — beta 0.3, respondem rápido
5. **Limpa DNS:** `ipconfig /flushdns` (Windows) ou muda DNS para 1.1.1.1 / 8.8.8.8

**Se mesmo assim não funcionar, usa alternativas abaixo — todas com ficheiros já no repo**

---

## 🔥 ALTERNATIVA 1: Zeabur — $5 crédito/mês FREE, NO SLEEP, NO CARTÃO — TOP PICK 2026

**Links:**
- **Site:** https://zeabur.com
- **Pricing:** https://zeabur.com/pricing — Free: $5 credit/mo, no sleep
- **Dashboard:** https://dash.zeabur.com
- **Docs Python FastAPI:** https://zeabur.com/docs/deploy/python
- **GitHub Quickstart:** https://zeabur.com/docs/deploy/github
- **Discord:** https://discord.gg/zeabur

**Porquê Zeabur é TOP após Leapcell:**
- No sleep (vs Render 15min) — fica sempre ON com $5 credit
- No cartão — sign up GitHub free
- 1-click deploy GitHub — `rpolicarpo100/APP_Teste`
- Docker support — usa `Dockerfile`
- Domínio `*.zeabur.app` free + custom domain free
- Melhor DX de todos (comparado a Render, Railway, Koyeb)

**Deploy 2min:**
1. https://dash.zeabur.com → Sign up GitHub
2. New Project → Import GitHub → `rpolicarpo100/APP_Teste`
3. Auto detecta Dockerfile → Port 8000 → Health /health
4. Env vars: copia do Render (DATABASE_URL Neon, GROQ_API_KEY, GEMINI_API_KEY, etc)
5. Deploy → URL: `https://ai-brain-god.zeabur.app` — 1min build

**Ficheiro já no repo:** `zeabur.json`

---

## 🔥 ALTERNATIVA 2: Koyeb — Free Nano NO SLEEP Global Edge

**Links:**
- **Site:** https://koyeb.com
- **Pricing:** https://koyeb.com/pricing — Free: 1 Nano 0.1 vCPU 512MB RAM, no sleep, scale to zero
- **Dashboard:** https://app.koyeb.com
- **Docs FastAPI:** https://koyeb.com/docs/quickstart/deploy-a-fastapi-app
- **Tutorial Python:** https://koyeb.com/tutorials/deploy-fastapi-applications-on-koyeb

**Deploy 2min:**
1. https://app.koyeb.com → Sign up GitHub
2. Create App → Import GitHub → `rpolicarpo100/APP_Teste`
3. Build: Dockerfile, Port 8000, Health /health, Region fra (Frankfurt perto PT)
4. Env vars: DATABASE_URL, GROQ_API_KEY, etc
5. Deploy → `https://ai-brain-god-xxx.koyeb.app`

**Ficheiro já no repo:** `koyeb.yaml`

---

## 🔥 ALTERNATIVA 3: Render — JÁ ESTÁS LIVE 512MB (mantém)

**Links:**
- **Dashboard:** https://dashboard.render.com
- **Live:** https://app-teste-x6od.onrender.com — FUNCIONA 100% — 10 agentes, 35 tools
- **Health:** https://app-teste-x6od.onrender.com/health → {"status":"ok"}
- **Docs:** https://render.com/docs
- **Pricing:** https://render.com/pricing — Free: 750h/mo, sleep 15min

**Vantagem:** Já live, não precisas fazer nada — já tens keep-alive GitHub Actions cron 5min (`.github/workflows/keep-alive.yml`) que pinga /health a cada 5min para evitar sleep

**Teste agora:**
- https://app-teste-x6od.onrender.com/workspace/ranking → 100.0 GOOD
- https://app-teste-x6od.onrender.com/workspace/persist/status → Supabase 1GB / R2 10GB / GitHub Pages instructions
- https://app-teste-x6od.onrender.com/dashboard → CHAT | AGENT BUILDER + spinner + localStorage

---

## 🔥 ALTERNATIVA 4: Oracle Cloud Always Free — 4 ARM cores 24GB RAM FOREVER (6x Leapcell)

**Links:**
- **Free Tier:** https://www.oracle.com/cloud/free/ — https://cloud.oracle.com/free
- **Console:** https://cloud.oracle.com
- **Pricing:** https://www.oracle.com/cloud/free/ — Always Free: 4 OCPUs ARM Ampere A1, 24GB RAM, 200GB storage, 10TB outbound, forever
- **Docs FastAPI:** https://docs.oracle.com/en-us/iaas/developer-tutorials/tutorials/fastapi/01-fastapi-summary.htm
- **Tutorial Deploy:** https://docs.oracle.com/solutions/deploy-fastapi-oracle-cloud/

**Vantagem:** 24GB RAM (6x Leapcell 4GB), free forever real, não é trial
**Desvantagem:** Precisa cartão para verificação (não cobra, só verifica), signup às vezes rejeitado (tenta com email gmail, não custom domain)

**Deploy:**
1. https://cloud.oracle.com/free → Sign up → verifica cartão (não cobra)
2. Create VM → Ampere A1 → 4 OCPUs 24GB RAM → Ubuntu 22.04
3. SSH → `git clone https://github.com/rpolicarpo100/APP_Teste && cd APP_Teste && docker-compose up -d`
4. Abre port 8000 no Security List

---

## 🔥 ALTERNATIVA 5: Fly.io — 256MB free + 1024MB no fly.toml

**Links:**
- **Site:** https://fly.io
- **Pricing:** https://fly.io/docs/about/pricing/ — free tier shared CPU
- **Dashboard:** https://fly.io/dashboard
- **Docs Python:** https://fly.io/docs/languages-and-frameworks/python/

**Ficheiro já no repo:** `fly.toml` — `memory_mb = 1024`, `primary_region = mad` (Madrid perto Lisboa)

**Deploy:**
```bash
fly auth signup
fly launch --dockerfile Dockerfile --region mad
fly secrets set DATABASE_URL=... GROQ_API_KEY=... GEMINI_API_KEY=...
fly deploy
```

---

## 📊 Comparação Final — Qual escolher se Leapcell falhar em PT

| Plataforma | RAM Free | vCPU | Sleep? | Cartão? | Link | Ficheiro no repo |
|------------|----------|------|--------|---------|------|------------------|
| **Leapcell** | 4GB | 3 vCPU | maior que 15min | Não | https://leapcell.io | Dockerfile.leapcell + leapcell.json |
| **Zeabur** | ~1-2GB via $5 credit | shared | Não | Não | https://zeabur.com | zeabur.json |
| **Koyeb** | 512MB | 0.1 vCPU | Não | Não | https://koyeb.com | koyeb.yaml |
| **Render** | 512MB | 0.1 vCPU | 15min mas keep-alive 5min | Não | https://render.com | render.yaml — JÁ LIVE |
| **Fly.io** | 1024MB no toml | 1 shared | Não (auto stop) | Não para trial | https://fly.io | fly.toml |
| **Oracle** | 24GB | 4 ARM | Não | Sim verificação | https://cloud.oracle.com/free | docker-compose.yml |
| **Railway** | 512MB via $5 credit | shared | Não | Não | https://railway.app | Dockerfile |

**Recomendação:**
1. **Tenta Leapcell agora incognito:** https://leapcell.io/signup — está ONLINE 200 OK verificado
2. **Se PT IP bloqueado, usa Zeabur:** https://zeabur.com — $5/mo free no sleep no cartão — 2min deploy — melhor alternativa
3. **Mantém Render LIVE:** https://app-teste-x6od.onrender.com — já funciona 100% com 35 tools + Neon + spinner + CHAT|AGENT
4. **Para 24GB free forever:** Oracle Cloud https://cloud.oracle.com/free — se tiveres cartão para verificação

**Todos os ficheiros já no repo, push já feito, Render já live com 5 tarefas FEITAS**
