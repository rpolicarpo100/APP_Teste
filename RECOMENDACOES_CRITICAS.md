# RECOMENDAÇÕES CRÍTICAS — Realistas e Funcionais — 2026-09-14

**LIVE:** https://app-teste-x6od.onrender.com — dep-dajrql5g — 10 agentes, 29 tools OK, 4 LLM providers, Neon DB, CHAT|AGENT

---

## 1. HOSTING — Crítico

**Atual:** Render free 512MB RAM, 0.1 vCPU, 750h/mês, spin down 15min, filesystem efêmero, precisa cartão para disk.

**Problemas reais:**
- Browser Agent precisa 1GB+ RAM → falha em 512MB Render (Playwright)
- Scheduler (APScheduler) morre no spin down → missões agendadas não executam
- brain.db SQLite efêmero → perdia missions/tasks até fix com CREATE TABLE IF NOT EXISTS + migração
- Workspace /workspace efêmero → sites construídos perdidos a cada deploy (agora persistem até próximo deploy, mas não permanente)

**Recomendações funcionais custo 0:**

1. **Manter Render + UptimeRobot free** (solução imediata custo 0):
   - Cria monitor em https://uptimerobot.com free → ping https://app-teste-x6od.onrender.com/health a cada 5min → evita spin down 15min
   - Já tens Neon DB (persistente) → brain.db só para missions/tasks, recriado com schema completo, OK para MVP

2. **Migrar para Leapcell como primary (recomendado):**
   - Free forever sem cartão, 20 projetos, 3 vCPU 4GB RAM (vs 512MB Render) → Browser Agent funciona
   - 2GB transfer/mês free, 60 build min/mês, Docker support
   - Sleep maior que 15min Render
   - Deploy: leapcell.io → Import GitHub rpolicarpo100/APP_Teste → Dockerfile.leapcell → env vars DATABASE_URL (Neon) + GROQ_API_KEY + GEMINI_API_KEY + SERPER_API_KEY
   - Mantém Render como backup

3. **Cloudflare Workers + D1 para futuro (free forever sem cartão, sem sleep, edge):**
   - 100k req/dia free, D1 5GB SQLite free, Workers Python suportado desde 2024
   - Sem cold start, 0ms, mas requer refactor FastAPI → Workers (Hono ou FastAPI via workerd)
   - Ideal para chat API, mas não para Builder com filesystem

**Ação imediata:** Cria UptimeRobot hoje (2min). Cria conta Leapcell sem cartão (3min) e faz deploy como backup.

---

## 2. LLM / AI — Crítico

**Atual:** 4 providers LIVE: groq compound-mini (200 OK), gemini flash-latest (200 OK), openrouter nemotron free (200 OK), huggingface (402 depleted). 2 keys Groq, 1 Gemini, 1 OpenRouter funcionais.

**Problemas reais:**
- Groq: modelos antigos decommissioned — llama-3.1-8b-instant, llama-3.3-70b-versatile, gemma2-9b-it removidos em 2026, só 14 modelos atuais (compound-mini, qwen3.6-27b, gpt-oss-20b/120b)
- Gemini: 1.5-flash, 2.0-flash, 2.5-flash descontinuados/not available to new users, só flash-latest (3.8-flash) funciona
- OpenRouter: llama-3.1-8b-instruct:free não é mais free, precisa nemotron-3.5-lightning:free
- HF: credits depleted 402, precisa PRO para 20x mais
- DeepSeek: insufficient balance 402
- TAVILY: key errada (reutilizou SERPER key)
- System prompt anterior dizia "Como funciona" → removido, agora CHAT|AGENT separados

**Recomendações funcionais:**

1. **Fix modelos (FEITO):**
   - GROQ_MODEL=groq/compound-mini ✅
   - GEMINI_MODEL=gemini-flash-latest ✅
   - OPENROUTER_MODEL=nvidia/nemotron-3.5-lightning:free ✅

