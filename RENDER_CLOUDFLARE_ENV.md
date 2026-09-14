# 🔧 Configurar Cloudflare em Render — PASSO A PASSO

## Credenciais que já tens (fornecidas na imagem)

```
CLOUDFLARE_API_TOKEN = cfat_dzi3wY3arde5ZqulpoQQORQvGo1irk2kVxHpGBWOS6a1c27d8
CLOUDFLARE_ACCOUNT_ID = 2994d6fc57ed22ae8ad47c3525cc3dae
R2_ACCOUNT_ID = 2994d6fc57ed22ae8ad47c3525cc3dae
R2_ACCESS_KEY_ID = 515775cd432c65f643469035389e36361c63d02b1733ac5d49cc3b382525b322
R2_SECRET_ACCESS_KEY = e05a62e2736a91d2f2f74c12a3a55de9
```

## Problema detectado no token cfat_...

Testei o token via API:
- `GET /accounts` → 403 Invalid access token
- `GET /accounts/{id}/ai/run` → 401 Authentication error
- `GET /accounts/{id}/ai-gateway/gateways` → 401 Authentication error
- `GET /accounts/{id}/r2/buckets` → 401 Authentication error

**Causa:** token sem permissões Workers AI + R2 + Account Read, ou expirado, ou é token de conta diferente.

## Solução: Criar novo token com permissões corretas

1. Vai a https://dash.cloudflare.com/profile/api-tokens
2. Clica **Create Token** → **Create Custom Token**
3. Configura:

**Token name:** `ai-brain-god-full`

**Permissions:**
- Account → `Workers AI` → Edit
- Account → `Workers Scripts` → Edit
- Account → `Workers KV Storage` → Edit
- Account → `Account Settings` → Read
- Account → `Workers R2 Storage` → Edit
- Zone → `Zone` → Read (opcional, se quiser listar zones)

**Account Resources:** Include → All accounts → `rpolicarpo...` (ID 2994d6fc57ed22ae8ad47c3525cc3dae)
**Zone Resources:** Include → All zones

4. Clica **Continue to summary** → **Create Token**
5. Copia o novo token `cfat_...`

## Criar AI Gateway (para usar endpoint compat OpenAI)

1. Vai a https://dash.cloudflare.com → AI → **AI Gateway**
2. Clica **Create Gateway**
3. ID: `ai-brain-god`
4. Name: `ai-brain-god`
5. Cria → copia Gateway ID (normalmente igual ao ID)

## Criar R2 Bucket para workspace persistente 10GB free

1. Vai a https://dash.cloudflare.com → R2 → **Overview**
2. Clica **Create bucket**
3. Name: `ai-brain-workspace`
4. Location: Automatic
5. Cria
6. Vai a **Manage R2 API Tokens** → já tens Access Key ID `515775cd432c65f643469035389e36361c63d02b1733ac5d49cc3b382525b322` — verifica se tem permissão Object Read & Write no bucket `ai-brain-workspace`

Se não tiver bucket associado, cria novo R2 token:
- https://dash.cloudflare.com → R2 → Manage R2 API Tokens → Create API Token
- Name: `ai-brain-r2`
- Permissions: Object Read & Write
- Bucket: `ai-brain-workspace`
- TTL: Forever
- Copia Access Key ID + Secret Access Key

## Adicionar env vars em Render

1. Vai a https://dashboard.render.com → teu serviço `APP_Teste` (ou `ai-brain-god`)
2. **Environment** → **Add Environment Variable**
3. Adiciona uma a uma:

```
CLOUDFLARE_API_TOKEN = <novo token cfat_... com permissões Workers AI>
CLOUDFLARE_ACCOUNT_ID = 2994d6fc57ed22ae8ad47c3525cc3dae
CLOUDFLARE_GATEWAY_ID = ai-brain-god
CLOUDFLARE_MODEL = @cf/meta/llama-3.3-70b-instruct-fp8-fast
R2_ACCOUNT_ID = 2994d6fc57ed22ae8ad47c3525cc3dae
R2_ACCESS_KEY_ID = 515775cd432c65f643469035389e36361c63d02b1733ac5d49cc3b382525b322
R2_SECRET_ACCESS_KEY = e05a62e2736a91d2f2f74c12a3a55de9
R2_BUCKET = ai-brain-workspace
```

