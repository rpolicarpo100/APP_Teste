# DEPLOY FINAL — Render + Neon + HuggingFace + Leapcell

## LIVE
- **URL:** https://app-teste-x6od.onrender.com
- **Deploy:** dep-dajqt4oj LIVE
- **Agents:** 10 (research, coding_qa, design, business, browser, automation, monitor, builder, provider_health, tools_health)
- **Tools:** 29 total, 29 OK, 0 fail
- **DB:** Neon Postgres `type: neon` url_set true — 0.5GB free permanente sem cartão
- **Memory:** count 2 persistente Neon
- **Businesses:** count 1 EXPENSYVX FINAL NEON persistente Neon
- **Platforms:** 13
- **LLM:** available true, providers ['huggingface'] — HF_TOKEN setado
- **Chat:** 200 OK (fix tabelas SQLite ephemeral)

## Stack custo 0 sem cartão

### Hosting
- **Render free** (atual LIVE): 750h/mês, 512MB RAM, spin down 15min, precisa UptimeRobot ping /health
- **Leapcell** (recomendado substituto HF Spaces): free forever sem cartão, 20 projetos, 3 vCPU 4GB RAM, 2GB transfer, Docker, suporta Playwright
- **HF Spaces Docker:** ❌ Agora exige PRO (402 Payment Required) — não é mais free forever

### Database
- **Neon** 0.5GB free permanente sem cartão ✅ LIVE
- Alternativas: Supabase 500MB pausa 1 semana, Turso 5GB SQLite, Upstash Redis 10k cmd/dia

### LLM — 5 providers custo 0
Ordem: Ollama local → Groq 14.4k/dia free → Gemini 60/min free → OpenRouter free → HuggingFace Inference free → fallback

- **Groq** (melhor): llama-3.1-8b-instant, 14.4k req/dia, sem cartão, console.groq.com → GROQ_API_KEY
- **Gemini**: gemini-1.5-flash, 60 req/min, sem cartão, aistudio.google.com → GEMINI_API_KEY
- **OpenRouter**: llama-3.1-8b:free, sem cartão
- **HuggingFace**: Qwen2.5-7B, Llama-3.1-8B, via router.huggingface.co/v1/chat/completions, free com HF_TOKEN, mas créditos mensais limitados, PRO 20x mais — **teu token DeadlyGOds esgotou créditos 402**
- **Ollama**: local apenas

**Para ativar LLM real em produção:** cria GROQ_API_KEY free em https://console.groq.com (sem cartão, 30s) e adiciona em Render → Environment → GROQ_API_KEY

### Storage
- Supabase Storage 1GB free sem cartão (para workspace persistente)

### Ficheiros criados
- `app/models/llm.py` — UniversalLLM com 5 providers + HuggingFaceClient
- `Dockerfile.leapcell` — para Leapcell
- `leapcell.json` — config Leapcell
- `LEAPCELL_DEPLOY.md` — guia deploy Leapcell
- `Dockerfile.hf` + `README_HF.md` — HF Spaces (agora exige PRO)
- `ANALISE_CONDICOES_E_ALTERNATIVAS.md` — gaps + comparativo hosting
- `ZERO_COST_ALTERNATIVES.md` — alternativas DB

## Próximos passos para produção total

1. **LLM:** Adiciona GROQ_API_KEY em Render (free 14.4k/dia sem cartão) → chat com IA real
2. **Leapcell:** Cria conta leapcell.io sem cartão, importa GitHub rpolicarpo100/APP_Teste, Dockerfile.leapcell, env vars DATABASE_URL + GROQ_API_KEY + HF_TOKEN
3. **UptimeRobot:** Cria monitor free 5min para https://app-teste-x6od.onrender.com/health para evitar spin down 15min
4. **Vector search:** Ativa pgvector no Neon: `CREATE EXTENSION vector` + embeddings HF free

## Teste

```bash
curl https://app-teste-x6od.onrender.com/system/status
curl https://app-teste-x6od.onrender.com/tools/health
curl -X POST https://app-teste-x6od.onrender.com/chat -H "Content-Type: application/json" -d '{"message":"Olá"}'
```
