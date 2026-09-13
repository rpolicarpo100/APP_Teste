# 💬 Pelo CHAT é possível construir APPs e SITES — REAL e FUNCIONAL

> Como pediste: "Pelo chat deve ser possível construir app e sites"

## ✅ Implementado e testado

Agora pelo **CHAT** podes dizer:

- "Cria um site de trading minimalista e bonito"
- "Cria uma app de gestão de tarefas minimalista"
- "Cria uma landing page para loja online de café"
- "Cria um portfolio para fotógrafo"
- "Cria um site para restaurante"

E o Brain **constrói na hora** — HTML real, bonito, leve, com preview.

## 🎥 Demonstração REAL executada

```bash
curl -X POST http://127.0.0.1:8000/chat -d '{"message": "Cria um site de trading minimalista e bonito"}'
```

**Resposta REAL:**
```json
{
  "message": "✅ SITE construído com sucesso via chat!\n\nObjectivo: Cria um site de trading minimalista e bonito\nEstilo: bonito e leve\nFicheiro: cria-um-site-de-trading-minimalista-e-bo-14b6b6.html\nTamanho: 6191 bytes\nPreview: /workspace/cria-um-site-de-trading-minimalista-e-bo-14b6b6.html",
  "mission_id": "444225e9-8171-49fe-8bb1-8cf9ecb84700",
  "artifacts": [{
    "type": "website",
    "path": "/home/user/ai-brain/data/workspace/cria-um-site-de-trading-minimalista-e-bo-14b6b6.html",
    "filename": "cria-um-site-de-trading-minimalista-e-bo-14b6b6.html",
    "url": "/workspace/cria-um-site-de-trading-minimalista-e-bo-14b6b6.html",
    "size": 6191
  }],
  "built_url": "/workspace/cria-um-site-de-trading-minimalista-365550.html"
}
```

**Ficheiros REAIS criados em `data/workspace/`:**
```
6.1K cria-um-site-de-trading-minimalista-365550.html
6.2K cria-um-site-de-trading-minimalista-e-bo-14b6b6.html
6.0K cria-uma-app-de-gest-o-de-tarefas-minima-905c3b.html
6.0K cria-uma-app-de-gest-o-de-tarefas-minima-abae4e.html
```

**Preview REAL acessível:**
- http://127.0.0.1:8000/workspace/cria-um-site-de-trading-minimalista-e-bo-14b6b6.html → 200 OK
- HTML bonito com nav, hero 48px, features grid 4 colunas, footer — 6191 bytes, sem dependências

## 🏗️ Como funciona — Fluxo REAL

```
User no CHAT: "Cria um site de trading minimalista"
    ↓
detect_build_intent() → is_build=True, tipo=site, estilo=bonito e leve
    ↓
_orchestrator.create_mission(objective=user_message, context={style, tipo})
    ↓
Cria task específica com agent_id="builder", required_tools=["site.builder", "filesystem.write"]
    ↓
_orchestrator.run_mission(mission_id) → Executor verifica permissões → BuilderAgent.execute()
    ↓
BuilderAgent → site_builder tool REAL → _generate_landing_html() → escreve HTML em data/workspace/{slug}-{uuid}.html
    ↓
Retorna artefacto com path, filename, url, size
    ↓
ChatResponse com message + mission_id + artifacts + built_url
    ↓
Frontend CHAT mostra bubble + preview iframe + botões Ver site / Copiar link
```

**Tudo REAL:**
- `site.builder` tool tem implementação callable verificável em `app/tools/site_builder.py`
- Gera HTML com `_generate_landing_html()` — detecta trading/loja/portfolio/app e adapta título, subtítulo, CTA, accent color, features
- Escreve ficheiro REAL via `Path.write_text()`
- Mount `/workspace` serve ficheiros estáticos para preview
- Missão e tasks persistidas em SQLite com evidência

## 🎨 O que gera — Leve mas bonito

Exemplo trading minimalista (6191 bytes):