4. **Save Changes** → Render vai fazer redeploy automático
5. Aguarda 2-3 min → testa:

```bash
curl https://app-teste-x6od.onrender.com/cloudflare/test
curl https://app-teste-x6od.onrender.com/cloudflare/ai/models
curl -X POST https://app-teste-x6od.onrender.com/cloudflare/ai/chat -H "Content-Type: application/json" -d '{"prompt":"Olá, quem és?"}'
curl https://app-teste-x6od.onrender.com/cloudflare/r2/status
```

## O que já está implementado no código (bf8e734)

- `app/models/llm.py` → CloudflareClient como 5º provider free 10k req/dia
  - Fallback chain: Ollama → Groq → Gemini → **Cloudflare** → OpenRouter → HuggingFace
  - Modelos: @cf/meta/llama-3-8b-instruct, @cf/meta/llama-3.3-70b-fp8-fast, @cf/mistral/mistral-7b, @cf/google/gemma-3-12b-it, @cf/qwen/qwen2.5-coder-32b, @cf/deepseek-ai/deepseek-r1-distill-qwen-32b, @cf/openai/gpt-oss-120b
  - Endpoints: direct /ai/run, gateway /workers-ai, compat /compat/chat/completions (OpenAI compat)

- `app/tools/cloudflare_deploy.py` → 4 tools para agente:
  - `cloudflare.test` → testa token + lista accounts, zones, gateways, Workers AI
  - `cloudflare.r2.upload` → upload workspace para R2 10GB free
  - `cloudflare.workers.deploy` → lista Pages projects + deploy
  - `cloudflare.ai.chat` → chat com Workers AI

- `app/api/cloudflare.py` → 6 endpoints REST:
  - GET /cloudflare/test
  - POST /cloudflare/test
  - GET /cloudflare/r2/status
  - POST /cloudflare/r2/upload
  - POST /cloudflare/workers/deploy
  - POST /cloudflare/ai/chat
  - GET /cloudflare/ai/models

## Teste local que falhou (sandbox SSL)

```
R2 boto3 → SSLError SSLV3_ALERT_HANDSHAKE_FAILURE _ssl.c:1032
→ falha OpenSSL no sandbox E2B Python 3.13, não é problema das keys
→ vai funcionar em produção Render (Python 3.11 + OpenSSL atualizado)
```

## Próximos passos depois de adicionar env vars em Render

1. Testar `/cloudflare/test` → deve retornar `valid: true`
2. Testar `/cloudflare/ai/chat` → deve responder com Llama 3.3 70B
3. Testar `/cloudflare/r2/status` → deve listar bucket `ai-brain-workspace`
4. Se token ainda der 401, criar novo token com permissões acima
5. Workspace persistente: depois de R2 OK, configurar Supabase Storage ou R2 para salvar `data/brain.db` + `workspace/` files

Links úteis:
- Dashboard: https://dash.cloudflare.com/2994d6fc57ed22ae8ad47c3525cc3dae
- API Tokens: https://dash.cloudflare.com/profile/api-tokens
- AI Gateway: https://dash.cloudflare.com/2994d6fc57ed22ae8ad47c3525cc3dae/ai/ai-gateway
- Workers AI: https://dash.cloudflare.com/2994d6fc57ed22ae8ad47c3525cc3dae/workers-and-pages
- R2: https://dash.cloudflare.com/2994d6fc57ed22ae8ad47c3525cc3dae/r2/overview
- Docs Workers AI: https://developers.cloudflare.com/workers-ai/
- Docs R2: https://developers.cloudflare.com/r2/
- Pricing Workers AI 10k free: https://developers.cloudflare.com/workers-ai/platform/pricing/
