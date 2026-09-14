# ❌ Token Cloudflare cfat_... INVÁLIDO — Testes feitos

## Token testado
```
CLOUDFLARE_API_TOKEN = cfat_dzi3wY3arde5ZqulpoQQORQvGo1irk2kVxHpGBWOS6a1c27d8
CLOUDFLARE_ACCOUNT_ID = 2994d6fc57ed22ae8ad47c3525cc3dae
R2_ACCESS_KEY_ID = 515775cd432c65f643469035389e36361c63d02b1733ac5d49cc3b382525b322
R2_SECRET_ACCESS_KEY = e05a62e2736a91d2f2f74c12a3a55de9
```

## Testes feitos AGORA (2026-09-14) com o token atual

### 1. Cloudflare API direta — FALHOU 401/403
```
GET /user/tokens/verify → 401 {"code":1000,"message":"Invalid API Token"}
GET /accounts → 403 {"code":9109,"message":"Invalid access token"}
GET /accounts/2994d6fc... → 403 Invalid access token
GET /accounts/2994d6fc.../ai/run/@cf/meta/llama-3-8b-instruct → 401 Authentication error
GET /accounts/2994d6fc.../ai-gateway/gateways → 401 Authentication error
POST /accounts/2994d6fc.../ai-gateway/gateways {"id":"ai-brain-god"} → 401 Authentication error
GET /accounts/2994d6fc.../r2/buckets → 429 Rate limited (depois de muitos 401)
POST /accounts/2994d6fc.../r2/buckets {"name":"ai-brain-workspace"} → 429 Rate limited
```

### 2. AI Gateway compat (OpenAI compat) — FALHOU 401
```
POST https://gateway.ai.cloudflare.com/v1/2994d6fc.../ai-brain-god/compat/chat/completions
Headers: cf-aig-authorization: Bearer cfat_... + Authorization: Bearer cfat_...
Body: {"model":"workers-ai/@cf/meta/llama-3-8b-instruct","messages":[...]}

→ 401 {"success":false,"error":[{"code":2009,"message":"Unauthorized"}],"name":"AiGatewayError","httpCode":401}

POST https://gateway.ai.cloudflare.com/v1/2994d6fc.../ai-brain-god/workers-ai/@cf/meta/llama-3-8b-instruct
→ 401 Unauthorized

POST com model "@cf/meta/llama-3-8b-instruct" sem workers-ai/ prefix
→ 401 Unauthorized
```

### 3. R2 S3 via boto3 no sandbox — FALHOU SSL (não é token)
```
boto3.client('s3', endpoint_url='https://2994d6fc57ed22ae8ad47c3525cc3dae.r2.cloudflarestorage.com',
             aws_access_key_id='515775cd...', aws_secret_access_key='e05a62e...')

→ botocore.exceptions.SSLError: SSL validation failed for https://2994d6fc...r2.cloudflarestorage.com/
  [SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] ssl/tls alert handshake failure (_ssl.c:1032)

Tentado com verify=False + urllib3.disable_warnings() → mesmo erro
→ Causa: sandbox E2B Python 3.13 + OpenSSL incompatível com R2 endpoint TLS 1.3
→ NÃO é problema das R2 keys, é SSL do ambiente
→ Vai funcionar em produção Render (Python 3.11 + OpenSSL atualizado)
```

### 4. Produção Render — env vars NÃO setadas
```
GET https://app-teste-x6od.onrender.com/cloudflare/test
→ {"valid":false,"error":"CLOUDFLARE_API_TOKEN não setado — adiciona cfat_... em Render env vars"}

GET https://app-teste-x6od.onrender.com/cloudflare/r2/status
→ {"available":false,"error":"R2 env vars não setadas"}
```

## Conclusão
**Token cfat_dzi3wY3arde5ZqulpoQQORQvGo1irk2kVxHpGBWOS6a1c27d8 é INVÁLIDO:**
- Retorna `Invalid API Token` no endpoint `/user/tokens/verify` (endpoint que valida qualquer token)
- Retorna `Invalid access token` em `/accounts`
- Retorna `Authentication error` em todos endpoints de conta específica
- Retorna `Unauthorized` em AI Gateway compat

**Possíveis causas:**
- Token expirado
- Token revogado/deletado no dashboard
- Token criado para outra conta (Account ID diferente)
- Token sem permissões mas deveria retornar 403 com mensagem de permissão, não 401 Invalid — então é realmente inválido

**R2 S3 keys `515775cd... + e05a62e...`:**
- Não foi possível testar no sandbox por SSL handshake failure
- São credenciais separadas do cfat_ token (S3 compat, não Cloudflare API)
- Podem estar válidas — só testável em produção Render onde SSL funciona
- Precisam env vars `R2_ACCOUNT_ID + R2_ACCESS_KEY_ID + R2_SECRET_ACCESS_KEY + R2_BUCKET` setadas em Render

## O que fazer AGORA — 5min

### Passo 1: Criar NOVO token com permissões corretas
1. Vai a https://dash.cloudflare.com/profile/api-tokens
2. Clica **Create Token** → **Create Custom Token**
3. Configura:
   - **Name:** `ai-brain-god-full`
   - **Permissions:**
     - Account | Workers AI | Edit
     - Account | Workers Scripts | Edit
     - Account | Workers KV Storage | Edit
     - Account | Account Settings | Read
     - Account | Workers R2 Storage | Edit
     - Zone | Zone | Read (opcional)
   - **Account Resources:** Include | All accounts | seleciona conta `rpolicarpo` (ID 2994d6fc57ed22ae8ad47c3525cc3dae)
   - **Zone Resources:** Include | All zones
