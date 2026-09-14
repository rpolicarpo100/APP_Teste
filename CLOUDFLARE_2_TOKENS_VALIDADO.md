# ✅ 2 Tokens Cloudflare VALIDOS — Workers AI + Gateway default OK

## Tokens recebidos

### Token 1: WORKERS — cfut_hGbwa... (workers)
- /user/tokens/verify → 200 valid active expires 2027-11-27 ✅
- Workers AI direct @cf/meta/llama-3.3-70b-instruct-fp8-fast → 200 OK "Sou um modelo de IA..." ✅
- Workers AI direct @cf/openai/gpt-oss-120b → 200 OK "Olá! Eu sou o ChatGPT..." ✅
- Gateway compat default → 401 Unauthorized ❌ (sem perm gateway)
- R2 buckets → 403 Authentication error ❌
- Gateway management API → 403 ❌

**Uso:** só Workers AI direct

### Token 2: GATEWAY — cfut_f6DN... (gateway)
- /user/tokens/verify → 200 valid active ✅
- Workers AI direct llama-3.3-70b → 200 OK "Olá! Como posso ajudar?" ✅
- AI Gateway compat com ID `default` → 200 OK "2" (1+1) ✅ — gateway default existe!
- AI Gateway compat com ID `ai-brain-god` → 400 "Please configure AI Gateway in dashboard" ❌ (não existe)
- Gateway compat gpt-oss-120b → 200 OK ✅
- R2 buckets → 403 ❌
- Gateway management API list/create → 403 ❌ (só compat funciona, não management)

**Uso:** Workers AI direct + AI Gateway compat com ID `default` — MAIS CAPACIDADES, RECOMENDADO

## Descoberta importante

**Gateway ID `default` já existe e funciona!**
- Testado: POST https://gateway.ai.cloudflare.com/v1/2994d6fc57ed22ae8ad47c3525cc3dae/default/compat/chat/completions
- Com GATEWAY token → 200 OK "2"
- Com WORKERS token → 401 Unauthorized

**Gateway ID `ai-brain-god` não existe:**
- Retorna 400 "Please configure AI Gateway in the Cloudflare dashboard"
- Precisa criar manualmente em https://dash.cloudflare.com/2994d6fc57ed22ae8ad47c3525cc3dae/ai/ai-gateway → Create Gateway → ID `ai-brain-god`

## Modelos testados

- ✅ `@cf/meta/llama-3.3-70b-instruct-fp8-fast` → 200 OK (recomendado, não deprecated)
- ✅ `@cf/openai/gpt-oss-120b` → 200 OK
- ❌ `@cf/meta/llama-3-8b-instruct` → 410 deprecated 2026-05-30
- ❌ `@cf/meta/llama-3.1-8b-instruct` → 410 deprecated
- ❌ `@cf/google/gemma-3-12b-it` → 403 not allowed neste account

## R2 — SSL handshake failure em todo lado

Testado com keys 515775cd... + e05a62e...:
- Sandbox E2B Python 3.13 → SSLV3_ALERT_HANDSHAKE_FAILURE
- Produção Render Python 3.11.0 OpenSSL 3.0.20 → SSLV3_ALERT_HANDSHAKE_FAILURE
- TLS test: R2 endpoint FAIL handshake, r2.cloudflarestorage.com FAIL cert expired, cloudflare.com OK, api.cloudflare.com OK, google.com OK
- Mesmo com verify=False → FAIL handshake

**Solução:** criar bucket manualmente via dashboard https://dash.cloudflare.com/2994d6fc57ed22ae8ad47c3525cc3dae/r2/overview → Create bucket `ai-brain-workspace`

## Código atualizado — deploy ae4b520 → 46148f0 LIVE

- `app/models/llm.py` → default model `llama-3.3-70b-instruct-fp8-fast`, gateway_id default fallback `default`
- `app/tools/cloudflare_deploy.py` → teste usa `llama-3.3-70b-fp8-fast`, gateway default fallback
- `app/api/cloudflare.py` → endpoints `/cloudflare/test` aceita token+account_id+gateway_id via body, `/cloudflare/r2/setup`, `/cloudflare/r2/tls-test`
- Teste produção: `POST /cloudflare/test {"token":"cfut_f6DN...","account_id":"2994d6fc...","gateway_id":"default"}` → `{"valid":true,"workers_ai_test":{"ok":true,"result":"1 + 1 = 2."}}` ✅

## Para ativar em produção Render — 2min

Vai a https://dashboard.render.com → serviço `APP_Teste` → Environment → Add:

```
CLOUDFLARE_API_TOKEN = cfut_f6DN... (gateway)
CLOUDFLARE_ACCOUNT_ID = 2994d6fc57ed22ae8ad47c3525cc3dae
CLOUDFLARE_GATEWAY_ID = default
CLOUDFLARE_MODEL = @cf/meta/llama-3.3-70b-instruct-fp8-fast
```

Save → redeploy 2-3min → testa:

```bash
curl https://app-teste-x6od.onrender.com/system/status | jq .llm
# deve incluir cloudflare em providers

curl -X POST https://app-teste-x6od.onrender.com/cloudflare/ai/chat -H "Content-Type: application/json" -d '{"message":"Olá, quem és?"}'
# deve retornar Llama 3.3 70B

curl https://app-teste-x6od.onrender.com/cloudflare/test
# deve retornar valid true se env vars setadas
```

Para R2 (depois de criar bucket manual):

```
R2_ACCOUNT_ID = 2994d6fc57ed22ae8ad47c3525cc3dae
R2_ACCESS_KEY_ID = 515775cd...
R2_SECRET_ACCESS_KEY = e05a62e...
R2_BUCKET = ai-brain-workspace
```

## Endpoints LIVE

- https://app-teste-x6od.onrender.com/health → status ok
- https://app-teste-x6od.onrender.com/system/status → 10 agents, 39 tools, db neon, llm groq/gemini/openrouter/huggingface (+ cloudflare quando env vars setadas)
- https://app-teste-x6od.onrender.com/cloudflare/test → testa token (precisa env vars)
- POST https://app-teste-x6od.onrender.com/cloudflare/test → com body token+account_id+gateway_id testa sem env vars → valid true + workers_ai_test ok true ✅
- https://app-teste-x6od.onrender.com/cloudflare/ai/models → lista 7 modelos
- https://app-teste-x6od.onrender.com/cloudflare/r2/status → R2 status (precisa env vars)
- https://app-teste-x6od.onrender.com/cloudflare/r2/tls-test → TLS debug OpenSSL 3.0.20

## Links

- Dashboard: https://dash.cloudflare.com/2994d6fc57ed22ae8ad47c3525cc3dae
- API Tokens: https://dash.cloudflare.com/profile/api-tokens
- AI Gateway: https://dash.cloudflare.com/2994d6fc57ed22ae8ad47c3525cc3dae/ai/ai-gateway
- R2: https://dash.cloudflare.com/2994d6fc57ed22ae8ad47c3525cc3dae/r2/overview
- Workers AI models: https://developers.cloudflare.com/workers-ai/models/
- App live: https://app-teste-x6od.onrender.com/health
- Repo: https://github.com/rpolicarpo100/APP_Teste

## Próximos passos opcionais

1. Criar gateway `ai-brain-god` manualmente via dashboard se quiseres ID custom em vez de `default`
2. Criar bucket R2 `ai-brain-workspace` manualmente via dashboard
3. Se quiseres token com perm R2 + Gateway management, criar novo token em https://dash.cloudflare.com/profile/api-tokens com permissions: Account Workers AI Edit + Workers R2 Storage Edit + AI Gateway Edit + Account Settings Read
