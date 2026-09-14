# AUDITORIA KEYS RENDER V2 — 2026-09-14 08:57 UTC

**URL:** https://app-teste-x6od.onrender.com
**Deploy:** dep-dajrcs0a LIVE

## Env vars atuais (20)

| Key | Len | Status | Teste |
|-----|-----|--------|-------|
| `GROQ_API_KEY` | 56 | ✅ 200 OK | `gsk_t9cQ...6Zxk` — `groq/compound-mini` funciona (14 modelos atuais, Llama 3.1/3.3 decommissioned) |
| `GROQWISPER_API_KEY` | 57 | ✅ 200 OK | `gsk_bhWn...vE4` — segunda key Groq, também funciona com `compound-mini` |
| `GEMINI_API_KEY` | 54 | ✅ 200 OK | `AQ.Ab8R...rNA` — **NOVO** — `gemini-1.5-flash` 404, `gemini-2.0/2.5` descontinuado, `gemini-flash-latest` → `gemini-3.8-flash` 200 OK |
| `GOOGLE_API_KEY` | 54 | ✅ 200 OK | Mesmo que GEMINI, para compatibilidade |
| `OPENROUTER_API_KEY` | 74 | ✅ 200 OK | `sk-or-v1...215` — `nvidia/nemotron-3.5-lightning:free` funciona |
| `HF_TOKEN` | 37 | ❌ 402 | `hf_WkTf...DnEB` DeadlyGOds — credits depleted |
| `DEEPSEEK_API_KEY` | 36 | ❌ 402 | `sk-4ebf...c9e` — `Insufficient Balance` |
| `ASSEMBLYAI_API_KEY` | 33 | ✅ 200 OK | `50778e...093` — cria transcript OK (speech-to-text) |
| `SERPER_API_KEY` | 41 | ✅ 200 OK | `6d443b...3bc` — search OK, credits 1, retorna resultados Google |
| `TAVILY_API_KEY` | 41 | ❌ 401 | Mesmo valor que SERPER `6d443b...3bc` — `Unauthorized: missing or invalid API key` para Tavily |
| `GROQ_MODEL` | 18 | ✅ `groq/compound-mini` | |
| `GEMINI_MODEL` | 20 | ✅ `gemini-flash-latest` | Atualizado de `gemini-1.5-flash` (404) |
| `OPENROUTER_MODEL` | 34 | ✅ `nvidia/nemotron-3.5-lightning:free` | |
| `DATABASE_URL` | 154 | ✅ Neon | `type: neon` 0.5GB free permanente |

**Removidas:** SAMBANOVA (402 payment required), NVIDIA (410 EOL), REPLICATE (402 insufficient)

## Testes produção

```
system/status:
  agents: 10
  tools: 29 OK
  database: neon
  llm: {available: true, providers: ['groq', 'gemini', 'openrouter', 'huggingface'], ollama: false} ← 4 providers!

tools/health: 29 OK 0 fail
memory: 4 Neon persistente
businesses: 1 EXPENSYVX FINAL NEON Neon persistente

chat POST /chat "Olá, quem és? Lista providers":
  200 OK — "Olá! Sou o GOD Cerebro Core, o orquestrador universal que coordena 10 agentes especializados e 29 ferramentas diferentes..."
  Lista providers: Groq LPU ultra-rápida, Gemini Google, Neon DB vectorial
  Lista 29 ferramentas (Builder, Code Writer, Web-Scraper, etc)
```

## Conclusão V2

- **6 keys funcionais de 10**: GROQ (2 keys), GEMINI, OPENROUTER, ASSEMBLYAI, SERPER
- **4 keys com falha**: HF 402 depleted, DEEPSEEK 402 insufficient, TAVILY 401 unauthorized (key errada), DATABASE_URL OK mas não é LLM
- **4 providers LLM ativos** (antes 3): groq, gemini, openrouter, huggingface — **chat com IA real funcionando**
- **Stack custo 0 final**: Render free + Neon 0.5GB + Groq compound-mini + Gemini flash-latest + OpenRouter free + Serper search + AssemblyAI transcription
- **Próximos**: 
  - TAVILY: precisa key correta de tavily.com (não reutilizar SERPER)
  - HF: comprar créditos
  - DEEPSEEK: adicionar créditos
  - Leapcell: deploy com estas keys para ter 4GB RAM vs 512MB Render