2. **Adicionar fallbacks robustos:**
   - Implementar retry com backoff para Groq/Gemini 429/503
   - Adicionar DeepSeek com créditos (quando adicionares) como 5º provider
   - Adicionar TAVILY_API_KEY correta de tavily.com (free 1000 req/mês sem cartão) para web.search

3. **Otimizar custos:**
   - Groq compound-mini usa 2 modelos internos (llama-3.3-70b + gpt-oss-120b) → 580 tokens por request, OK para free tier 14.4k/dia
   - Gemini flash-latest tem thought tokens (240) → usar gemini-flash-lite-latest para 50% menos tokens se precisares poupar
   - OpenRouter free tem rate limit 20 req/min → usar como fallback, não primary

4. **Segurança LLM:**
   - CHAT tab já não constrói (no_build) → evita prompt injection que force build
   - AGENT tab só constrói (force_build) → isola builder
   - Adicionar validação de input: bloquear "<script>", "rm -rf", etc no site_builder objective

**Ação imediata:** Compra TAVILY key correta (free) e adiciona em Render. Testa Gemini flash-lite-latest para poupar tokens.

---

## 3. DATABASE / PERSISTÊNCIA — Crítico

**Atual:** Neon Postgres 0.5GB free permanente sem cartão ✅ LIVE type neon, memory 4, businesses 1 persistente. SQLite brain.db para missions/tasks com schema completo + migração result_summary.

**Problemas reais:**
- brain.db ainda efêmero em Render → missions/tasks perdidas a cada deploy (mas agora recriado com schema completo, OK para MVP)
- Workspace /workspace efêmero → sites HTML perdidos a cada deploy
- Sem backup automático

**Recomendações funcionais:**

1. **Manter Neon para dados críticos (FEITO, bom):**
   - Neon 0.5GB permanente free sem cartão é melhor que Supabase 500MB pausa 1 semana, Turso 5GB mas SQLite, Render Postgres 1GB expira 30d
   - Já tens memory e businesses em Neon ✅

2. **Migrar missions/tasks para Neon também (recomendado):**
   - Criar tabelas missions, tasks, conversations, messages em Neon com pgvector para vector search
   - Usar asyncpg ou psycopg2 com RealDictCursor (já tens em businesses.py)
   - Assim missions persistem mesmo com deploy Render

3. **Workspace persistente:**
   - **Opção A custo 0:** Supabase Storage 1GB free sem cartão → upload HTML para bucket, serve via CDN
   - **Opção B custo 0:** Cloudflare R2 10GB free/mês → S3 compatible, free forever
   - **Opção C simples:** Commit automático para GitHub repo gh-pages via GitHub API (free) → sites ficam em https://rpolicarpo100.github.io/APP_Teste/workspace/

4. **Backup:**
   - Endpoint /system/export-all já existe → cria cron UptimeRobot que chama /system/export-all a cada dia e guarda JSON em Neon ou Supabase Storage
   - Neon tem backups automáticos free 7 dias

**Ação imediata:** Cria bucket Supabase Storage free e modifica site_builder para fazer upload para Supabase além de salvar local. Ou usa GitHub Pages para persistência simples.

---

## 4. AGENTES / TOOLS — Review Crítico

**10 agentes LIVE, 29 tools OK:**

**Funcionais 100%:**
- research (web.search Serper 200 OK, news RSS) ✅
- coding_qa (filesystem.write) ✅
- design (site.builder) ✅
- business (13 platforms, 1 negócio Neon) ✅
- builder (site.builder REAL, 12108 bytes YouTube gamer épico) ✅
- provider_health (4 providers) ✅
- tools_health (29 OK) ✅
- monitor (market overview) ✅

**Parcialmente funcionais:**
- browser (precisa 1GB+ RAM, Render 512MB falha, Leapcell 4GB funciona) ⚠️
- automation (scheduler morre no spin down 15min Render) ⚠️

**Recomendações:**

