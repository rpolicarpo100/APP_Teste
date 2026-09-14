# ☁️ Cloudflare Workers AI + R2 + Workers Deploy — com token cfat_...

**Token recebido:** `cfat_dzi3wY3arde5ZqulpoQQORQvGo1irk2kVxHpGBWOS6a1c27d8` — Account API Token (cfat_ format)

**Status token:** Formato válido cfat_... (Account API Token) — verificado via https://developers.cloudflare.com/fundamentals/api/get-started/token-formats/
- `cfat_` = Account API Token (owned by account, not user) — https://developers.cloudflare.com/fundamentals/api/get-started/account-owned-tokens/
- `cfut_` = User API Token
- `cfk_` = Global API Key

**Teste API:** `GET /accounts` → 403 Invalid access token — token não tem permissão `Account:Read` ou precisa Account ID na URL

## ✅ O que falta para ativar Cloudflare Workers AI free

Precisas de **Account ID** + opcional **Gateway ID**

### Como obter Account ID (10s):

1. **Dashboard:** https://dash.cloudflare.com → faz login
2. **URL contém Account ID:** `https://dash.cloudflare.com/<ACCOUNT_ID>/...` — copia o ID (hex 32 chars)
3. **Ou:** https://dash.cloudflare.com → clica no domínio → na direita "Account ID"
4. **Link direto:** https://dash.cloudflare.com/?to=/:account/workers-and-pages

### Como obter Gateway ID para AI Gateway (30s, opcional mas recomendado):

1. **AI Gateway:** https://dash.cloudflare.com → AI → AI Gateway (ou https://dash.cloudflare.com/?to=/:account/ai/ai-gateway)
2. **Create Gateway:** Nome `ai-brain-god` → Create
3. **Copia Gateway ID:** aparece no dashboard AI Gateway

### Env vars para Render / Leapcell / Zeabur / Koyeb:

```
CLOUDFLARE_API_TOKEN=cfat_dzi3wY3arde5ZqulpoQQORQvGo1irk2kVxHpGBWOS6a1c27d8
  → Já tens — Account API Token

CLOUDFLARE_ACCOUNT_ID=xxx
  → Pega em https://dash.cloudflare.com → URL: /<ACCOUNT_ID>/...

CLOUDFLARE_GATEWAY_ID=ai-brain-god
  → Opcional — se criaste AI Gateway em https://dash.cloudflare.com → AI → AI Gateway

CLOUDFLARE_MODEL=@cf/meta/llama-3-8b-instruct
  → Opcional — modelo default Workers AI free

# Para R2 10GB free (precisa S3 keys separadas, além de cfat_)
R2_ACCOUNT_ID=xxx (mesmo que CLOUDFLARE_ACCOUNT_ID)
R2_ACCESS_KEY_ID=xxx
R2_SECRET_ACCESS_KEY=xxx
R2_BUCKET=workspace
  → Cria em https://dash.cloudflare.com/r2 → Manage R2 API Tokens → Create Token → Object Read & Write
```

## 🚀 Cloudflare Workers AI — Modelos Free

**Todos free sem cartão, via Workers AI:**

- `@cf/meta/llama-3-8b-instruct` — Llama 3 8B, rápido, bom PT-PT
- `@cf/meta/llama-3.3-70b-instruct-fp8-fast` — Llama 3.3 70B, mais inteligente
- `@cf/mistral/mistral-7b-instruct-v0.1` — Mistral 7B
- `@cf/google/gemma-3-12b-it` — Gemma 3 12B
- `@cf/qwen/qwen2.5-coder-32b-instruct` — Qwen Coder 32B, bom para code
- `@cf/deepseek-ai/deepseek-r1-distill-qwen-32b` — DeepSeek R1 32B, reasoning
- `@cf/openai/gpt-oss-120b` — GPT-OSS 120B (se disponível)

**Endpoints:**
- Direct: `https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}`
- Via AI Gateway: `https://gateway.ai.cloudflare.com/v1/{account_id}/{gateway_id}/workers-ai/{model}`
- Compat OpenAI: `https://gateway.ai.cloudflare.com/v1/{account_id}/{gateway_id}/compat/chat/completions` com model `workers-ai/@cf/meta/llama-3-8b-instruct`

**Free tier:** 10k requests/dia Workers AI free — https://developers.cloudflare.com/workers-ai/platform/pricing/

## 🔧 Ferramentas Implementadas

- `cloudflare.test` — testa token cfat_... + tenta obter accounts + testa Workers AI
- `cloudflare.r2.upload` — upload workspace para R2 10GB free
- `cloudflare.workers.deploy` — deploy para Cloudflare Workers/Pages
- `cloudflare.ai.chat` — chat com Workers AI

**Endpoints API:**
- `GET /cloudflare/test` — testa token
- `POST /cloudflare/r2/upload` — upload R2
- `POST /cloudflare/workers/deploy` — deploy Workers/Pages
- `POST /cloudflare/ai/chat` — chat AI

## 📊 Cloudflare vs Leapcell vs Zeabur vs Render

| Feature | Cloudflare Workers | Leapcell | Zeabur | Render |
|---------|-------------------|----------|--------|--------|
| **RAM** | 128MB per Worker (mas Workers AI 4GB) | 4GB | ~1-2GB via $5 credit | 512MB |
| **vCPU** | shared | 3 vCPU | shared | 0.1 vCPU |
| **Sleep** | Não | maior que 15min | Não | 15min |
| **Cartão** | Não | Não | Não | Não |
| **Free tier** | 100k req/dia Workers, 10k AI | 20 proj, 2GB transfer | $5 credit/mo | 750h/mo |
| **Custom domain** | Sim free | Sim | Sim | Sim |
| **R2 Storage** | 10GB free | Não | Não | Não |
| **Workers AI** | 10k req/dia free | Não | Não | Não |
| **Link** | https://workers.cloudflare.com | https://leapcell.io | https://zeabur.com | https://render.com |

**Recomendação:** Usa Cloudflare Workers AI como 5º provider LLM free (já implementado) + R2 10GB para persistência + Workers/Pages para deploy 4GB alternativa a Leapcell
