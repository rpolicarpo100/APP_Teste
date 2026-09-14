# AGENTES E FUNCIONALIDADES — Review 2026-09-14

## 10 Agentes LIVE

### 1. Research Agent (`research`)
- **Função:** Investigação web, pesquisa de ferramentas, notícias, mercados
- **Tools:** web.search (Serper API ✅), web.fetch, news.portugal, news.world, news.markets, news.crypto, news.all
- **Uso:** "Pesquisa ferramentas gratuitas de trading", "Analisa canal YouTube Deadly Gods"
- **Status:** ✅ Ativo, usa SERPER_API_KEY (200 OK)

### 2. Coding_QA Agent (`coding_qa`)
- **Função:** Escrever código, QA, debug, gerar scripts Python
- **Tools:** filesystem.read, filesystem.write, filesystem.list, python.execute (desativado em prod por segurança), site.builder
- **Uso:** "Cria um script Python para...", "Corrige este código"
- **Status:** ✅ Ativo, allow_file_write true, allow_python_exec false (segurança)

### 3. Design Agent (`design`)
- **Função:** Criar designs, SVGs, specs visuais, UI/UX
- **Tools:** filesystem.write, site.builder
- **Uso:** "Cria design para landing page minimalista", "Gera SVG para logo"
- **Status:** ✅ Ativo

### 4. Business Agent (`business`)
- **Função:** Calcular margens, analisar mercado, criar modelo de negócio, gestão negócios
- **Tools:** businesses CRUD, platforms, market data
- **Uso:** "Calcula margem para negócio gaming", "Cria modelo negócio para loja online"
- **Status:** ✅ Ativo, 13 platforms, 1 negócio persistente Neon

### 5. Browser Agent (`browser`)
- **Função:** Abrir browser, screenshots, automação web
- **Tools:** browser.open, browser.screenshot
- **Uso:** "Abre site X e tira screenshot"
- **Status:** ⚠️ Precisa 1GB+ RAM, Render free 512MB limitado, Leapcell 4GB funciona

### 6. Automation Agent (`automation`)
- **Função:** Criar automações, schedulers, cron jobs
- **Tools:** scheduler.create, scheduler.list
- **Uso:** "Cria automação para verificar notícias a cada hora"
- **Status:** ✅ Ativo, mas scheduler morre no spin down Render 15min, precisa UptimeRobot ou Leapcell

### 7. Monitor Agent (`monitor`)
- **Função:** Monitorar sistema, health checks, logs
- **Tools:** dashboard.market_overview, provider.health_check, tool.health_check
- **Uso:** "Verifica saúde do sistema"
- **Status:** ✅ Ativo

### 8. Builder Agent (`builder`) — PRINCIPAL PARA AGENT TAB
- **Função:** Construir sites, apps, landing pages, sites YouTube gamer épico, AI assistants
- **Tools:** site.builder (REAL, gera HTML 12KB leve e bonito), filesystem.write
- **Uso:** "quero criar um site para o meu canal de youtube https://www.youtube.com/@Deadly_Gods_Portugal" → gera HTML gamer dark épico com embed YouTube
- **Status:** ✅ Ativo, testado LIVE: quero-criar-um-site-para-o-meu-canal-de--dcd605.html 12108 bytes
- **Tipos suportados:** youtube-site (gamer escuro épico), site, landing, portfolio, loja, app, ai (AI Assistant)
- **Estilos:** gamer escuro épico (Deadly Gods), moderno minimalista, bonito e leve, escuro elegante

### 9. Provider Health Agent (`provider_health`)
- **Função:** Verifica saúde de LLM providers (Groq, Gemini, OpenRouter, HuggingFace)
- **Tools:** provider.health_check, provider.ranking, provider.failover
- **Uso:** Automático a cada 5min via scheduler
- **Status:** ✅ Ativo, 4 providers LIVE: groq, gemini, openrouter, huggingface

### 10. Tools Health Agent (`tools_health`)
- **Função:** Verifica saúde de 29 tools, ranking, failover
- **Tools:** tool.health_check, tool.audit, tool.ranking, tool.failover, tool.usage_log
- **Uso:** Automático a cada 10min, endpoint /tools/health
- **Status:** ✅ Ativo, 29 total 29 OK 0 fail

