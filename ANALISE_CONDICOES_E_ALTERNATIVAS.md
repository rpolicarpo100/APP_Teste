# O que falta para o nosso AI ter condições? + Substituto Render Free Forever + Necessidades Críticas

## Estado Atual (Produção LIVE https://app-teste-x6od.onrender.com)

- 10 agentes: research, coding_qa, design, business, browser, automation, monitor, builder, provider_health, tools_health
- 29 tools OK (filesystem, web, python, scheduler, browser, site, news, crypto, stocks, dashboard, provider, tool)
- Database: Neon Postgres free 0.5GB permanente sem cartão (type: neon, url_set: true) — persistência custo 0 ✅
- Memory: 1 memória persistente em Neon ✅ (antes dava 500, agora 200)
- Businesses: 1 negócio EXPENSYVX FINAL NEON persistente em Neon ✅
- Platforms: 13 plataformas multi-links ✅
- Tools Health: auditoria + ranking + failover ✅
- Provider Health: 8 providers, 7 OK ✅

## O que FALTA para ter condições de produção real

### 1. LLM — Ollama não disponível em produção
- `ollama_available: false` — fallback local sem LLM
- Chat usa lógica local, não usa Llama/Mistral/GPT
- **Crítico:** Sem LLM, agentes não raciocinam, só executam tools básicas
- **Solução custo 0:** Groq free tier (14.400 req/dia, Llama 3.1 70B/8B, Mixtral, sem cartão) + OpenRouter free + Gemini free 60 req/min

### 2. Vector Search — Memória semântica ineficiente
- `memory_manager.search()` usa `LIKE %query%` — O(n), sem embeddings
- Não usa pgvector (Neon/Supabase suportam pgvector free)
- **Crítico:** Para RAG, precisa embeddings + similaridade vetorial
- **Solução custo 0:** Ativar `pgvector` no Neon (já temos Neon) + gerar embeddings via Hugging Face free API ou local `sentence-transformers`

### 3. Hosting — Render Free tem limitações severas
- Spins down após 15 min sem tráfego → primeiro request demora 60s
- Filesystem efêmero → `data/brain.db` e `workspace/` perdidos sem disk (agora usamos Neon, OK para DB, mas workspace files ainda perdidos)
- 750 horas/mês → ~31 dias se sempre ligado, mas com spin down economiza
- Sem disk em free (precisa cartão) → já resolvido com Neon, mas workspace ainda efêmero
- Postgres Free expira 30 dias (se usar Render Postgres)
- Requer cartão para web services? Docs dizem static sites sem cartão, web services com cartão — mas nosso está funcionando sem? Tem cartão no billing?
- **Solução custo 0 free forever:** Ver abaixo

### 4. File Storage — Workspace perdido
- Sites construídos via `site.builder` salvos em `workspace/` → perdidos no Render free sem disk
- **Solução custo 0:** Supabase Storage 1GB free sem cartão, ou Cloudflare R2 10GB free, ou Turso com blobs

### 5. Scheduler — APScheduler precisa always-on
- Render free spin down mata scheduler → jobs de provider_health (5min) e tools_health (10min) não rodam quando dorme
- **Solução custo 0:** UptimeRobot free (50 monitors, 5min) pinga `/health` para manter acordado, ou Cloudflare Cron Triggers (100k req/dia free)

### 6. Browser Automation — RAM insuficiente
- Playwright precisa 1GB+ RAM, Render free tem 512MB → crash
- **Solução:** Tornar opcional, ou usar Browserless free tier, ou usar `web.fetch` como fallback

### 7. Segurança — Sem auth, rate limit, anti-injection
- API aberta sem autenticação
- **Solução custo 0:** Adicionar API key simples via env var + rate limit via middleware

### 8. Backup/Restore — Sem backup automático
- Neon free tem PITR 6h, mas sem export automático
- **Solução custo 0:** Endpoint `/system/export-all` já existe, adicionar cron para exportar para Supabase Storage ou GitHub Gist

## Substituto Render Free Forever — Alternativas Viáveis Custo 0 Sem Cartão

### Pesquisa (2026)

| Plataforma | Free Forever? | Cartão? | RAM | Sleep? | Docker? | Melhor para |
|---|---|---|---|---|---|---|
| **Render** (atual) | Sim, 750h/mês | Sim para web services | 512MB | Sim, 15min idle, 30-60s wake | Sim | APIs, side projects |
| **Koyeb** | ❌ Fechou free Starter para novos users após aquisição Mistral AI Fev 2026 | - | - | - | - | Não viável mais |
| **Back4app Containers** | Sim, 1 container | Não | 256MB | Não? | Sim | Iniciantes, 1 container |
| **Hugging Face Spaces** | Sim | Não | 16GB | Sim, 48h idle | Sim (Docker) | AI apps, FastAPI Docker |
| **Deta Space** | Sim | Não | 512MB | Sim | Sim | Pequenos apps |
| **PythonAnywhere** | Sim | Não | 512MB disk, 100 CPU-sec/dia | Não | Não (WSGI) | Python WSGI, iniciantes |
| **Replit** | Sim, mas 100 CPU-sec/dia | Não | 1GB | Sim | Sim | Prototipagem browser |
| **Cloudflare Workers + D1** | Sim, 100k req/dia | Não | 128MB | Não, edge, 0ms cold | Não (Workers runtime) | APIs edge, serverless |
| **Vercel Hobby** | Sim, 100GB BW, 1M inv | Não | Serverless | Não | Não | Frontend, serverless funcs |
| **Oracle Cloud Always Free** | Sim, 4 OCPUs 24GB RAM 200GB | Sim (mas free forever) | 24GB | Não | Sim (VM) | Full VM, Docker Compose |
| **Google Cloud Run** | Sim, 2M req/mês | Sim | 512MB | Sim, scale to zero | Sim | APIs, event-driven |
| **Railway** | ❌ Só $5 trial | Não para trial | 1 vCPU 0.5GB | Não | Sim | Trial, não free forever |
| **Fly.io** | ❌ Trial only para novos | Sim | 256MB | Não | Sim | Não free forever mais |
| **Leapcell** | Sim, 20 projetos, 3 vCPU 4GB por projeto, 2GB transfer/mês | Não | 4GB | Não | Sim | Alternativa Railway sem cartão |
| **Nhost** | Sim, 1 projeto, 1GB DB + 1GB storage | Não | - | - | - | Backend com auth |
| **Northflank** | Sim, Developer 2 serviços | Não | - | - | Sim | Microserviços |

