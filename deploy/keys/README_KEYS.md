# Chaves Deploy — GitHub rpolicarpo100/APP_Teste

## 1. Deploy Key SSH (para push via SSH)

Publica (adicionar em GitHub → Settings → Deploy keys → Add deploy key → Allow write access):

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILdrfjEZGo/w2M8fOpz4ZKJM0Hb1YSEoIIaQ6NYJnWx6 rpolicarpo100@ai-brain-deploy
```

Privada em `github_deploy_key` — guarda em local seguro, não commitar.

Para usar:
```bash
eval $(ssh-agent)
ssh-add deploy/keys/github_deploy_key
git remote add origin git@github.com:rpolicarpo100/APP_Teste.git
git push -u origin master:main
```

## 2. PAT (Personal Access Token) — mais fácil

1. Vai a https://github.com/settings/tokens/new
2. Cria token classic com scope `repo`
3. Copia token

Push via HTTPS:
```bash
git remote add origin https://<TOKEN>@github.com/rpolicarpo100/APP_Teste.git
git push -u origin master:main
```

Ou usa env:
```bash
export GITHUB_TOKEN=ghp_xxx
./scripts/push_github.sh
```

## 3. Fly.io Token

1. https://fly.io/dashboard → Tokens → Create token
2. Copia `FLY_API_TOKEN`
3. Adiciona em GitHub → APP_Teste → Settings → Secrets → New repository secret → FLY_API_TOKEN
4. GitHub Actions vai auto-deploy a cada push
5. Ou deploy manual:
```bash
export FLY_API_TOKEN=fo1_xxx
flyctl deploy
```

