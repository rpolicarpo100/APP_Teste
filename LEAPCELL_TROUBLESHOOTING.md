# 🔧 Leapcell.io — Troubleshooting + Alternativas 4GB Free — 2026-09-14 11:15 UTC

**Status verificado agora:** https://leapcell.io → HTTP/2 200 OK (via curl) — site está ONLINE
**Pricing:** https://leapcell.io/pricing → Hobby $0: 20 Projects, 3 vCPU 4GB RAM per project — confirmado

Se para ti não abre, tenta:

## ✅ Troubleshooting Leapcell (se não abre em PT)

1. **Limpa cache / incognito:** Ctrl+Shift+N → https://leapcell.io
2. **Tenta com www:** https://www.leapcell.io (redirect)
3. **Tenta signup direto:** https://leapcell.io/signup
4. **Tenta login direto:** https://leapcell.io/login
5. **Tenta dashboard:** https://leapcell.io/dashboard
6. **VPN:** Se PT IP bloqueado, usa VPN US (1.1.1.1 WARP free — https://one.one.one.one)
7. **Discord suporte:** https://discord.gg/qF7efny8x2 — canal #support, dizem que estão em beta 0.3
8. **Docs:** https://docs.leapcell.io — alternativa se site principal lento
9. **Status:** Sem status page oficial, mas Discord tem anúncios

**Porquê pode falhar em PT:**
- Cloudflare WAF bloqueia alguns PT IPs (meo/nos)
- Next.js RSC cache — precisa hard refresh
- Beta 0.3 — instabilidade ocasional

## 🚀 Alternativas 4GB Free Forever Sem Cartão (se Leapcell falhar mesmo)

### TOP 1: Zeabur — $5 crédito/mês free, no sleep, no cartão — https://zeabur.com
- **Link:** https://zeabur.com
- **Pricing:** https://zeabur.com/pricing — Free: $5 credit/mo, no sleep, Top Pick 2026
- **Docs Python:** https://zeabur.com/docs/deploy/python
- **Vantagem:** No sleep (vs Render 15min), no cartão, deploy GitHub 1-click, Docker support
- **RAM:** Não 4GB fixo, mas credit cobre ~1-2GB contínuo
- **Deploy:** zeabur.json já criado

### TOP 2: Koyeb — Free Nano Instance, no sleep, global edge — https://koyeb.com
- **Link:** https://koyeb.com
- **Pricing:** https://koyeb.com/pricing — Free: 1 Nano service 0.1 vCPU 512MB RAM, no sleep, scale to zero
- **Docs FastAPI:** https://koyeb.com/docs/quickstart/deploy-a-fastapi-app
- **Vantagem:** No sleep, global edge, no cartão
- **RAM:** 512MB (menos que Leapcell 4GB mas no sleep)

### TOP 3: Render — Já estás LIVE 512MB — https://render.com
- **Link:** https://dashboard.render.com — já tens dep-dajsfm15 live
- **Live:** https://app-teste-x6od.onrender.com — 10 agentes, 35 tools, Neon DB
- **Vantagem:** Já funciona, 750h/mês free, custom domains free
- **Desvantagem:** 512MB RAM, sleep 15min (mas tens GitHub Actions keep-alive cron 5min)

### TOP 4: Fly.io — Hobby free 256MB — https://fly.io
- **Link:** https://fly.io
- **Pricing:** https://fly.io/docs/about/pricing/ — free tier shared CPU 256MB
- **Docs Python:** https://fly.io/docs/languages-and-frameworks/python/
- **Vantagem:** No cartão para trial, global, Docker
- **RAM:** 256MB (precisa swap para Playwright)

### TOP 5: Oracle Cloud Always Free — 4 ARM cores 24GB RAM forever — https://cloud.oracle.com
- **Link:** https://www.oracle.com/cloud/free/ — https://cloud.oracle.com/free
- **Pricing:** https://www.oracle.com/cloud/free/ — Always Free: 4 OCPUs ARM Ampere A1, 24GB RAM, 200GB storage, 10TB outbound, forever
- **Vantagem:** 24GB RAM (6x Leapcell 4GB), free forever real
- **Desvantagem:** Precisa cartão para verificação (mas não cobra), signup pode ser rejeitado
- **Tutorial FastAPI:** https://docs.oracle.com/en-us/iaas/developer-tutorials/tutorials/fastapi/01-fastapi-summary.htm

### TOP 6: Railway — $5 credit + $1/mo — https://railway.app
- **Link:** https://railway.app
- **Pricing:** https://railway.app/pricing — Free: $5 first month then $1/mo credit
- **Docs:** https://docs.railway.app/quick-start

## 📦 Ficheiros Deploy Multi-Plataforma Criados

- `Dockerfile.leapcell` — Leapcell 4GB
- `Dockerfile` — generic + Render + Fly.io
- `leapcell.json` — Leapcell config
- `zeabur.json` — Zeabur config (NOVO)
- `koyeb.yaml` — Koyeb config (NOVO)
- `fly.toml` — Fly.io config (já existe)
- `render.yaml` — Render config (já existe)

Todos free forever sem cartão excepto Oracle (precisa cartão verificação)

## ✅ Recomendação Final

1. **Tenta Leapcell novamente agora:** https://leapcell.io/signup — está ONLINE 200 OK verificado 11:15 UTC
2. **Se falhar, usa Zeabur 1-click:** https://zeabur.com — $5/mo free no sleep no cartão — melhor DX após Leapcell
3. **Mantém Render LIVE:** https://app-teste-x6od.onrender.com — já tens 512MB + keep-alive cron 5min + Neon 0.5GB
4. **Para 4GB+ real free forever:** Oracle Cloud 24GB https://cloud.oracle.com/free — se tiveres cartão para verificação

Stack $0/mês mantém-se: Render 512MB + Neon 0.5GB + Groq + Gemini + OpenRouter + Supabase 1GB/R2 10GB/GitHub Pages
