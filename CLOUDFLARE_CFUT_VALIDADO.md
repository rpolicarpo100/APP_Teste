# ✅ Cloudflare cfut_ token VALIDADO — Workers AI OK, R2 SSL fail

## Novo token testado: `cfut_... (validado)`

### Testes feitos 2026-09-14

#### 1. Token validity — 200 OK
```
GET /user/tokens/verify
→ 200 {"result":{"id":"31951a0bc4c1c0e8ec7e4451ae9e1593","status":"active","expires_on":"2027-11-27T23:59:59Z"},"success":true,"errors":[],"messages":[{"code":10000,"message":"This API Token is valid and active"}]}
```
**Token válido, ativo, expira 2027-11-27**

#### 2. List Accounts — 200 mas vazio
```
GET /accounts
→ 200 {"result":[],"result_info":{"page":1,"per_page":20,"total_pages":0,"count":0,"total_count":0}}
```
Token não tem permissão para listar accounts (normal para User Token com escopo limitado)

#### 3. Get Account 2994d6fc57ed22ae8ad47c3525cc3dae — 403
```
GET /accounts/2994d6fc57ed22ae8ad47c3525cc3dae
→ 403 {"success":false,"errors":[{"code":9109,"message":"Unauthorized to access requested resource"}]}
```
Token não tem acesso direto a este account ID via API de contas, mas Workers AI funciona mesmo assim (ver abaixo)

#### 4. Workers AI — 200 OK ✅
```
POST /accounts/2994d6fc57ed22ae8ad47c3525cc3dae/ai/run/@cf/meta/llama-3.3-70b-instruct-fp8-fast
{"prompt":"Olá, quem és? Responde em PT curto"}
→ 200 {"result":{"choices":[{"finish_reason":"length","text":".\n\nSou um modelo de inteligência artificial..."}],"usage":{"prompt_tokens":17,"completion_tokens":256}},"success":true}

POST /accounts/2994d6fc57ed22ae8ad47c3525cc3dae/ai/run/@cf/openai/gpt-oss-120b
→ 200 {"result":{"choices":[{"message":{"content":"Olá! Eu sou o ChatGPT, um modelo de linguagem avançado criado pela OpenAI...","role":"assistant"}}]},"success":true}

POST /accounts/2994d6fc57ed22ae8ad47c3525cc3dae/ai/run/@cf/meta/llama-3-8b-instruct
→ 410 {"errors":[{"message":"AiError: Model has been deprecated: @cf/meta/llama-3-8b-instruct was deprecated on 2026-05-30...","code":5028}]}
→ Modelo deprecated 2026-05-30, usar llama-3.3-70b-fp8-fast

POST /accounts/2994d6fc57ed22ae8ad47c3525cc3dae/ai/run/@cf/google/gemma-3-12b-it
→ 403 {"errors":[{"message":"AiError: Ai: This account is not allowed to access @cf/google/gemma-3-12b-it...","code":5018}]}
→ Modelo não permitido neste account
```

**Workers AI FUNCIONA com este token + account 2994d6fc...**
- ✅ `@cf/meta/llama-3.3-70b-instruct-fp8-fast` → 200 OK
- ✅ `@cf/openai/gpt-oss-120b` → 200 OK
- ❌ `@cf/meta/llama-3-8b-instruct` → 410 deprecated
- ❌ `@cf/google/gemma-3-12b-it` → 403 not allowed

#### 5. R2 buckets via Cloudflare API — 403
```
GET /accounts/2994d6fc.../r2/buckets
→ 403 {"success":false,"errors":[{"code":10000,"message":"Authentication error","documentation_url":"https://developers.cloudflare.com/api/resources/r2"}]}

POST /accounts/2994d6fc.../r2/buckets {"name":"ai-brain-workspace"}
→ 403 Authentication error
```
Token sem permissão R2 — precisa criar bucket manualmente via dashboard

#### 6. AI Gateway — 401/403
```
GET /accounts/2994d6fc.../ai-gateway/gateways → 403 Authentication error
POST /accounts/2994d6fc.../ai-gateway/gateways {"id":"ai-brain-god"} → 403
POST https://gateway.ai.cloudflare.com/v1/2994d6fc.../ai-brain-god/compat/chat/completions → 401 Unauthorized
```
Token sem permissão AI Gateway — precisa criar gateway manualmente via dashboard