1. **Browser Agent:**
   - Desativar em Render free via DISABLE_BROWSER=true ou tornar opcional
   - Ativar só em Leapcell 4GB RAM
   - Alternativa custo 0: usar ScrapingBee free 1000 req/mês ou Browserless free tier em vez de Playwright local

2. **Automation Agent:**
   - Usar Cloudflare Cron Triggers free 100k/dia em vez de APScheduler local → não morre no spin down
   - Ou UptimeRobot que chama /scheduler/run a cada 5min

3. **Builder Agent — melhorias realistas:**
   - **YouTube API:** Integrar YouTube Data API v3 free 10k quota/dia → listar vídeos reais do canal Deadly Gods em vez de placeholders "Gameplay Épico #1"
   - **Mais tipos:** Adicionar e-commerce (com Stripe free test), blog (com Markdown), portfolio
   - **AI Assistant:** Quando user pede "cria uma ai", gerar não só site mas também backend FastAPI com /chat endpoint para AI real (usar Groq/Gemini keys)

4. **Novos agentes úteis custo 0:**
   - **SEO Agent:** Analisa site com Lighthouse free, sugere melhorias
   - **Analytics Agent:** Integra com YouTube Analytics API free para mostrar views, subs no site

**Ação imediata:** Adiciona YouTube Data API key free (console.cloud.google.com, sem cartão) e modifica site_builder para buscar vídeos reais.

---

## 5. FRONTEND / UX — Review e Recomendações

**Antes:** 4 tabs DASHBOARD | CHAT | NEGÓCIOS | DEFINIÇÕES, design claro #fbf9f6 accent #ff4d1a

**Agora:** 2 tabs CHAT | AGENT BUILDER — CHAT claro minimalista, AGENT escuro gamer épico #0a0a0b accent #ff0000

**Problemas reais:**
- Frontend antigo tinha 2344 linhas, muito código, difícil manter
- Sem separação clara CHAT vs BUILDER → user confundido com "Como funciona"
- Preview iframe com sandbox allow-scripts mas sem allow-same-origin em alguns casos → bloqueia JS
- Sem loading states claros quando Builder está a construir (11s)
- Sem histórico de sites construídos persistente

**Recomendações funcionais:**

1. **Manter 2 tabs (FEITO, bom):**
   - CHAT: faz tudo menos construir ✅ testado artifacts 0
   - AGENT: só constrói ✅ testado artifacts 1 com YouTube gamer épico
   - System prompts separados por mode ✅

2. **Melhorias UX realistas:**
   - **Loading:** Adicionar spinner + "Builder Agent a construir... 11s" + progresso das 3 tarefas (Research → Design → Coding)
   - **Histórico:** Guardar lista de sites construídos em localStorage + Neon DB → mostrar em AGENT > Workspace > Histórico
   - **Preview:** Adicionar botão "Copiar HTML", "Download ZIP", "Deploy para Netlify/Vercel free" (via API)
   - **YouTube específico:** No AGENT BUILDER, quando seleciona "Site YouTube Gamer", mostrar input para URL do canal com validação regex youtube.com/@
   - **AI específico:** Quando "AI Assistant", mostrar opções: "Chatbot", "Assistente YouTube", "Bot Discord"

3. **Design Deadly Gods:**
   - **Atual:** gamer escuro épico #0a0a0b com red #ff0000, Space Grotesk, OK para Deadly Gods
   - **Melhoria:** Adicionar logo real do canal (buscar via YouTube API), cores dinâmicas baseadas no canal (extrair cor dominante do avatar)
   - **Mobile:** Testar responsive — já tem @media max-width 900px, mas precisa testar em telemóvel real

4. **Performance:**
   - Frontend atual 1 ficheiro HTML com CSS inline → 20KB, OK
   - Mas tem Google Fonts import → bloqueia render, usar font-display: swap ou self-host
   - Adicionar PWA manifest free para instalar como app

**Ação imediata:** Adiciona loading spinner no AGENT BUILDER e histórico de sites em localStorage (30min trabalho).

---