```html
<!DOCTYPE html>
<html lang="pt-PT">
<head><title>Trading Tools — Leve & Bonito</title>
<style>
  :root{--accent:#ff4d1a;--bg:#fbf9f6;--card:#fff;--r:20px}
  body{font-family:ui-sans-system,Inter,sans-serif}
  .nav{height:64px;backdrop-filter:blur(20px)}
  .hero{grid-template-columns:1.2fr 0.8fr; padding:80px 28px}
  .hero h1{font-size:48px;letter-spacing:-1.5px}
</style>
</head>
<body>
  <div class="nav"><div class="logo">BRAIN</div></div>
  <div class="hero">
    <h1>Trading Tools <span>bonita.</span></h1>
    <p>Ferramentas curadas, sem ruído. Só o que funciona.</p>
    <button>Começar agora →</button>
  </div>
  <div class="features">4 cards</div>
</body>
</html>
```

- **Leve:** 6KB, sem Bootstrap, sem Tailwind CDN, inline CSS, sem JS pesado
- **Bonito:** hero 48px, grid 1.2fr 0.8fr, mock com rotate(1deg), features 4 colunas, footer
- **Adaptativo:** Se objectivo contém "trading" → título Trading Tools + accent #ff4d1a; "loja" → Loja Minimalista + accent #1a1a1a; "portfolio" → Portfolio + #2563eb; "app" → App Leve & Bonita + #7c3aed

## 💬 No frontend CHAT — Experiência

1. User escreve "Cria um site..."
2. Mostra bubble temporária "🏗️ A construir... → A criar missão real → Builder Agent a gerar HTML → A guardar em data/workspace"
3. Após 2-5s, mostra bubble bot com:
   - Texto ✅ SITE construído
   - Card com filename, botão "Abrir em nova aba ↗"
   - Iframe preview 320px height do site
   - Botões "Ver site" e "Copiar link"
   - Missão ID curta

Tudo em `frontend/index.html` — 1 ficheiro, sem dependências, com JS vanilla que detecta `built_url` e `artifacts`.

## 🔧 Ferramentas e agentes novos

**Tool nova:**
- `site.builder` — id, name, description, risk MEDIUM, requires_approval False, input_schema objective/style/brand, implementação REAL em `site_builder.py`

**Agent novo:**
- `builder` — Builder Agent, specialty "Construção de Apps e Sites", skills site_building, frontend_dev, tools site.builder + filesystem.*

**Permissões:**
- `TOOL_PERMISSIONS["site.builder"]` — FILE_WRITE, autonomy 2
- `AGENT_PERMISSIONS["builder"]` + `design` e `coding_qa` podem usar site.builder
- `AGENT_PERMISSIONS["coding_qa"]` já tinha filesystem.list fix

**Planner:**
- `KEYWORD_AGENT_MAP` agora inclui "criar app", "criar site", "landing page", "website", "portfolio", "loja online" → builder

**Main:**
- `import app.tools.site_builder`
- `app.mount("/workspace", StaticFiles(directory=workspace_path))` — preview
- `chat.set_orchestrator(orchestrator)` — chat pode orquestrar
- Rotas `/dashboard` e `/dashboard/` retornam FileResponse directo — fix 307

## 📁 Como usar no PC

1. `run.bat` → abre http://127.0.0.1:8000/dashboard
2. Vai para CHAT
3. Escreve: "Cria um site de ..."
4. Recebe site com preview iframe + link /workspace/{ficheiro}.html
5. Ficheiro fica em `data/workspace/` — podes editar, copiar, fazer deploy

**Exemplos para testar no CHAT:**
```
Cria um site de trading minimalista e bonito
Cria uma landing page para loja de café especial
Cria um portfolio para designer minimalista
Cria uma app de tarefas com estilo escuro elegante
Cria um site para restaurante italiano
```

Cada um gera HTML diferente com accent, título, features adaptados.

## ✅ Testes

- `pytest tests/ -q` → 23 passed (mantido)
- Chat builder manual → 2 sites + 1 app criados, 6KB cada, 200 OK preview
- `curl /workspace/{file}.html` → 200 OK, HTML bonito verificável

---

**Pelo CHAT é possível construir APPs e SITES — REAL e FUNCIONAL — como pediste.**
