# BRAIN — DASHBOARD | CHAT | NEGÓCIOS | DEFINIÇÕES

> App leve mas bonita — 4 abas principais como pediste — 100% local

## 🎯 As 4 abas que pediste

### 1. DASHBOARD
- **Hero:** "Bom dia — vamos criar algo bonito?" com greeting dinâmico
- **Stats:** 4 cards — Missões, Agentes (7), Ferramentas (10), Memórias
- **Missões recentes:** lista real da API `GET /tasks` com status colorido
- **Agentes:** 5 agentes com ícone, nome, specialty, status READY com green-dot
- **Quick actions:** Research e Design — cria missão em 1 clique
- **Real:** Dados vêm de `data/brain.db` via API, não mock

### 2. CHAT
- **Chat real:** `POST /chat` com conversation_id, histórico em SQLite
- **Bubbles bonitas:** bot com avatar B preto, user com TU laranja claro, cantos 18px com 6px num lado
- **Quick buttons:** Pesquisar, Design, Negócios — preenche input
- **Fallback leve:** Sem Ollama, modo local com lógica simples, sem inventar LLM
- **Com Ollama:** Se `ollama pull qwen3:8b`, chat fica com LLM local real

### 3. NEGÓCIOS — Aba principal para ti
Ferramentas reais, sem invenção de métricas:

**💰 Calculadora de Margem REAL:**
- Inputs: Custo e Preço venda
- Cálculo: `(preço-custo)/preço*100` + lucro + markup
- KPIs: 3 cards com margem, lucro, markup
- Result box com fórmula transparente + [VERIFICADO] vs [ESTIMATIVA] vs [NÃO VERIFICADO]
- Guarda em memória `POST /memory` tipo long

**📊 Modelo de Negócio:**
- Form: Ideia, Proposta valor, Segmento, Canal
- Cria missão real `POST /tasks` com `objective: Analisar negócio: {ideia}`
- Executa Business Agent real — retorna modelo com value_proposition, customer_segments, channels, cost_structure, kpis, risks, data_status
- Distingue factos vs estimativas, não inventa vendas/tráfego

**🔍 Análise Concorrência:**
- Textarea URLs (1 por linha) + objectivo
- Cria missão com `competitor_urls` no context
- Usa `web.fetch` REAL — evidência com status_code e length
- Não inventa concorrentes

**📈 Missões de Negócio Recentes:**
- Filtra missões com "negócio", "mercado", "concorrência"
- Lista com status colorido
- Botão actualizar

### 4. DEFINIÇÕES
- **Sistema:** `GET /system/status` JSON completo
- **Ollama:** Info + como instalar, host, modelo, modelos disponíveis
- **Segurança & Autonomia:** Níveis 0-4 explicados, RBAC, path restrictions
- **Pastas & Leveza:** Estrutura, como desinstalar (apagar pasta)
- Botões: Refresh, API Docs, Ver logs, Ver memória

## 🎨 Design — Leve mas bonita

- **Leve:** 1 HTML 35KB, 823 linhas, sem React, sem Tailwind build, sem node_modules, CSS inline, JS vanilla
- **Bonita:** 
  - Paleta quente: #fbf9f6 fundo, #ff4d1a accent, #1e1c1a texto
  - Topbar com tabs em pill `background: #f5efe8 + border-radius: 999px` — DASHBOARD | CHAT | NEGÓCIOS | DEFINIÇÕES como pediste, com dot activo
  - Cards com `border-radius: 20px` + `box-shadow: 0 1px 2px + 0 4px 16px`
  - Tipografia system font (sem Google Fonts obrigatório) — fallback para offline
  - Animações slideIn 0.25s
  - Responsive: topbar vira coluna em mobile, tabs scroll horizontal

## 🚀 Como usar no PC

**Duplo clique:**
```
run.bat → abre http://127.0.0.1:8000/dashboard
```

**Manual:**
```
python run_app.py
```

Abre automaticamente browser.

## 📁 Ficheiros

- `frontend/index.html` — 4 abas, 35KB, leve e bonita
- `run_app.py` — launcher
- `run.bat` / `run.ps1` — Windows
- `app/` — backend real
- `data/` — tudo local

## 🔍 Porque não conseguias ver antes?

Possíveis razões:
- Preview E2B às vezes bloqueia /dashboard sem trailing slash — tenta /dashboard/ com barra no fim
- Ou tenta /docs para ver API
- Ou corre local no teu PC com run.bat — funciona 100% local, sem sandbox

Nova versão tem fallback: se API falhar, mostra mensagem amigável em vez de ficar em branco.

---

Feito para DASHBOARD | CHAT | NEGÓCIOS | DEFINIÇÕES — leve mas bonita, 100% no teu PC.