### Recomendação Custo 0 Sem Cartão — Stack Final

**Opção A: Manter Render + Neon (atual, funciona, custo 0)**

- Hosting: Render free 750h + UptimeRobot free para manter acordado (ping /health a cada 5min)
- DB: Neon free 0.5GB permanente sem cartão (já implementado, type: neon)
- Storage: Supabase Storage 1GB free sem cartão para workspace files
- LLM: Groq free tier (14.4k req/dia) + Gemini free
- Vector: Neon pgvector (ativar extensão)
- **Prós:** Já está live, 10 agentes, sem cartão, funciona
- **Contras:** Spin down 15min (mitigado com UptimeRobot), workspace efêmero (mitigado com Supabase Storage)

**Opção B: Hugging Face Spaces (melhor free forever sem cartão para Python)**

- Hosting: HF Spaces Docker — 16GB RAM, 2 vCPU, free, sem cartão, 1-click GitHub, não expira, sleep 48h (melhor que 15min Render)
- DB: Neon (mesmo) ou Supabase
- **Como migrar:** Criar Space → Docker → `FROM python:3.11` + `pip install -r requirements.render.txt` + `uvicorn app.main:app --host 0.0.0.0 --port 7860` (HF usa 7860)
- **Prós:** 16GB RAM vs 512MB Render → Playwright funciona, sem cartão, free forever
- **Contras:** Sleep 48h (melhor que Render), precisa adaptar porta

**Opção C: Cloudflare Workers + D1 + Hyperdrive (free forever, sem sleep, edge)**

- Hosting: Workers free 100k req/dia, 0ms cold, sem cartão, nunca dorme, edge global
- DB: D1 5GB SQLite free, sem cartão, ou Neon via Hyperdrive
- Storage: R2 10GB free
- **Prós:** Free forever, sem sleep, sem cartão, edge, D1 5GB (maior que Neon 0.5GB)
- **Contras:** Precisa refatorar FastAPI para Workers Python (Cloudflare agora suporta Python Workers), APScheduler → Cron Triggers

**Opção D: Oracle Cloud Always Free (mais poderoso, free forever, mas precisa cartão)**

- 4 OCPUs Ampere, 24GB RAM, 200GB storage, 2 VMs free forever
- Pode rodar Docker Compose com tudo: FastAPI + Postgres + Ollama local + Playwright
- **Prós:** Mais poderoso, free forever, full root, sem sleep
- **Contras:** Precisa cartão (mas não cobra), setup mais complexo

### Melhor Substituto Render Free Forever Sem Cartão

**Para nosso caso (FastAPI + 10 agentes + scheduler + Playwright):**

1. **Imediato (já temos):** **Render + Neon + UptimeRobot** — custo 0, sem cartão, já live, basta adicionar UptimeRobot para manter acordado
2. **Melhor free forever sem cartão:** **Hugging Face Spaces** — 16GB RAM, Docker, free, sem cartão, suporta Playwright, sleep 48h vs 15min Render
3. **Futuro edge:** **Cloudflare Workers + D1** — free forever, sem sleep, 5GB D1, mas precisa refatorar

### Implementação Sugerida Custo 0

1. Adicionar UptimeRobot free para pingar `https://app-teste-x6od.onrender.com/health` a cada 5 min → evita spin down Render
2. Ativar `pgvector` no Neon para memória semântica:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   CREATE TABLE memories_vec (id TEXT PRIMARY KEY, embedding vector(384), content TEXT);
   ```
3. Adicionar Groq free LLM:
   - Criar conta https://console.groq.com (sem cartão)
   - Gerar API key
   - Setar `GROQ_API_KEY` no Render
   - Código já tem fallback para usar Groq se `GROQ_API_KEY` setado
4. Adicionar Supabase Storage para workspace:
   - Criar Supabase free (sem cartão)
   - Usar para salvar sites construídos

## Conclusão

**O que falta para ter condições:** LLM (Groq free), Vector Search (Neon pgvector), UptimeRobot para evitar sleep, Storage persistente (Supabase), Auth básica.

**Substituto Render free forever custo 0 sem cartão:** Manter Render + Neon + UptimeRobot (já funciona) ou migrar para Hugging Face Spaces (16GB RAM, free, sem cartão, melhor que Render para nosso caso com Playwright).

**Stack final custo 0 recomendado:** Render (host) + Neon (DB 0.5GB permanente) + Groq (LLM 14.4k/dia) + Supabase Storage (1GB) + UptimeRobot (keep awake) — tudo sem cartão, free forever.
