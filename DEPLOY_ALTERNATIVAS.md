# Deploy Alternativas — APP_Teste (AI Brain GOD) — sem Fly.io

Repo: https://github.com/rpolicarpo100/APP_Teste
Stack: FastAPI + SQLite + 8 agentes + 21 tools + 1 HTML frontend

## Tabela rápida

| Plataforma | Custo | Região perto PT | Docker? | Volume persistente | 1-clique | Ideal para |
|---|---|---|---|---|---|---|
| **Docker Local** | Grátis | Local | ✅ | ✅ pasta data/ | `docker-compose up` | Teste rápido |
| **GitHub Codespaces** | 60h/mês free | EU | ✅ | ❌ efémero | Botão no GitHub | Testar sem instalar |
| **Render** | Free 750h/mês | Frankfurt | ✅ | ✅ disk | ✅ render.yaml | Deploy público free |
| **Railway** | $5 free/mês | EU | ✅ | ✅ volume | `railway up` | Simples + DB |
| **Koyeb** | Free tier | Frankfurt | ✅ | ❌ (usa volume) | GitHub connect | FastAPI nativo |
| **Hugging Face Spaces** | Free | - | ✅ Docker | ❌ efémero | Dockerfile | Demo pública |
| **Replit** | Free | - | ❌ | ✅ | Import GitHub | Teste instant |
| **VPS Hetzner/DigitalOcean** | €4/mês | Falkenstein/Lisboa | ✅ | ✅ | Manual | Produção barata |
| **Coolify (self-host)** | Grátis (teu servidor) | Teu | ✅ | ✅ | GitHub | Controlo total |

---

## 1. Docker Local — já pronto ✅ (recomendado para testar melhor)

**Pros:** Mais rápido, dados persistem em `data/`, sem limites
```bash
git clone git@github.com:rpolicarpo100/APP_Teste.git
cd APP_Teste
docker-compose up --build
# Abre http://localhost:8000/dashboard/
# Teste: ./scripts/test_deploy.sh http://localhost:8000
```
Stop: `docker-compose down`

## 2. GitHub Codespaces — 0 instalação

1. Vai a https://github.com/rpolicarpo100/APP_Teste
2. Code → Codespaces → Create codespace on main
3. No terminal codespace:
```bash
pip install -r requirements.txt
python -m app.main
```
4. VSCode avisa "Port 8000 forwarded" → Open in Browser → `/dashboard/`

**Vantagem:** Testas em 2 min sem instalar nada local.

## 3. Render — melhor free tier sem Fly.io (recomendado público)

**Pros:** Frankfurt perto PT, 750h free, disk persistente, auto deploy a cada push

1. Vai a https://dashboard.render.com → New → Web Service
2. Connect GitHub → seleciona `rpolicarpo100/APP_Teste`
3. Config já vem do `render.yaml`:
   - Build: `pip install -r requirements.txt`
   - Start: `python -m app.main`
   - Health: `/health`
4. Env vars: `APP_ENV=production`, `APP_PORT=10000` (Render define PORT=10000)
5. Add Disk: Name `ai-brain-data`, Mount `/opt/render/project/src/data`, Size 1GB
6. Create → deploy → URL: `https://app-teste-xxxx.onrender.com/dashboard/`

**1-clique:** Adiciona no README:
```md
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/rpolicarpo100/APP_Teste)
```

**Teste:**
```bash
./scripts/test_deploy.sh https://app-teste-xxxx.onrender.com
```

## 4. Railway — mais simples que Render

```bash
npm i -g @railway/cli
railway login
git clone git@github.com:rpolicarpo100/APP_Teste.git
cd APP_Teste
railway init
railway up
railway domain
# → https://app-teste-production.up.railway.app/dashboard/
```

Ou via dashboard: https://railway.app/new → Deploy from GitHub → APP_Teste

**Volume:** Railway → Service → Volumes → Add Volume `/app/data`

## 5. Koyeb — FastAPI nativo, muito rápido

1. https://app.koyeb.com → Create App → GitHub → APP_Teste
2. Builder: Dockerfile
3. Port: 8000
4. Env: `APP_ENV=production`
5. Deploy → `https://app-teste-xxxxx.koyeb.app/dashboard/`

Free: 2 apps, 512MB RAM, Frankfurt.

## 6. Hugging Face Spaces — demo pública grátis (Docker)

1. https://huggingface.co/new-space → 
   - Name: `APP_Teste`
   - SDK: Docker
2. Clone space:
```bash
git clone https://huggingface.co/spaces/SEU_USER/APP_Teste
cp -r /caminho/APP_Teste/* .
git add .
git commit -m "AI Brain GOD"
git push
```
3. Space builda Dockerfile auto → URL: `https://SEU_USER-APP_Teste.hf.space/dashboard/`

**Nota:** Data efémera — para demo apenas, não guarda brain.db.

## 7. Replit — teste instantâneo

1. https://replit.com → Create Repl → Import from GitHub → `rpolicarpo100/APP_Teste`
2. Replit detecta Python → Run: `python -m app.main`
3. URL: `https://APP-Teste.replit.app/dashboard/`

## 8. VPS barato (Hetzner €4/mês — produção real)

Para negócio real com dados persistentes:

```bash
# No teu PC
ssh root@SEU_IP_VPS

# No VPS
apt update && apt install docker.io docker-compose git -y
git clone https://github.com/rpolicarpo100/APP_Teste.git
cd APP_Teste
docker-compose up -d --build
# Nginx opcional para https://teudominio.pt
```

Hetzner CX11: 1 vCPU, 2GB RAM, 20GB SSD, €4.15/mês, Falkenstein (perto PT), tráfego 20TB.

DigitalOcean Droplet similar €6/mês com região Frankfurt.

## 9. Coolify — self-hosted tipo Vercel no teu VPS

Se tens VPS, instala Coolify (alternativa open-source a Vercel/Netlify):

```bash
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
# Abre http://SEU_IP:8000 → conecta GitHub → deploy APP_Teste auto
```

## 10. Local sem Docker (mais leve)

```bash
git clone git@github.com:rpolicarpo100/APP_Teste.git
cd APP_Teste
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
# http://localhost:8000/dashboard/
```

---

## Qual escolher para testar melhor?

**Para ti agora (sem Fly.io):**

- **Teste rápido 2 min:** GitHub Codespaces (sem instalar nada)
- **Teste local sério:** `docker-compose up --build` (recomendado, dados persistem)
- **Deploy público free para partilhar:** **Render** (Frankfurt, disk persistente, 750h free) → melhor alternativa ao Fly.io
- **Deploy mais simples:** Railway
- **Demo pública:** Hugging Face Spaces

**Minha recomendação:** 
1. Usa Docker local para desenvolver
2. Faz deploy Render para URL pública partilhável (grátis, sem cartão para começar)
3. Quando crescer, VPS Hetzner €4/mês

---

## Scripts prontos no repo

- `scripts/deploy_local.sh` — venv + run
- `scripts/deploy_docker.sh` — build + run Docker
- `scripts/test_deploy.sh <URL>` — testa 9 endpoints, verifica 8 agentes + 21 tools
- `docker-compose.yml` — já com volume data/
- `render.yaml` — já para Render 1-clique
- `Dockerfile` — multi-stage leve

Todos testados: `./scripts/test_deploy.sh http://localhost:8000` → 9/9 ✅

---

## Próximos passos

1. Escolhe plataforma acima
2. Diz qual queres e eu gero comando 1-clique
3. Ou faz push novo e GitHub Actions CI já testa

Repo já em: https://github.com/rpolicarpo100/APP_Teste
