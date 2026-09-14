# 🚀 Leapcell Deploy — 3 Minutos — Free Forever Sem Cartão — FINAL 2026-09-14

**LIVE atual Render:** https://app-teste-x6od.onrender.com — dep-dajsfm15 — 10 agentes, 33 tools OK

**Porquê Leapcell vs Render vs HF Spaces:**
- **Leapcell:** free forever sem cartão, 20 projetos, 3 vCPU 4GB RAM por projeto, 2GB transfer/mês, 60 build min/mês, Docker support, sleep maior que 15min Render — https://leapcell.io
- **Render:** 512MB RAM, 0.1 vCPU, sleep 15min, free 750h/mês — https://render.com
- **HF Spaces:** Docker agora exige PRO $9/mês (402 Payment Required) — https://huggingface.co/spaces

## ✅ Deploy em 3 Minutos — Passo a Passo com Links

### 1. Cria conta Leapcell (30s)
- **Link:** https://leapcell.io
- **Sign up:** com GitHub (sem cartão) — https://leapcell.io/signup
- **Dashboard:** https://leapcell.io/dashboard

### 2. New Project → Import from GitHub (30s)
- **Link New Project:** https://leapcell.io/dashboard/new
- **Repo:** `rpolicarpo100/APP_Teste`
- **GitHub Repo Link:** https://github.com/rpolicarpo100/APP_Teste
- **Branch:** main

### 3. Build Config (30s)
- **Build Type:** Dockerfile
- **Dockerfile Path:** `Dockerfile.leapcell` (já existe no repo)
- **Port:** 8000
- **Health Check:** `/health`
- **Replicas:** 1

### 4. Env Vars — Copia do Render (60s)
Adiciona estas env vars no dashboard Leapcell → Project → Settings → Environment Variables:

```
DATABASE_URL=postgresql://neondb_owner:npg_D1kFH0lYPvAi@ep-muddy-brook-adc8sq9j-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require
  → Neon 0.5GB free permanente — https://console.neon.tech — free sem cartão
  → Já tens, 0.5GB permanente, scale to zero

GROQ_API_KEY=gsk_t9cQt1...
  → Groq free 14.4k/dia — https://console.groq.com/keys — free sem cartão
  → Model: groq/compound-mini (funciona 200 OK, llama-3.3-70b + gpt-oss-120b)

GROQ_MODEL=groq/compound-mini

GEMINI_API_KEY=AQ.Ab8RN6I...
  → Gemini free 60/min — https://aistudio.google.com/app/apikey — free sem cartão
  → Model: gemini-flash-latest (200 OK, version gemini-3.8-flash)

GEMINI_MODEL=gemini-flash-latest

OPENROUTER_API_KEY=sk-or-v1-7...
  → OpenRouter free — https://openrouter.ai/keys — free sem cartão
  → Model: nvidia/nemotron-3.5-lightning:free

OPENROUTER_MODEL=nvidia/nemotron-3.5-lightning:free

HF_TOKEN=hf_WkTfIKPB...
  → HuggingFace — https://huggingface.co/settings/tokens — opcional, credits depleted

SERPER_API_KEY=6d443b41fa...
  → Serper Google Search 2500 free — https://serper.dev — free sem cartão

ASSEMBLYAI_API_KEY=50778e480f...
  → AssemblyAI transcription — https://www.assemblyai.com/dashboard — free $50 credits

# NOVO — Tarefa 2: Workspace Persistente Free Forever
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...
SUPABASE_BUCKET=workspace
  → Supabase Storage 1GB free — https://supabase.com/dashboard/project/_/storage — free sem cartão, 1GB storage
  → Cria projeto: https://supabase.com/dashboard/new
  → Storage → New bucket → workspace → public

R2_ACCOUNT_ID=xxx
R2_ACCESS_KEY_ID=xxx
R2_SECRET_ACCESS_KEY=xxx
R2_BUCKET=workspace
  → Cloudflare R2 10GB free — https://dash.cloudflare.com/r2 — free sem cartão, 10GB storage S3 compat
  → Cria bucket: https://dash.cloudflare.com/r2 → Create bucket → workspace
  → Manage R2 API Tokens → Create API Token → Object Read & Write

GITHUB_TOKEN=ghp_xxx
GITHUB_REPO=rpolicarpo100/APP_Teste
  → GitHub Pages gh-pages free forever — https://github.com/settings/tokens → Generate new token classic → repo scope
  → Repo: https://github.com/rpolicarpo100/APP_Teste/settings/pages → Source: gh-pages branch

# NOVO — Tarefa 5: Auth + CORS Seguro
API_KEY=gera-uma-key-segura-aqui
  → Opcional — se setada, exige header X-API-Key para endpoints protegidos — free, custo 0
  → Gera: openssl rand -hex 32

CORS_ORIGINS=https://app-teste-x6od.onrender.com,https://ai-brain-god.leapcell.dev,http://localhost:8000
  → CORS seguro — não * se API_KEY setada — lista de origens permitidas

# Deploy opcional Netlify/Vercel
NETLIFY_TOKEN=nfp_xxx
  → Netlify free — https://app.netlify.com/user/applications#personal-access-tokens — free sem cartão, drag & drop

VERCEL_TOKEN=vercel_xxx
  → Vercel free — https://vercel.com/account/tokens — free sem cartão
```

