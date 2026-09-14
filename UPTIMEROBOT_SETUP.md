# UptimeRobot Setup — 2min — Evita spin down Render 15min

**Render free dorme após 15min sem tráfego → cold start 30-60s**

**Solução 1: GitHub Actions (FEITO, custo 0, sem cartão, sem conta extra)**
- `.github/workflows/keep-alive.yml` já criado
- Ping a cada 5min para /health, /system/status, /tools/health, /memory, /businesses
- Mantém Render acordado + Neon ativo
- Funciona automaticamente após push para main

**Solução 2: UptimeRobot free (alternativa, 2min)**
1. Cria conta em https://uptimerobot.com free sem cartão
2. Dashboard → Add New Monitor → HTTP(s)
3. Friendly Name: `BRAIN GOD Render`
4. URL: `https://app-teste-x6od.onrender.com/health`
5. Monitoring Interval: 5 minutes
6. Create Monitor
7. Adiciona mais 2 monitores:
   - `https://app-teste-x6od.onrender.com/system/status`
   - `https://app-teste-x6od.onrender.com/tools/health`

**Solução 3: cron-job.org free (sem conta GitHub)**
1. https://cron-job.org free sem cartão
2. Create cronjob → URL https://app-teste-x6od.onrender.com/health → every 5min

**Resultado:** Render nunca dorme, sem cold start, Neon sempre ativo, custo 0.

**Teste:** Após 20min sem tráfego, chama https://app-teste-x6od.onrender.com/health — deve responder <1s (não 30-60s cold start)