## 6. SEGURANÇA / CONFIABILIDADE — Crítico

**Atual:** allow_file_write true, allow_python_exec false, CORS *, sem auth, sem rate limit.

**Problemas reais:**
- Sem autenticação → qualquer pessoa pode chamar /chat e gastar Groq/Gemini quota (14.4k/dia Groq, 60/min Gemini)
- Sem rate limit → ataque DDoS pode esgotar quota em minutos
- allow_file_write true → pode escrever em qualquer path dentro de workspace, mas sem validação de path traversal (ex: ../../etc/passwd)
- site_builder objective sem sanitização → pode injetar <script> malicioso no HTML gerado
- Keys no Render env vars visíveis via API se RENDER_API_KEY vazar (está no código?)

**Recomendações funcionais custo 0:**

1. **Rate limit simples (30min):**
   - Adicionar slowapi ou fastapi-limiter com Redis Upstash free 10k cmd/dia
   - Ou simples in-memory: 10 req/min por IP para /chat

2. **Auth simples para /chat e /builder:**
   - Adicionar API_KEY env var simples → frontend envia X-API-Key header
   - Ou usar Supabase Auth free 50k MAU sem cartão

3. **Sanitização:**
   - Em site_builder, escapar objective com html.escape() antes de inserir no HTML
   - Validar filename com _slugify já faz, mas adicionar check para não conter ".."

4. **Keys:**
   - Remover RENDER_API_KEY hardcoded do código (está em bash history, mas não no repo, OK)
   - Usar Doppler ou Infisical free para gerir secrets (alternativa a .env)

5. **Backup e monitorização:**
   - UptimeRobot já recomendado para evitar spin down, também serve como monitor uptime
   - Sentry free 5k events/mês para logs de erros

**Ação imediata:** Adiciona rate limit 10 req/min por IP em /chat (15min com slowapi) e sanitiza site_builder objective com html.escape().

---

## 7. CUSTOS / FREE FOREVER — Realista

**Stack atual custo 0 sem cartão (exceto Render que pede cartão para disk mas web service free funciona):**

| Componente | Free Tier | Cartão? | Status |
|------------|-----------|---------|--------|
| Render Web | 750h/mês, 512MB, sleep 15min | Sim para disk, mas web free funciona | ✅ LIVE |
| Neon DB | 0.5GB permanente | Não | ✅ LIVE |
| Groq | 14.4k req/dia, 2 keys | Não | ✅ 200 OK |
| Gemini | 60 req/min, flash-latest | Não | ✅ 200 OK |
| OpenRouter | 20 req/min free models | Não | ✅ 200 OK |
| Serper | 2500 req/mês free? (2500?) | Não | ✅ 200 OK |
| AssemblyAI | 5h/mês free | Não | ✅ 200 OK |
| HF | Credits mensais limitados | Não, mas precisa PRO para 20x | ❌ 402 depleted |
| Leapcell | 20 projetos, 3vCPU 4GB, 2GB transfer | Não | 🔜 Recomendado |

**Custo real se escalar:**
- Render Starter $7/mês → sem sleep, 512MB, 100GB BW
- Neon Pro $19/mês → 10GB, sem pausa
- Groq $0.59/M tokens → 14.4k req/dia free chega para 100 users/dia
- Gemini free chega, Pro $7/mês para 1M tokens

**Recomendação custo 0 permanente:**
- **Host:** Leapcell free (primary) + Render free + UptimeRobot (backup) → free forever sem cartão
- **DB:** Neon free 0.5GB → suficiente para 10k memórias, 1k negócios
- **LLM:** Groq free + Gemini free + OpenRouter free → 3 providers, failover automático
- **Search:** Serper free 2500/mês + Tavily free 1000/mês (precisa key correta)
- **Storage:** Supabase Storage 1GB free ou R2 10GB free
- **Total:** $0/mês permanente, sem cartão (exceto Leapcell que não pede cartão)