### 5. Deploy (2min build)
- **Click Deploy** → URL: `https://ai-brain-god.leapcell.dev` (exemplo)
- **Logs:** Ver build logs em real-time
- **Total: 3min**

## 📊 Vantagens Leapcell vs Alternativas

| Feature | Leapcell Free | Render Free | HF Spaces Docker |
|---------|---------------|-------------|------------------|
| **Custo** | free forever sem cartão | free 750h/mês, pede cartão p/ disk | Docker exige PRO $9/mês 402 |
| **RAM** | 4GB | 512MB | 16GB mas PRO |
| **vCPU** | 3 vCPU | 0.1 vCPU | 2 vCPU mas PRO |
| **Sleep** | maior que 15min | 15min | não sleep mas PRO |
| **Projetos** | 20 free | ilimitado mas sleep | 1 free mas sem Docker |
| **Build min** | 60 min/mês | ilimitado | ilimitado mas PRO |
| **Transfer** | 2GB/mês | 100GB/mês | ilimitado |
| **Docker** | ✅ | ✅ | ❌ exige PRO |
| **Playwright** | ✅ 4GB RAM funciona | ❌ 512MB falha | ✅ mas PRO |

## 🔗 Links Importantes

- **Leapcell:** https://leapcell.io
- **Leapcell Docs:** https://docs.leapcell.io
- **Leapcell Dashboard:** https://leapcell.io/dashboard
- **Leapcell Pricing:** https://leapcell.io/pricing — free forever sem cartão
- **Render Dashboard:** https://dashboard.render.com — atual live
- **Neon Console:** https://console.neon.tech — DB 0.5GB free
- **Groq Console:** https://console.groq.com — LLM free 14.4k/dia
- **Gemini API Keys:** https://aistudio.google.com/app/apikey — LLM free 60/min
- **OpenRouter Keys:** https://openrouter.ai/keys — LLM free
- **Supabase Storage:** https://supabase.com/dashboard — Storage 1GB free
- **Cloudflare R2:** https://dash.cloudflare.com/r2 — Storage 10GB free
- **GitHub Pages:** https://pages.github.com — free forever
- **GitHub Tokens:** https://github.com/settings/tokens — para gh-pages deploy
- **Netlify Tokens:** https://app.netlify.com/user/applications#personal-access-tokens — deploy free
- **Vercel Tokens:** https://vercel.com/account/tokens — deploy free

## ✅ Tarefas 5 Pendentes — Agora FEITAS

1. ✅ **Leapcell deploy manual 3min** — este ficheiro + Dockerfile.leapcell + leapcell.json prontos — https://leapcell.io → 3min
2. ✅ **Workspace persistente Supabase 1GB free ou R2 10GB ou GitHub Pages** — `app/tools/persistent_storage.py` + `/workspace/persist` endpoints + site_builder auto-persist
3. ✅ **Missions/tasks migrar SQLite efêmero → Neon Postgres** — `app/database/unified.py` + orchestrator.py refatorado → Neon 0.5GB free permanente
4. ✅ **Loading spinner + histórico localStorage no AGENT BUILDER** — frontend/index.html com CHAT|AGENT tabs, spinner animado, histórico 20 itens localStorage, timer 0s→11s
5. ✅ **Auth API_KEY + path traversal check extra + CORS seguro** — `app/security/auth.py` + middleware + headers X-Content-Type-Options nosniff etc

**Stack $0/mês free forever:** Leapcell 4GB + Neon 0.5GB + Groq 14.4k/dia + Gemini 60/min + OpenRouter free + Serper + AssemblyAI + Supabase 1GB/R2 10GB/GitHub Pages + GitHub Actions keep-alive

**Deploy final:** Render https://app-teste-x6od.onrender.com (live) + Leapcell https://ai-brain-god.leapcell.dev (após 3min setup)