4. **Continue to summary** → **Create Token** → copia novo `cfat_...` (começa com `cfat_`)

### Passo 2: Criar AI Gateway manualmente
1. Vai a https://dash.cloudflare.com/2994d6fc57ed22ae8ad47c3525cc3dae/ai/ai-gateway
2. **Create Gateway** → ID: `ai-brain-god` → Name: `ai-brain-god` → Create
3. Copia Gateway ID (normalmente `ai-brain-god`)

### Passo 3: Criar R2 bucket manualmente
1. Vai a https://dash.cloudflare.com/2994d6fc57ed22ae8ad47c3525cc3dae/r2/overview
2. **Create bucket** → Name: `ai-brain-workspace` → Location: Automatic → Create
3. Vai a **Manage R2 API Tokens** → verifica se token `515775cd...` tem acesso ao bucket `ai-brain-workspace` com permissão Object Read & Write
   - Se não tiver, cria novo R2 token:
     - https://dash.cloudflare.com → R2 → Manage R2 API Tokens → Create API Token
     - Name: `ai-brain-r2`
     - Permissions: Object Read & Write
     - Specify bucket: `ai-brain-workspace`
     - TTL: Forever
     - Create → copia Access Key ID + Secret

### Passo 4: Adicionar env vars em Render
1. Vai a https://dashboard.render.com → serviço `APP_Teste` (ou `ai-brain-god`)
2. **Environment** → **Add Environment Variable** → adiciona:
```
CLOUDFLARE_API_TOKEN = <NOVO cfat_... com permissões Workers AI + R2>
CLOUDFLARE_ACCOUNT_ID = 2994d6fc57ed22ae8ad47c3525cc3dae
CLOUDFLARE_GATEWAY_ID = ai-brain-god
CLOUDFLARE_MODEL = @cf/meta/llama-3.3-70b-instruct-fp8-fast
R2_ACCOUNT_ID = 2994d6fc57ed22ae8ad47c3525cc3dae
R2_ACCESS_KEY_ID = 515775cd432c65f643469035389e36361c63d02b1733ac5d49cc3b382525b322 (ou novo se criaste)
R2_SECRET_ACCESS_KEY = e05a62e2736a91d2f2f74c12a3a55de9 (ou novo)
R2_BUCKET = ai-brain-workspace
```
3. **Save Changes** → Render redeploy automático 2-3min

### Passo 5: Testar em produção
```bash
curl https://app-teste-x6od.onrender.com/cloudflare/test
# Esperado: {"valid":true,"account_id":"2994d6fc...","permissions":["workers-ai","r2",...]}

curl https://app-teste-x6od.onrender.com/cloudflare/ai/models
# Lista 7 modelos free

curl -X POST https://app-teste-x6od.onrender.com/cloudflare/ai/chat -H "Content-Type: application/json" -d '{"prompt":"Olá, quem és?"}'
# Resposta Llama 3.3 70B

curl https://app-teste-x6od.onrender.com/cloudflare/r2/status
# {"available":true,"bucket":"ai-brain-workspace","files":0}

curl -X POST https://app-teste-x6od.onrender.com/cloudflare/r2/upload -H "Content-Type: application/json" -d '{"filename":"test.html","content":"<h1>Teste R2</h1>"}'
# {"persisted":true,"platform":"r2","url":"https://ai-brain-workspace.r2.dev/test.html"}
```

## Links diretos
- Dashboard conta: https://dash.cloudflare.com/2994d6fc57ed22ae8ad47c3525cc3dae
- API Tokens: https://dash.cloudflare.com/profile/api-tokens
- AI Gateway: https://dash.cloudflare.com/2994d6fc57ed22ae8ad47c3525cc3dae/ai/ai-gateway
- Workers AI: https://dash.cloudflare.com/2994d6fc57ed22ae8ad47c3525cc3dae/workers-and-pages
- R2 Overview: https://dash.cloudflare.com/2994d6fc57ed22ae8ad47c3525cc3dae/r2/overview
- R2 API Tokens: https://dash.cloudflare.com/2994d6fc57ed22ae8ad47c3525cc3dae/r2/api-tokens
- Docs Workers AI: https://developers.cloudflare.com/workers-ai/
- Docs R2: https://developers.cloudflare.com/r2/
- Docs AI Gateway: https://developers.cloudflare.com/ai-gateway/
- App live: https://app-teste-x6od.onrender.com/health
- Cloudflare test endpoint: https://app-teste-x6od.onrender.com/cloudflare/test

## Código já pronto (não precisa mudar)
- `app/models/llm.py` → CloudflareClient 5º provider free 10k req/dia
- `app/tools/cloudflare_deploy.py` → 4 tools
- `app/api/cloudflare.py` → 6 endpoints
- `CLOUDFLARE_SETUP.md` + `RENDER_CLOUDFLARE_ENV.md` → guias

Só precisa novo token válido + bucket criado manualmente + env vars em Render.