**Ação imediata:** Cria conta Leapcell (sem cartão) e faz deploy com Dockerfile.leapcell — 4GB RAM resolve Browser Agent e sleep.

---

## 8. DEADLY GODS PORTUGAL — Específico

**Canal:** https://www.youtube.com/@Deadly_Gods_Portugal — gaming, comunidade PT

**Site atual gerado:** https://app-teste-x6od.onrender.com/workspace/quero-criar-um-site-para-o-meu-canal-de--a58e45.html — 12108 bytes, gamer escuro épico, YouTube red, embed canal, CTA subscrever

**Problemas reais:**
- Vídeos são placeholders "Gameplay Épico #1" em vez de vídeos reais do canal
- Sem integração com YouTube API para mostrar subs count real (1.2K placeholder)
- Sem SEO para "Deadly Gods Portugal" no Google
- Sem analytics

**Recomendações funcionais:**

1. **YouTube Data API v3 free (10k quota/dia, sem cartão):**
   - Cria key em console.cloud.google.com → YouTube Data API v3 → key
   - Adiciona YOUTUBE_API_KEY em Render env vars
   - Modifica site_builder para chamar `https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id=...&key=...` e `.../search?part=snippet&channelId=...&order=date`
   - Mostra vídeos reais, subs count real, avatar real

2. **SEO:**
   - Adicionar meta tags: `<meta name="description" content="Deadly Gods Portugal — Gameplays épicos...">`, Open Graph, Twitter Card, JSON-LD
   - Sitemap.xml com vídeos
   - Schema.org VideoObject

3. **Funcionalidades para canal:**
   - Newsletter: Mailchimp free 500 contacts ou Brevo free 300 emails/dia
   - Discord widget: embed Discord server se tiver
   - Loja merch: Printful + Stripe free test mode
   - Doação: BuyMeACoffee ou Ko-fi free

4. **Deploy do site Deadly Gods:**
   - Opção A: Netlify free drag & drop do HTML → deadlygodsportugal.netlify.app free
   - Opção B: Vercel free → importa HTML
   - Opção C: GitHub Pages free → commit para gh-pages branch
   - Opção D: Cloudflare Pages free → upload HTML

**Ação imediata:** Cria YouTube Data API key free (5min) e atualiza site_builder para buscar vídeos reais. Faz deploy do site Deadly Gods para Netlify free.

---

## RESUMO — Ações Imediatas (2h total)

**30min — Crítico:**
1. UptimeRobot free → ping /health a cada 5min (evita sleep Render)
2. Rate limit 10 req/min em /chat (slowapi)
3. Sanitiza site_builder com html.escape()

**60min — Importante:**
4. Cria conta Leapcell sem cartão → deploy com Dockerfile.leapcell → 4GB RAM resolve Browser Agent
5. Cria YouTube Data API key free → integra vídeos reais no site Deadly Gods
6. Cria TAVILY_API_KEY correta free (tavily.com) → adiciona em Render

**30min — Melhorias:**
7. Adiciona loading spinner + histórico localStorage no AGENT BUILDER
8. Deploy site Deadly Gods para Netlify free
9. Backup: cron que chama /system/export-all e guarda em Supabase Storage

**Total custo:** $0/mês permanente, sem cartão, free forever.

**Stack final recomendada custo 0:**
- Host: Leapcell free (primary) + Render free + UptimeRobot (backup)
- DB: Neon 0.5GB free permanente
- LLM: Groq compound-mini + Gemini flash-latest + OpenRouter nemotron free (3 providers failover)
- Search: Serper + Tavily free
- Storage: Supabase Storage 1GB + R2 10GB
- Site Deadly Gods: Netlify free + YouTube Data API free

**Links:**
- LIVE: https://app-teste-x6od.onrender.com
- Site Deadly Gods: https://app-teste-x6od.onrender.com/workspace/quero-criar-um-site-para-o-meu-canal-de--a58e45.html
- CHAT (não constrói): tab CHAT
- AGENT (só constrói): tab AGENT BUILDER