#### 7. R2 S3 via boto3 — SSL handshake failure ❌ (ambiente, não token)
```
boto3.client('s3', endpoint_url='https://2994d6fc57ed22ae8ad47c3525cc3dae.r2.cloudflarestorage.com',
             aws_access_key_id='515775cd... (R2 key)',
             aws_secret_access_key='e05a62e... (R2 secret)')

Sandbox E2B Python 3.13:
→ SSLError SSLV3_ALERT_HANDSHAKE_FAILURE _ssl.c:1032

Produção Render Python 3.11.0 OpenSSL 3.0.20 7 Apr 2026:
→ SSLError SSLV3_ALERT_HANDSHAKE_FAILURE _ssl.c:992

TLS test em produção:
- https://2994d6fc57ed22ae8ad47c3525cc3dae.r2.cloudflarestorage.com/ → FAIL SSLV3_ALERT_HANDSHAKE_FAILURE
- https://r2.cloudflarestorage.com/ → FAIL CERTIFICATE_VERIFY_FAILED certificate has expired
- https://cloudflare.com/ → OK 301
- https://api.cloudflare.com/ → OK 301
- https://www.google.com/ → OK 200
- R2 with verify=False → FAIL SSLV3_ALERT_HANDSHAKE_FAILURE (mesmo sem verificar cert)

Conclusão: R2 endpoints com problema TLS — não é problema das keys, é SSL handshake entre cliente Python OpenSSL 3.0.20 e servidor R2
→ Funciona no browser (TLS stack diferente), mas não em Python boto3/httpx
→ Solução: criar bucket manualmente via dashboard https://dash.cloudflare.com/r2/overview (browser funciona)
```

## O que funciona e o que precisa ação manual

### ✅ Workers AI — FUNCIONA com novo token
- Token `cfut_... (validado)` válido até 2027-11-27
- Account ID `2994d6fc57ed22ae8ad47c3525cc3dae`
- Modelos working: `@cf/meta/llama-3.3-70b-instruct-fp8-fast` + `@cf/openai/gpt-oss-120b`
- Código atualizado em `app/models/llm.py` default agora `llama-3.3-70b-fp8-fast` (não deprecated)
- Teste em produção via `POST /cloudflare/test {"token":"cfut_...","account_id":"2994d6fc..."}` → `{"valid":true,"workers_ai_test":{"ok":true,"result":"1 + 1 = 2."}}` ✅

**Para ativar em produção Render:**
1. Vai a https://dashboard.render.com → serviço `APP_Teste` → Environment
2. Adiciona:
```
CLOUDFLARE_API_TOKEN = cfut_... (validado)
CLOUDFLARE_ACCOUNT_ID = 2994d6fc57ed22ae8ad47c3525cc3dae
CLOUDFLARE_MODEL = @cf/meta/llama-3.3-70b-instruct-fp8-fast
```
3. Save → redeploy 2-3min
4. Testa:
```bash
curl https://app-teste-x6od.onrender.com/system/status | jq .llm
# Deve mostrar "cloudflare" em providers

curl -X POST https://app-teste-x6od.onrender.com/cloudflare/ai/chat -H "Content-Type: application/json" -d '{"message":"Olá"}'
# Deve retornar resposta Llama 3.3 70B
```

### ❌ R2 — precisa criar bucket manualmente via dashboard (SSL fail em Python)
- R2 S3 keys `515775cd... + e05a62e...` não testáveis via boto3 por SSL handshake failure tanto sandbox quanto produção
- Cloudflare API para R2 retorna 403 (token sem perm R2)
- **Solução:** criar bucket manualmente:
  1. Vai a https://dash.cloudflare.com/2994d6fc57ed22ae8ad47c3525cc3dae/r2/overview
  2. Create bucket → Name: `ai-brain-workspace` → Create
  3. Depois, para usar via S3, precisa de R2 API Token com Object Read & Write:
     - https://dash.cloudflare.com/2994d6fc57ed22ae8ad47c3525cc3dae/r2/api-tokens → Create API Token → Name `ai-brain-r2` → Permissions Object Read & Write → Bucket `ai-brain-workspace` → Create → copia Access Key + Secret
  4. Adiciona em Render env vars:
```
R2_ACCOUNT_ID = 2994d6fc57ed22ae8ad47c3525cc3dae
R2_ACCESS_KEY_ID = <novo ou 515775cd...>
R2_SECRET_ACCESS_KEY = <novo ou e05a62e...>
R2_BUCKET = ai-brain-workspace
```

### ❌ AI Gateway — precisa criar manualmente
- Token sem permissão Gateway (403)
- Criar manualmente: https://dash.cloudflare.com/2994d6fc57ed22ae8ad47c3525cc3dae/ai/ai-gateway → Create Gateway → ID `ai-brain-god`
- Depois adiciona `CLOUDFLARE_GATEWAY_ID=ai-brain-god` em Render env vars

## Endpoints novos criados para debug

- `POST /cloudflare/test` com `{"token":"...","account_id":"...","gateway_id":"..."}` → testa token sem precisar env vars
- `POST /cloudflare/r2/setup` com `{"account_id","access_key_id","secret_access_key","bucket"}` → tenta criar bucket via boto3 em produção (atualmente falha SSL, mas útil para debug)
- `GET /cloudflare/r2/tls-test` → testa TLS handshake para 5 endpoints, retorna OpenSSL version + Python version + status

## Código atualizado e pushed

- `app/models/llm.py` → default model `llama-3.3-70b-fp8-fast` (não deprecated), models_to_try prioriza working models
- `app/tools/cloudflare_deploy.py` → teste usa `llama-3.3-70b-fp8-fast` não `llama-3-8b`
- `app/api/cloudflare.py` → aceita token+account_id+gateway_id via body + endpoints R2 setup + TLS test
- Deploy `88102f2` LIVE em https://app-teste-x6od.onrender.com/health

## Próximos passos

1. **Ativar Workers AI em produção:** setar `CLOUDFLARE_API_TOKEN=cfut_... + CLOUDFLARE_ACCOUNT_ID=2994d6fc...` em Render dashboard → redeploy → testar `/system/status` → deve aparecer `cloudflare` em providers
2. **Criar R2 bucket manualmente via dashboard:** https://dash.cloudflare.com/2994d6fc.../r2/overview → Create `ai-brain-workspace` → depois setar R2 env vars em Render
3. **Criar AI Gateway manualmente:** https://dash.cloudflare.com/2994d6fc.../ai/ai-gateway → Create `ai-brain-god` → setar `CLOUDFLARE_GATEWAY_ID` em Render
4. **Testar tudo:**
```bash
curl https://app-teste-x6od.onrender.com/cloudflare/test
curl -X POST https://app-teste-x6od.onrender.com/cloudflare/test -H "Content-Type: application/json" -d '{"token":"cfut_...","account_id":"2994d6fc..."}'
curl https://app-teste-x6od.onrender.com/cloudflare/ai/models
curl -X POST https://app-teste-x6od.onrender.com/cloudflare/ai/chat -d '{"message":"Olá"}'
curl https://app-teste-x6od.onrender.com/cloudflare/r2/status
curl https://app-teste-x6od.onrender.com/cloudflare/r2/tls-test
```

Links:
- Dashboard: https://dash.cloudflare.com/2994d6fc57ed22ae8ad47c3525cc3dae
- API Tokens: https://dash.cloudflare.com/profile/api-tokens
- AI Gateway: https://dash.cloudflare.com/2994d6fc57ed22ae8ad47c3525cc3dae/ai/ai-gateway
- R2: https://dash.cloudflare.com/2994d6fc57ed22ae8ad47c3525cc3dae/r2/overview
- R2 API Tokens: https://dash.cloudflare.com/2994d6fc57ed22ae8ad47c3525cc3dae/r2/api-tokens
- Workers AI models: https://developers.cloudflare.com/workers-ai/models/
- App live: https://app-teste-x6od.onrender.com/health
- Cloudflare test: https://app-teste-x6od.onrender.com/cloudflare/test
