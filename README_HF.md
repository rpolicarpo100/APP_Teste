---
title: AI Brain GOD - 10 agentes + Tools Health
emoji: 🧠
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
---

# AI Brain GOD — Hugging Face Spaces (Free Forever, sem cartão)

Alternativa custo 0 ao Render free — 16GB RAM, 2 vCPU, free forever, sem cartão.

**Deploy:**
1. Cria Space em https://huggingface.co/new-space → Docker → Blank
2. `git clone https://huggingface.co/spaces/SEU_USER/ai-brain-god`
3. Copia todos os ficheiros deste repo para lá
4. `git push`

**Env vars no Space → Settings → Variables:**
- `DATABASE_URL` = Neon Postgres URI (free 0.5GB permanente sem cartão)
- `GROQ_API_KEY` = free 14.4k req/dia sem cartão em console.groq.com
- `GEMINI_API_KEY` = free 60 req/min em aistudio.google.com

**URLs:**
- Dashboard: `/dashboard/`
- Health: `/health`
- Tools Health: `/tools/health`
- Docs: `/docs`

**Vantagens vs Render free:**
- 16GB RAM vs 512MB → Playwright funciona
- Sleep 48h vs 15min
- Free forever sem cartão
- Sem limite 750h/mês

**Zero custo stack:** HF Spaces (host) + Neon (DB) + Groq (LLM) + Supabase Storage (files) — tudo sem cartão.
