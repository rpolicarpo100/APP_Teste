# Deploy — GitHub rpolicarpo100/APP_Teste + Fly.io

## ✅ Estado atual

- **Repo local:** git init feito, 2 commits, 96 files, branch main pronto
- **Docker:** Dockerfile + docker-compose.yml + testado ✅ (8 agentes 21 tools)
- **Fly.io:** fly.toml pronto (app ai-brain-god, região mad, volume ai_brain_data)
- **GitHub Actions:** .github/workflows/fly-deploy.yml (auto deploy a cada push)
- **Chave SSH deploy:** gerada em `deploy/keys/`

### Teste local OK:
```
./scripts/test_deploy.sh http://localhost:8000
→ 9 endpoints ✅
→ Agentes 8 ✅ Tools 21 ✅ External 4/4 ✅
```

## 🔑 Chaves geradas para rpolicarpo100

### 1. SSH Deploy Key (GitHub)

**Pública — adiciona em GitHub:**

Vai a https://github.com/rpolicarpo100/APP_Teste/settings/keys → New deploy key

- Title: `ai-brain-deploy`
- Key:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILdrfjEZGo/w2M8fOpz4ZKJM0Hb1YSEoIIaQ6NYJnWx6 rpolicarpo100@ai-brain-deploy
```
- ✅ Allow write access

**Privada — guardada local (não commitar):**
```
```
Ficheiro: `deploy/keys/github_deploy_key` (chmod 600)

Para usar:
```bash
eval $(ssh-agent)
ssh-add deploy/keys/github_deploy_key
git remote add origin git@github.com:rpolicarpo100/APP_Teste.git
git push -u origin main
```

### 2. GitHub PAT (mais fácil que SSH)

Se preferir HTTPS:

1. https://github.com/settings/tokens/new
   - Note: `APP_Teste deploy`
   - Expiration: 90 days
   - Scopes: ✅ repo
2. Generate → copia `ghp_...`

Push:
```bash
export GITHUB_TOKEN=ghp_xxx
./scripts/push_github.sh
# ou
git remote add origin https://ghp_xxx@github.com/rpolicarpo100/APP_Teste.git
git push -u origin main
```

## 🚀 Fly.io — Token que enviaste está inválido

O token que colaste:
```
FlyV1 fm2_lJPEC... , fm2_lJPEThQ...
```
Está truncado / expirado → erro `missing third-party discharge token` + 401.

### Como gerar novo token válido:

**Opção A — Dashboard (mais fácil):**
1. Vai a https://fly.io/dashboard
2. Tokens → Create token → **Deploy token** → escolhe app `ai-brain-god` ou cria
3. Copia token que começa com `FlyV1 fm2_...` COMPLETO (tem 2 partes separadas por vírgula, não cortes)

**Opção B — CLI:**
```bash
flyctl auth login
flyctl tokens create deploy -x 999h --app ai-brain-god
# copia token completo
```

Depois:

**Deploy manual:**
```bash
export FLY_API_TOKEN="FlyV1 fm2_...."
./scripts/deploy_fly.sh
# ou
flyctl deploy --remote-only
```

**Deploy automático via GitHub:**
1. Copia FLY_API_TOKEN
2. Vai a https://github.com/rpolicarpo100/APP_Teste/settings/secrets/actions
3. New repository secret → Name: `FLY_API_TOKEN` → Value: cola token completo
4. Faz push → GitHub Actions corre `fly-deploy.yml` → deploy auto

## 📦 Push imediato (quando tiveres token)

```bash
cd ai-brain
export GITHUB_TOKEN=ghp_seu_token_aqui
./scripts/push_github.sh

# Verifica em https://github.com/rpolicarpo100/APP_Teste
```

## 🌐 URLs após deploy

- Fly.io: https://ai-brain-god.fly.dev/dashboard/
- Health: https://ai-brain-god.fly.dev/health
- Network: https://ai-brain-god.fly.dev/system/network
- Docs: https://ai-brain-god.fly.dev/docs

## 🧪 Teste deploy Fly

```bash
./scripts/test_deploy.sh https://ai-brain-god.fly.dev
```

## 📁 Ficheiros prontos

- `Dockerfile` ✅
- `docker-compose.yml` ✅
- `fly.toml` (app ai-brain-god, mad) ✅
- `render.yaml` ✅
- `.github/workflows/fly-deploy.yml` ✅
- `.github/workflows/ci.yml` ✅
- `scripts/push_github.sh` ✅
- `scripts/deploy_fly.sh` ✅
- `scripts/test_deploy.sh` ✅
- `deploy/keys/` com chave SSH ✅

## ⚠️ Segurança

- NUNCA commitar `deploy/keys/github_deploy_key` (privada) — já está no .gitignore
- Troca token Fly após uso se exposto
- Em produção muda SECRET_KEY em fly.toml env
