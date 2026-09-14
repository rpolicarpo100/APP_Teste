# AUDITORIA KEYS RENDER — 2026-09-14

**URL:** https://app-teste-x6od.onrender.com
**Deploy:** dep-dajr4909 LIVE
**Env vars:** 20

## Keys encontradas

| Key | Len | Status | Detalhe |
|-----|-----|--------|---------|
| `GROQ_API_KEY` | 56 | ✅ **200 OK** | `gsk_t9cQ...6Zxk` — modelo antigo `llama-3.1-8b-instant` decommissioned, atualizado para `groq/compound-mini` que funciona |
| `OPENROUTER_API_KEY` | 73 | ✅ **200 OK** | `sk-or-v1...6215` — modelo antigo `llama-3.1-8b-instruct:free` indisponível free, atualizado para `nvidia/nemotron-3.5-lightning:free` |
| `HF_TOKEN` | 37 | ❌ **402 Depleted** | `hf_WkTfI...DnEB` user DeadlyGOds — `You have depleted your monthly included credits. Purchase pre-paid credits... PRO 20x more` |
| `SAMBANOVA_API_KEY` | 36 | ❌ **402 Payment Required** | `d94c16...ec76` — `balance_units 0, payment method required at cloud.sambanova.ai/plans/billing` |
| `NVIDIA_API_KEY` | 70 | ❌ **410 Gone** | `nvapi-S8...BNcq` — modelo `meta/llama-3.1-8b-instruct` EOL 2026-08-26 |
| `REPLICATE_API_KEY` | 40 | ❌ **402 Insufficient Credit** | `r8_ZrFLd...n6K8` user rpolicarpo100 Deadly_Gods_Portugal — account OK mas predictions `Insufficient credit to run this model` |
| `DATABASE_URL` | 154 | ✅ OK | Neon Postgres `type: neon` url_set true — 0.5GB free permanente |
| `GROQ_MODEL` | — | ✅ `groq/compound-mini` | Atualizado de `llama-3.1-8b-instant` (decommissioned) |
| `OPENROUTER_MODEL` | — | ✅ `nvidia/nemotron-3.5-lightning:free` | Atualizado de `llama-3.1-8b-instruct:free` (não free) |
| `HF_MODEL` | — | `meta-llama/Llama-3.1-8B-Instruct` | Mas créditos esgotados |

## Testes diretos

- **GROQ `groq/compound-mini`**: 200 OK — retorna `Olá, como posso ajudar?` — composto de `llama-3.3-70b-versatile` + `gpt-oss-120b`
- **OPENROUTER `nvidia/nemotron-3.5-lightning:free`**: 200 OK
- **HF**: 402 credits depleted
- **SAMBANOVA**: 402 payment required
- **NVIDIA**: 410 model EOL
- **REPLICATE**: account 200 OK, mas predictions 402 insufficient credit

## Produção LIVE

```
system/status:
  agents: 10 (research, coding_qa, design, business, browser, automation, monitor, builder, provider_health, tools_health)
  tools: 29 total, 29 OK, 0 fail
  database: {type: neon, url_set: true}
  llm: {available: true, providers: ['groq', 'openrouter', 'huggingface'], ollama: false}

tools/health: 29 OK
memory: 4 (Neon persistente)
businesses: 1 EXPENSYVX FINAL NEON (Neon persistente)
chat: 200 OK — "Sou o GOD Cerebro Core, o orquestrador universal que coordena 10 agentes e 29 ferramentas." — LLM real Groq
```

## Conclusão

- **2 de 6 keys funcionais** após correção de modelos: GROQ e OPENROUTER
- **4 keys com créditos esgotados/pagamento**: HF, SambaNova, NVIDIA (EOL), Replicate
- **Stack custo 0 funcional**: Render free + Neon 0.5GB + Groq compound-mini + OpenRouter free
- **Chat com IA real** já funciona em produção
- **Próximos passos**: 
  - HF: comprar créditos ou PRO para 20x mais (https://huggingface.co/settings/billing)
  - SambaNova: adicionar payment method
  - Replicate: comprar créditos
  - NVIDIA: usar modelo novo `meta/llama-3.3-70b-instruct` em vez de `llama-3.1-8b`

## Modelos Groq atuais (14)

```
meta-llama/llama-prompt-guard-2-22m
qwen/qwen3.8-27b
allam-2-7b
groq/compound
whisper-large-v3-turbo
meta-llama/llama-prompt-guard-2-86m
canopylabs/orpheus-v1-english
openai/gpt-oss-safeguard-20b
openai/gpt-oss-20b
qwen/qwen3.6-27b
openai/gpt-oss-120b
whisper-large-v3
groq/compound-mini ✅ FUNCIONA
```

Llama 3.1, 3.3, Gemma2 foram decommissioned em 2026.

## Modelos OpenRouter free atuais

```
nvidia/nemotron-3.5-lightning:free ✅
google/gemma-4-26b-a4b-it:free
nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free
...
```

`meta-llama/llama-3.1-8b-instruct:free` já não é free, precisa versão paga.
