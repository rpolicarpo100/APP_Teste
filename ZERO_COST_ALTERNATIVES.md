# Alternativas Viáveis e Funcionais a Custo 0 — Persistência sem Cartão

> Render free web services têm filesystem efêmero — SQLite em `data/brain.db` é apagado a cada deploy/restart/spin-down (15 min idle). Disk persistente exige cartão (erro: "Payment information is required"). Abaixo 5 alternativas **100% grátis, sem cartão, funcionais**.

## Resumo Rápido

| Alternativa | Engine | Storage Grátis | Cartão? | Expira? | Ideal para |
|---|---|---|---|---|---|
| **Render Postgres Free** | Postgres | 1 GB | Não | 30 dias | Demo rápida, mesmo dashboard |
| **Neon** | Postgres serverless | 0.5 GB × 100 projetos, 100 CU-h/mês | Não | Nunca (permanente) | **Recomendado** — melhor para app |
| **Supabase** | Postgres | 500 MB × 2 projetos | Não | Nunca, pausa após 1 semana idle | Full backend (auth, storage) |
| **Turso** | SQLite/libSQL edge | 5 GB, 500M rows read/mês | Não | Nunca | **Drop-in SQLite** — migração mínima |
| **Upstash Redis** | Redis | 256 MB, 500K cmds/mês | Não | Nunca | Cache, sessions, ranking |

## 1. Render Postgres Free (custo 0, dentro do Render)

**Como criar (sem código):**
1. Dashboard → New → Postgres → Name: `ai-brain-db` → Plan: Free → Create
2. Copia Internal Connection String: `postgres://...`
3. No serviço `APP_Teste` → Environment → Add `DATABASE_URL` = string copiada
4. Deploy → app usa Postgres automaticamente (já suporta via `psycopg2-binary`)

**Prós:** Zero config, vive ao lado do serviço, sem cartão
**Contras:** Expira 30 dias após criação, precisa recriar

## 2. Neon — Recomendado (custo 0, permanente, sem cartão)

**Free tier:** 0.5 GB por projeto, até 100 projetos, 100 CU-hours/mês, scale to zero, branching, sem cartão, comercial OK.

**Como criar:**
1. Vai a https://neon.tech → Sign up (só email)
2. New Project → Region: AWS eu-central-1 (Frankfurt perto de Lisboa)
3. Copia Connection String: `postgresql://user:pass@ep-xxx.eu-central-1.aws.neon.tech/neondb?sslmode=require`
4. Render → APP_Teste → Environment → `DATABASE_URL` = string
5. Deploy → `app/database/connection.py` detecta `neon` e usa Postgres

**Código já pronto:** `connection.py` faz `postgres://` → `postgresql://` e `pool_pre_ping=True`

**Teste local:**
```bash
export DATABASE_URL="postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require"
python -m app.main
# /tools/health deve dar 29 OK com Postgres
```

## 3. Supabase (custo 0, 500MB, sem cartão)

**Free tier:** 500 MB × 2 projetos, unlimited API, pausa após 1 semana idle (acorda no request).

**Como criar:**
1. https://supabase.com → Sign up
2. New Project → Region EU
3. Settings → Database → Connection String → URI
4. Render → `DATABASE_URL` = URI
5. Deploy

**Prós:** Inclui Auth, Storage, Realtime
**Contras:** Pausa após 1 semana sem uso (primeiro request demora)

## 4. Turso — Drop-in SQLite (custo 0, 5GB, sem cartão)

**Free tier:** 5 GB total, 100 databases, 500M rows read/mês, 10M writes/mês, 1 dia PITR, sem cartão.

**Ideal porque:** Nosso app já usa SQLite — Turso é SQLite na edge, migração mínima.

**Como criar:**
1. https://turso.tech → Sign up
2. `turso db create ai-brain --location ams` (Amsterdam perto)
3. `turso db show ai-brain --url` → `libsql://ai-brain-xxx.turso.io`
4. `turso db tokens create ai-brain` → token
5. Render → `DATABASE_URL` = `libsql://ai-brain-xxx.turso.io?authToken=TOKEN`
6. Código: `connection.py` já detecta `libsql://` e tenta `sqlite+libsql://` (precisa `pip install sqlalchemy-libsql` — opcional, se falhar cai para SQLite)

**Alternativa simples sem driver:** Usar Turso via HTTP API direto nos tools, mantendo SQLite local como cache.

## 5. Upstash Redis (cache, custo 0)

**Free tier:** 256 MB, 500K comandos/mês, 1 DB, sem cartão.

**Uso:** Para `tool_rankings` e cache de ranking, não para dados principais. Pode complementar Postgres.

## Implementação Atual no Código

`app/database/connection.py` já suporta:

```python
db_url = os.getenv('DATABASE_URL') or settings.database_url
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://','postgresql://',1)
if db_url.startswith('libsql://'):
    # Turso
elif db_url.startswith('sqlite'):
    # SQLite local (efêmero no Render free sem disk)
else:
    # Postgres (Neon, Supabase, Render Postgres)
```

- `requirements.render.txt` agora inclui `psycopg2-binary==2.9.9` para Postgres
- `get_db_type()` retorna `sqlite|neon|supabase|render_postgres|postgres|turso` para debug em `/system/status`

## Recomendação Final Custo 0

**Para produção imediata sem cartão e sem expiração:** **Neon**

- Criar conta Neon (30 seg, só email)
- Copiar `DATABASE_URL`
- Adicionar no Render → Environment → Save → Manual Deploy
- Pronto — dados persistem, 0 custo, sem cartão, permanente

**Para manter 100% Render sem serviço externo:** **Render Postgres Free** — cria DB free no mesmo dashboard, expira 30 dias mas é 0 custo e sem cartão, basta recriar mensalmente.

**Para manter SQLite sem mudar nada:** **Turso** — 5GB free, sem cartão, drop-in.

## Teste em Produção

Após setar `DATABASE_URL`:

```bash
curl https://app-teste-x6od.onrender.com/ | jq .agents
# deve dar 10 agentes

curl https://app-teste-x6od.onrender.com/tools/health | jq .stats
# total 29 ok 29

curl https://app-teste-x6od.onrender.com/tools/ranking | jq '.rankings | length'
# 29

curl https://app-teste-x6od.onrender.com/system/status | jq .database
# deve mostrar tipo: neon/supabase/render_postgres
```

## Status Atual

- Serviço live: `https://app-teste-x6od.onrender.com` — 10 agentes, 29 tools OK, sem disk (efêmero)
- Código pronto para qualquer `DATABASE_URL` — basta setar env var no Render
- Sem custo, sem cartão, funcional
