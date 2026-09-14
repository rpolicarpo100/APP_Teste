# Leapcell — Deploy Free Forever sem cartão (substituto Render + HF Spaces)

**Porquê Leapcell?**
- ✅ Free forever sem cartão
- ✅ 20 projetos free
- ✅ 3 vCPU + 4GB RAM por projeto (vs Render 0.5 vCPU 512MB)
- ✅ 2GB data transfer/mês free
- ✅ 60 build minutes/mês
- ✅ Docker support
- ✅ Não dorme 15min como Render (sleep maior)
- ✅ Suporta Playwright (4GB RAM)

**HF Spaces Docker agora exige PRO (402) — Leapcell é o substituto free forever real**

## Deploy em 3 minutos

1. Cria conta em https://leapcell.io — sem cartão
2. Dashboard → New Project → Import from GitHub → `rpolicarpo100/APP_Teste`
3. Build: Dockerfile `Dockerfile.leapcell`
4. Port: 8000
5. Health check: `/health`
6. Env vars:
   - `DATABASE_URL` = Neon Postgres URI (free 0.5GB permanente sem cartão, já tens em Render)
   - `GROQ_API_KEY` = free 14.4k req/dia em console.groq.com
   - `GEMINI_API_KEY` = free 60/min em aistudio.google.com
   - `HF_TOKEN` = `${HF_TOKEN}` (já tens, free Inference)
   - `OPENROUTER_API_KEY` = opcional free

7. Deploy → URL: `https://ai-brain-god.leapcell.app` (exemplo)

## Stack custo 0 final

- **Host:** Leapcell free (ou Render free + UptimeRobot)
- **DB:** Neon Postgres 0.5GB free permanente sem cartão (já live)
- **LLM:** 5 providers custo 0 sem cartão:
  - Ollama local
  - Groq 14.4k/dia (llama-3.1-8b-instant)
  - Gemini 60/min (gemini-1.5-flash)
  - OpenRouter free (llama-3.1-8b:free)
  - **HuggingFace Inference** (Qwen2.5-7B-Instruct) com `HF_TOKEN` — free sem cartão
- **Storage:** Supabase Storage 1GB free sem cartão
- **Vector:** Neon pgvector

## Teste local LLM com HF_TOKEN

```bash
export HF_TOKEN=${HF_TOKEN}
python -c "from app.models.llm import llm_client; print(llm_client.get_available_providers()); r=llm_client.chat([{'role':'user','content':'Olá, és o GOD?'}], 'És o GOD Cerebro Core'); print(r['content'][:500])"
```

## Vantagens vs Render

- 4GB RAM vs 512MB → Playwright funciona
- 3 vCPU vs 0.1 vCPU
- Sleep maior vs 15min
- Free forever sem cartão

## Vantagens vs HF Spaces

- HF Spaces Docker agora exige PRO (402 Payment Required) — Leapcell é free forever real sem cartão