## 29 Tools

- **Filesystem:** read, write, list
- **Web:** search (Serper ✅), fetch
- **Python:** execute (desativado prod)
- **Scheduler:** create, list
- **Browser:** open, screenshot
- **Site:** builder (REAL)
- **News:** portugal, world, markets, crypto, all (Google News RSS, CoinDesk, BBC)
- **Crypto:** markets, gainers_losers (CoinGecko API)
- **Stocks:** markets, gainers_losers (Yahoo Finance)
- **Dashboard:** market_overview
- **Provider:** health_check, ranking, failover
- **Tool:** health_check, audit, ranking, failover, usage_log

## Funcionalidades Adicionais

### LLM — 4 providers custo 0
- Groq compound-mini (200 OK, 2 keys), Gemini flash-latest (200 OK), OpenRouter nemotron free (200 OK), HuggingFace (402 depleted)
- Chat com IA real LIVE

### Database
- Neon Postgres 0.5GB free permanente sem cartão, type neon, memory 4, businesses 1 persistente

### Storage
- Workspace /workspace com ficheiros HTML gerados, preview via iframe
- Supabase Storage 1GB free opcional para persistência

### Search
- Serper API (Google Search) ✅ 200 OK, Tavily precisa key correta, AssemblyAI transcription ✅

## Nova Arquitetura 2 Tabs

### CHAT Tab — faz tudo MAS NÃO constrói
- **Mode:** chat, no_build=true
- **Faz:** pesquisa, análise, cálculos margem, explicações, orquestração, conversa com LLM real
- **Não faz:** construir sites/apps/AI (se pedir para construir, explica que deve ir para AGENT BUILDER)
- **Agentes usados:** research, coding_qa, design, business, browser, automation, monitor, provider_health, tools_health (todos exceto builder)
- **Exemplo:** "Analisa o canal Deadly Gods Portugal e dá sugestões" → Research Agent

### AGENT BUILDER Tab — só constrói
- **Mode:** agent, force_build=true
- **Faz:** só construir — sites, apps, landing pages, sites YouTube gamer épico, AI assistants
- **Não faz:** pesquisa, conversa geral (foca em build)
- **Agentes usados:** builder apenas, com site.builder tool REAL
- **Design:** gamer escuro épico #0a0a0b com accent #ff0000 YouTube red, Space Grotesk font
- **Exemplo:** "quero criar um site para o meu canal de youtube https://www.youtube.com/@Deadly_Gods_Portugal" → Builder Agent gera HTML 12108 bytes gamer épico com embed YouTube, CTA subscrever
- **Tipos:** youtube-site, site, landing, portfolio, loja, app, ai

## Site Review — Design Atualizado

**Antes:** 4 tabs DASHBOARD | CHAT | NEGÓCIOS | DEFINIÇÕES, design claro #fbf9f6 com accent #ff4d1a laranja

**Agora:** 2 tabs CHAT | AGENT BUILDER
- **CHAT:** design claro, minimalista, Inter font, sidebar com 10 agentes grid 2 cols, quick buttons para pesquisa/análise
- **AGENT:** design escuro gamer épico #0a0a0b, accent #ff0000 YouTube red, Space Grotesk font, sidebar com build types (YouTube Gamer, Site/Landing, AI Assistant, App), preview bar, workspace tabs (Preview, Workspace, Missões), build log mono, input com gradiente red
- **Preview:** iframe para /workspace/*.html, botão abrir nova tab
- **Workspace:** lista ficheiros, missões, stats sites construídos

**Vantagens:**
- Separação clara: CHAT conversa, AGENT constrói
- Sem "Como funciona" — CHAT explica, AGENT constrói direto
- Design atualizado para Deadly Gods Portugal (gamer épico)
- Capacidade AI: "quero criar uma ai" → AGENT BUILDER gera AI Assistant site

## Próximos Passos

1. Adicionar mais tipos em Builder: e-commerce, portfolio, blog
2. Integrar YouTube API para listar vídeos reais do canal
3. Adicionar TAVILY_API_KEY correta
4. Leapcell deploy com 4GB RAM para Browser Agent funcionar
5. UptimeRobot para evitar spin down 15min Render
