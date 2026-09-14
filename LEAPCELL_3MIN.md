# Leapcell Deploy — 3 minutos — Free Forever sem cartão

**Porquê Leapcell?**
- Free forever sem cartão (vs HF Spaces Docker agora exige PRO 402)
- 20 projetos free, 3 vCPU 4GB RAM por projeto (vs Render 512MB) → Browser Agent funciona
- 2GB transfer/mês free, 60 build min/mês, Docker support
- Sleep maior que 15min Render
- Suporta Playwright

## Deploy em 3 minutos (sem cartão, sem token)

1. **Cria conta:** https://leapcell.io → Sign up com GitHub (sem cartão) — 30s
2. **New Project → Import from GitHub:** `rpolicarpo100/APP_Teste` — 30s
3. **Build config:**
   - Build Type: Dockerfile
   - Dockerfile Path: `Dockerfile.leapcell`
   - Port: 8000
   - Health Check: `/health`
4. **Env vars (copia do Render):**
   - `DATABASE_URL` = Neon Postgres URI (já tens, 0.5GB permanente free)
   - `GROQ_API_KEY` = gsk_t9cQt1... (free 14.4k/dia, já tens)
   - `GROQ_MODEL` = groq/compound-mini
   - `GEMINI_API_KEY` = AQ.Ab8RN6I... (free 60/min, já tens)
   - `GEMINI_MODEL` = gemini-flash-latest
   - `OPENROUTER_API_KEY` = sk-or-v1-7... (free)
   - `OPENROUTER_MODEL` = nvidia/nemotron-3.5-lightning:free
   - `HF_TOKEN` = hf_WkTfIKPB... (opcional, credits depleted)
   - `SERPER_API_KEY` = 6d443b41fa... (search)
   - `ASSEMBLYAI_API_KEY` = 50778e480f... (transcription)
5. **Deploy** → URL: `https://ai-brain-god.leapcell.dev` (exemplo) — 2min build

**Total: 3min**

## Vantagens vs Render
- 4GB RAM vs 512MB → Playwright Browser Agent funciona
- 3 vCPU vs 0.1 vCPU
- Sleep maior vs 15min
- Free forever sem cartão (Render pede cartão para disk)

## Vantagens vs HF Spaces
- HF Spaces Docker agora exige PRO (402 Payment Required) — Leapcell é free forever real sem cartão

**Sem YouTube API** — conforme pedido, não usamos YouTube Data API, apenas HTML estático gamer épico com embed e placeholders
**Tavily eliminado** — TAVILY_API_KEY deletada do Render (era mesma que SERPER, 401 Unauthorized)
